import cv2
import os
import urllib.request
import numpy as np
from enum import IntEnum
from dataclasses import dataclass
from typing import List, Tuple, Optional

import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarkerOptions

class HandLandmark(IntEnum):
    """
    Enumeración que mapea los 21 puntos de referencia (landmarks) de la mano 
    definidos por MediaPipe. Permite el acceso por nombre descriptivo y mantiene 
    la compatibilidad de índices.
    """
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20

@dataclass
class LandmarkPoint:
    """
    Estructura de datos que representa un único punto de referencia de la mano.
    Almacena tanto la posición tridimensional normalizada provista por MediaPipe,
    como las coordenadas proyectadas a píxeles basadas en la resolución del frame.
    """
    index: int
    x: float  # Normalizado (0.0 a 1.0)
    y: float  # Normalizado (0.0 a 1.0)
    z: float  # Profundidad relativa
    pixel_x: int  # Coordenada X real en la ventana/imagen (píxeles)
    pixel_y: int  # Coordenada Y real en la ventana/imagen (píxeles)

@dataclass
class HandDetectionResult:
    """
    Contrato de datos de salida para la detección. Desacopla por completo
    el resto de los módulos del proyecto de los tipos de datos nativos de MediaPipe.
    """
    detected: bool
    landmarks: List[LandmarkPoint]
    center_normalized: Optional[Tuple[float, float]] = None
    center_pixel: Optional[Tuple[int, int]] = None


# Definición de las 21 conexiones esqueléticas de la mano para graficar
HAND_CONNECTIONS = [
    # Pulgar
    (HandLandmark.WRIST, HandLandmark.THUMB_CMC),
    (HandLandmark.THUMB_CMC, HandLandmark.THUMB_MCP),
    (HandLandmark.THUMB_MCP, HandLandmark.THUMB_IP),
    (HandLandmark.THUMB_IP, HandLandmark.THUMB_TIP),
    
    # Índice
    (HandLandmark.WRIST, HandLandmark.INDEX_FINGER_MCP),
    (HandLandmark.INDEX_FINGER_MCP, HandLandmark.INDEX_FINGER_PIP),
    (HandLandmark.INDEX_FINGER_PIP, HandLandmark.INDEX_FINGER_DIP),
    (HandLandmark.INDEX_FINGER_DIP, HandLandmark.INDEX_FINGER_TIP),
    
    # Medio
    (HandLandmark.WRIST, HandLandmark.MIDDLE_FINGER_MCP),
    (HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.MIDDLE_FINGER_PIP),
    (HandLandmark.MIDDLE_FINGER_PIP, HandLandmark.MIDDLE_FINGER_DIP),
    (HandLandmark.MIDDLE_FINGER_DIP, HandLandmark.MIDDLE_FINGER_TIP),
    
    # Anular
    (HandLandmark.WRIST, HandLandmark.RING_FINGER_MCP),
    (HandLandmark.RING_FINGER_MCP, HandLandmark.RING_FINGER_PIP),
    (HandLandmark.RING_FINGER_PIP, HandLandmark.RING_FINGER_DIP),
    (HandLandmark.RING_FINGER_DIP, HandLandmark.RING_FINGER_TIP),
    
    # Meñique
    (HandLandmark.WRIST, HandLandmark.PINKY_MCP),
    (HandLandmark.PINKY_MCP, HandLandmark.PINKY_PIP),
    (HandLandmark.PINKY_PIP, HandLandmark.PINKY_DIP),
    (HandLandmark.PINKY_DIP, HandLandmark.PINKY_TIP),
    
    # Nudillos (base de la palma)
    (HandLandmark.INDEX_FINGER_MCP, HandLandmark.MIDDLE_FINGER_MCP),
    (HandLandmark.MIDDLE_FINGER_MCP, HandLandmark.RING_FINGER_MCP),
    (HandLandmark.RING_FINGER_MCP, HandLandmark.PINKY_MCP)
]


class HandDetector:
    """
    Clase encargada de encapsular la detección de manos y landmarks mediante MediaPipe.
    Se encarga de procesar los frames y mapear los resultados a estructuras de datos limpias.
    Utiliza la API moderna de MediaPipe Tasks compatible con Python 3.13.
    """
    def __init__(self, 
                 static_image_mode: bool = False,
                 max_num_hands: int = 1,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Inicializa el detector de MediaPipe. Si el archivo del modelo 'hand_landmarker.task' 
        no existe localmente, lo descarga automáticamente de forma autocurativa.
        
        Args:
            static_image_mode (bool): Si es True, trata cada imagen como independiente.
            max_num_hands (int): Número máximo de manos a detectar. Limitado a 1 para este proyecto.
            min_detection_confidence (float): Umbral de confianza de detección.
            min_tracking_confidence (float): Umbral de confianza de tracking.
        """
        # Ruta donde se almacenará y buscará el modelo de MediaPipe
        self.model_path = "hand_landmarker.task"
        
        # Lógica autocurativa: Descargar el modelo oficial de Google si no está presente
        if not os.path.exists(self.model_path):
            package_dir = os.path.dirname(os.path.abspath(__file__))
            model_path_in_package = os.path.join(package_dir, "hand_landmarker.task")
            if os.path.exists(model_path_in_package):
                self.model_path = model_path_in_package
            else:
                print(f"Descargando modelo de landmarks ('{self.model_path}')...")
                url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
                urllib.request.urlretrieve(url, self.model_path)
                print("Descarga completada con éxito.")

        # Configuración de opciones para la API moderna de MediaPipe Tasks
        base_options = BaseOptions(model_asset_path=self.model_path)
        options = HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.hands = vision.HandLandmarker.create_from_options(options)

    def detect(self, frame: np.ndarray) -> HandDetectionResult:
        """
        Procesa un frame BGR de OpenCV, realiza la detección de landmarks de la mano,
        y devuelve un contrato de datos limpio y desacoplado de MediaPipe.
        
        Args:
            frame (np.ndarray): Imagen en formato BGR.
            
        Returns:
            HandDetectionResult: Estructura conteniendo el resultado de la detección.
        """
        if frame is None or frame.size == 0:
            return HandDetectionResult(detected=False, landmarks=[])

        try:
            h, w, _ = frame.shape
        except ValueError:
            # En caso de que el frame no tenga 3 canales o formato esperado
            return HandDetectionResult(detected=False, landmarks=[])

        # MediaPipe Tasks requiere un objeto mp.Image.
        # Primero, convertimos el frame BGR de OpenCV a RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Ejecuta la detección
        detection_result = self.hands.detect(mp_image)
        
        # Si no se detectaron manos
        if not detection_result.hand_landmarks:
            return HandDetectionResult(detected=False, landmarks=[])

        # Extraemos la primera mano detectada (limitado a max_num_hands=1)
        raw_landmarks = detection_result.hand_landmarks[0]
        
        landmarks: List[LandmarkPoint] = []
        sum_x, sum_y = 0.0, 0.0
        
        for idx, lm in enumerate(raw_landmarks):
            # MediaPipe retorna coordenadas normalizadas entre [0.0, 1.0] relativas al ancho y alto del frame
            x, y, z = lm.x, lm.y, lm.z
            
            # Convertimos las coordenadas a píxeles y nos aseguramos de no salirnos de los límites del frame (clamping)
            pixel_x = int(min(max(0, x * w), w - 1))
            pixel_y = int(min(max(0, y * h), h - 1))
            
            landmarks.append(LandmarkPoint(
                index=idx,
                x=x,
                y=y,
                z=z,
                pixel_x=pixel_x,
                pixel_y=pixel_y
            ))
            
            # Acumulamos para el cálculo del centro de gravedad de la mano
            sum_x += x
            sum_y += y

        # Calculamos el baricentro o centro geométrico promedio de los 21 puntos
        center_x_norm = sum_x / 21.0
        center_y_norm = sum_y / 21.0
        center_x_pixel = int(min(max(0, center_x_norm * w), w - 1))
        center_y_pixel = int(min(max(0, center_y_norm * h), h - 1))

        return HandDetectionResult(
            detected=True,
            landmarks=landmarks,
            center_normalized=(center_x_norm, center_y_norm),
            center_pixel=(center_x_pixel, center_y_pixel)
        )

    def draw_landmarks(self, frame: np.ndarray, result: HandDetectionResult, draw_center: bool = True) -> np.ndarray:
        """
        Dibuja los landmarks de la mano, las conexiones esqueléticas y opcionalmente el centro 
        sobre el frame provisto utilizando OpenCV.
        
        Esta visualización es puramente para depuración/retroalimentación y está separada de los datos.
        
        Args:
            frame (np.ndarray): Imagen sobre la cual se dibujará (modificación in-place).
            result (HandDetectionResult): El resultado de la detección.
            draw_center (bool): Si es True, dibuja también un círculo distintivo en el centro de la mano.
            
        Returns:
            np.ndarray: El frame modificado con los dibujos de depuración.
        """
        if not result.detected or not result.landmarks:
            return frame

        # 1. Dibujar conexiones esqueléticas
        for start_idx, end_idx in HAND_CONNECTIONS:
            # Validamos que los índices existan dentro de la lista para evitar errores de límites
            if start_idx < len(result.landmarks) and end_idx < len(result.landmarks):
                p1 = result.landmarks[start_idx]
                p2 = result.landmarks[end_idx]
                cv2.line(
                    frame, 
                    (p1.pixel_x, p1.pixel_y), 
                    (p2.pixel_x, p2.pixel_y), 
                    (0, 255, 0),  # Color verde
                    2, 
                    cv2.LINE_AA
                )

        # 2. Dibujar círculos en cada landmark
        for lm in result.landmarks:
            cv2.circle(
                frame, 
                (lm.pixel_x, lm.pixel_y), 
                5,            # Radio
                (0, 0, 255),  # Color rojo para los puntos
                -1,           # Relleno
                cv2.LINE_AA
            )

        # 3. Dibujar centro de la mano
        if draw_center and result.center_pixel is not None:
            cv2.circle(
                frame, 
                result.center_pixel, 
                8,              # Radio un poco mayor
                (255, 0, 0),    # Color azul para el centro
                -1,             # Relleno
                cv2.LINE_AA
            )
            # Agregar un borde blanco fino para mejor legibilidad estética
            cv2.circle(
                frame, 
                result.center_pixel, 
                8, 
                (255, 255, 255), 
                1, 
                cv2.LINE_AA
            )

        return frame

    def close(self):
        """
        Libera explícitamente los recursos utilizados por el procesador de MediaPipe.
        """
        if hasattr(self, 'hands') and self.hands is not None:
            self.hands.close()
