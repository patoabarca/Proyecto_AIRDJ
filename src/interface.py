"""
Módulo 9: Interfaz Visual y Feedback de AirDJ.

Este módulo es responsable únicamente de la presentación visual.
Recibe información calculada por otros módulos y la dibuja sobre el frame.

NO:
- Detecta la mano
- Reconoce gestos
- Decide estados
- Controla timers
- Ejecuta comandos multimedia

Solo dibuja lo que recibe.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, List, Any
from enum import Enum


class SystemState(str, Enum):
    """Estados posibles del sistema AirDJ (para visualización)."""
    BLOQUEADO = "BLOQUEADO"
    ACTIVANDO = "ACTIVANDO"
    ACTIVO = "ACTIVO"
    EJECUTANDO = "EJECUTANDO"
    COOLDOWN = "COOLDOWN"


@dataclass
class LandmarkPoint:
    """Punto de referencia para dibujo (compatible con hand_detector)."""
    x: float  # Normalizado 0-1
    y: float  # Normalizado 0-1
    z: float = 0.0  # Profundidad relativa


class AirDJInterface:
    """
    Renderizador de interfaz visual para AirDJ.
    
    Recibe información del sistema y la dibuja sobre un frame OpenCV.
    Completamente desacoplado de la lógica de negocio.
    """
    
    # Dimensiones y colores por defecto
    DEFAULT_FONT = cv2.FONT_HERSHEY_SIMPLEX
    DEFAULT_FONT_SCALE = 0.7
    DEFAULT_THICKNESS = 2
    DEFAULT_LINE_SPACING = 35
    
    # Paleta de colores (BGR)
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_RED = (0, 0, 255)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLUE = (255, 0, 0)
    COLOR_YELLOW = (0, 255, 255)
    COLOR_CYAN = (255, 255, 0)
    COLOR_MAGENTA = (255, 0, 255)
    COLOR_ORANGE = (0, 165, 255)
    COLOR_GRAY = (128, 128, 128)
    
    # Color por estado
    STATE_COLORS = {
        SystemState.BLOQUEADO: COLOR_RED,
        SystemState.ACTIVANDO: COLOR_YELLOW,
        SystemState.ACTIVO: COLOR_GREEN,
        SystemState.EJECUTANDO: COLOR_CYAN,
        SystemState.COOLDOWN: COLOR_ORANGE
    }
    
    def __init__(self, debug: bool = False):
        """
        Inicializa el renderizador de interfaz.
        
        Args:
            debug (bool): Si True, muestra información adicional.
        """
        self.debug = debug
        self.frame_height = 0
        self.frame_width = 0

    def render(
        self,
        frame: np.ndarray,
        state: Optional[SystemState] = None,
        activation_progress: float = 0.0,
        time_left: float = 0.0,
        volume_value: Optional[float] = None,
        detected_gesture: Optional[str] = None,
        executed_command: Optional[str] = None,
        landmarks: Optional[List[Any]] = None,
        command_zone: Optional[Tuple[float, float, float, float]] = None,
        fps: Optional[float] = None
    ) -> np.ndarray:
        """
        Renderiza la interfaz sobre el frame.
        
        Args:
            frame: Frame OpenCV sobre el cual dibujar.
            state: Estado actual del sistema.
            activation_progress: Progreso de activación [0.0, 1.0].
            time_left: Tiempo restante en segundos.
            volume_value: Valor de volumen [0, 100].
            detected_gesture: Gesto detectado (ej. "PALMA").
            executed_command: Comando ejecutado (ej. "PLAY_PAUSA").
            landmarks: Lista de puntos de referencia (opcional, para debug).
            command_zone: Geometría de la zona de comandos (x1, y1, x2, y2) en [0,1].
            fps: FPS de procesamiento (opcional).
        
        Returns:
            Frame anotado con la interfaz visual.
        """
        # Validar frame
        if frame is None or frame.size == 0:
            return frame
        
        # Crear copia para no modificar original
        output_frame = frame.copy()
        self.frame_height, self.frame_width = output_frame.shape[:2]
        
        # Sanitizar inputs
        if state is None:
            state = SystemState.BLOQUEADO
        
        activation_progress = max(0.0, min(1.0, float(activation_progress or 0.0)))
        time_left = max(0.0, float(time_left or 0.0))
        
        if volume_value is not None:
            volume_value = max(0.0, min(100.0, float(volume_value)))
        
        # Dibujar componentes en orden (de fondo a frente)
        if command_zone is not None:
            self._draw_command_zone(output_frame, command_zone)
        
        self._draw_state(output_frame, state)
        
        if state == SystemState.ACTIVANDO:
            self._draw_activation_progress(output_frame, activation_progress)
        elif state in (SystemState.ACTIVO, SystemState.EJECUTANDO):
            self._draw_timer(output_frame, time_left)
        elif state == SystemState.COOLDOWN:
            self._draw_cooldown(output_frame, time_left)
        
        if executed_command is not None:
            self._draw_command(output_frame, executed_command)
        
        if volume_value is not None:
            self._draw_volume(output_frame, volume_value)
        
        if detected_gesture is not None:
            self._draw_gesture(output_frame, detected_gesture)
        
        if self.debug:
            if landmarks is not None:
                self._draw_landmarks(output_frame, landmarks)
            if fps is not None:
                self._draw_fps(output_frame, fps)
        
        return output_frame

    def _draw_state(self, frame: np.ndarray, state: SystemState) -> None:
        """Dibuja el estado actual en la esquina superior izquierda."""
        x = 20
        y = 50
        
        state_text = f"Estado: {state.value}"
        color = self.STATE_COLORS.get(state, self.COLOR_WHITE)
        
        # Fondo semi-transparente para texto
        text_size = cv2.getTextSize(
            state_text, self.DEFAULT_FONT, self.DEFAULT_FONT_SCALE, self.DEFAULT_THICKNESS
        )[0]
        
        padding = 10
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x - padding, y - text_size[1] - padding),
            (x + text_size[0] + padding, y + padding),
            self.COLOR_BLACK,
            -1
        )
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        cv2.putText(
            frame,
            state_text,
            (x, y),
            self.DEFAULT_FONT,
            self.DEFAULT_FONT_SCALE,
            color,
            self.DEFAULT_THICKNESS,
            cv2.LINE_AA
        )

    def _draw_activation_progress(self, frame: np.ndarray, progress: float) -> None:
        """Dibuja barra de progreso de activación."""
        progress = max(0.0, min(1.0, progress))
        
        # Posición y tamaño de la barra
        bar_width = 300
        bar_height = 40
        x = (self.frame_width - bar_width) // 2
        y = self.frame_height - 100
        
        # Fondo
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), self.COLOR_GRAY, 2)
        
        # Progreso
        progress_width = int(bar_width * progress)
        cv2.rectangle(
            frame,
            (x + 2, y + 2),
            (x + progress_width - 2, y + bar_height - 2),
            self.COLOR_YELLOW,
            -1
        )
        
        # Porcentaje
        percentage_text = f"ACTIVANDO: {progress * 100:.0f}%"
        text_size = cv2.getTextSize(
            percentage_text, self.DEFAULT_FONT, 0.6, 1
        )[0]
        text_x = x + (bar_width - text_size[0]) // 2
        text_y = y + bar_height + 25
        
        cv2.putText(
            frame,
            percentage_text,
            (text_x, text_y),
            self.DEFAULT_FONT,
            0.6,
            self.COLOR_YELLOW,
            1,
            cv2.LINE_AA
        )

    def _draw_timer(self, frame: np.ndarray, time_left: float) -> None:
        """Dibuja temporizador de ventana de comandos."""
        time_left = max(0.0, time_left)
        timer_text = f"Tiempo: {time_left:.1f}s"
        
        x = 20
        y = self.frame_height - 20
        
        color = self.COLOR_GREEN if time_left > 2.0 else (self.COLOR_YELLOW if time_left > 0.5 else self.COLOR_RED)
        
        cv2.putText(
            frame,
            timer_text,
            (x, y),
            self.DEFAULT_FONT,
            0.6,
            color,
            1,
            cv2.LINE_AA
        )

    def _draw_cooldown(self, frame: np.ndarray, time_left: float) -> None:
        """Dibuja indicador de cooldown."""
        time_left = max(0.0, time_left)
        cooldown_text = f"COOLDOWN: {time_left:.1f}s"
        
        x = self.frame_width - 300
        y = self.frame_height - 20
        
        cv2.putText(
            frame,
            cooldown_text,
            (x, y),
            self.DEFAULT_FONT,
            0.6,
            self.COLOR_ORANGE,
            1,
            cv2.LINE_AA
        )

    def _draw_volume(self, frame: np.ndarray, volume_value: float) -> None:
        """Dibuja barra de volumen."""
        volume_value = max(0.0, min(100.0, volume_value))
        
        # Posición: esquina inferior derecha
        bar_width = 250
        bar_height = 30
        x = self.frame_width - bar_width - 20
        y = self.frame_height - 50
        
        # Fondo
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), self.COLOR_GRAY, 2)
        
        # Volumen
        volume_width = int(bar_width * (volume_value / 100.0))
        # Cambiar color según volumen
        if volume_value < 30:
            color = self.COLOR_GREEN
        elif volume_value < 70:
            color = self.COLOR_YELLOW
        else:
            color = self.COLOR_RED
        
        cv2.rectangle(
            frame,
            (x + 2, y + 2),
            (x + volume_width - 2, y + bar_height - 2),
            color,
            -1
        )
        
        # Texto
        volume_text = f"VOL: {volume_value:.0f}%"
        text_size = cv2.getTextSize(
            volume_text, self.DEFAULT_FONT, 0.5, 1
        )[0]
        text_x = x + (bar_width - text_size[0]) // 2
        text_y = y - 5
        
        cv2.putText(
            frame,
            volume_text,
            (text_x, text_y),
            self.DEFAULT_FONT,
            0.5,
            self.COLOR_CYAN,
            1,
            cv2.LINE_AA
        )

    def _draw_command(self, frame: np.ndarray, command: str) -> None:
        """Dibuja el comando ejecutado en el centro de la pantalla."""
        if not command:
            return
        
        command_text = f"COMANDO: {command}"
        
        text_size = cv2.getTextSize(
            command_text, self.DEFAULT_FONT, 1.0, 2
        )[0]
        
        x = (self.frame_width - text_size[0]) // 2
        y = (self.frame_height - text_size[1]) // 2
        
        # Fondo semi-transparente
        padding = 20
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x - padding, y - text_size[1] - padding),
            (x + text_size[0] + padding, y + padding),
            self.COLOR_BLACK,
            -1
        )
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Texto
        cv2.putText(
            frame,
            command_text,
            (x, y),
            self.DEFAULT_FONT,
            1.0,
            self.COLOR_CYAN,
            2,
            cv2.LINE_AA
        )

    def _draw_gesture(self, frame: np.ndarray, gesture: str) -> None:
        """Dibuja el gesto detectado."""
        if not gesture:
            return
        
        gesture_text = f"Gesto: {gesture}"
        
        x = self.frame_width - 250
        y = 50
        
        cv2.putText(
            frame,
            gesture_text,
            (x, y),
            self.DEFAULT_FONT,
            0.7,
            self.COLOR_MAGENTA,
            2,
            cv2.LINE_AA
        )

    def _draw_command_zone(self, frame: np.ndarray, zone: Tuple[float, float, float, float]) -> None:
        """Dibuja la zona de comandos si se proporciona."""
        if not zone or len(zone) != 4:
            return
        
        x1_norm, y1_norm, x2_norm, y2_norm = zone
        
        # Convertir de coordenadas normalizadas a píxeles
        x1 = int(x1_norm * self.frame_width)
        y1 = int(y1_norm * self.frame_height)
        x2 = int(x2_norm * self.frame_width)
        y2 = int(y2_norm * self.frame_height)
        
        # Dibujar rectángulo de zona
        cv2.rectangle(frame, (x1, y1), (x2, y2), self.COLOR_GREEN, 2)
        
        # Label
        cv2.putText(
            frame,
            "ZONA DE COMANDOS",
            (x1 + 5, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.COLOR_GREEN,
            1,
            cv2.LINE_AA
        )

    def _draw_landmarks(self, frame: np.ndarray, landmarks: List[Any]) -> None:
        """Dibuja landmarks de la mano en modo debug."""
        if not landmarks:
            return
        
        for landmark in landmarks:
            # Soportar diferentes tipos de landmarks
            if hasattr(landmark, 'x') and hasattr(landmark, 'y'):
                x = int(landmark.x * self.frame_width)
                y = int(landmark.y * self.frame_height)
            elif isinstance(landmark, (tuple, list)) and len(landmark) >= 2:
                x = int(landmark[0] * self.frame_width)
                y = int(landmark[1] * self.frame_height)
            else:
                continue
            
            # Dibujar punto
            cv2.circle(frame, (x, y), 4, self.COLOR_BLUE, -1)

    def _draw_fps(self, frame: np.ndarray, fps: float) -> None:
        """Dibuja FPS en modo debug."""
        fps_text = f"FPS: {fps:.1f}"
        
        cv2.putText(
            frame,
            fps_text,
            (20, self.frame_height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.COLOR_GRAY,
            1,
            cv2.LINE_AA
        )
