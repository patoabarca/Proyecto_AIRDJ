import math
from typing import List, Tuple, Optional, Any

try:
    from src.hand_detector import HandLandmark
except ImportError:
    # Fallback de enumeración si no se puede importar la clase del detector de mano
    from enum import IntEnum
    class HandLandmark(IntEnum):
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

class VolumeController:
    """
    Clase responsable de convertir las posiciones de los landmarks de una mano
    en un valor de volumen normalizado (0-100%) y suavizado temporalmente.
    
    Esta implementación es desacoplada y modular, siguiendo un diseño académico.
    """
    
    def __init__(self, 
                 min_distance: float = 0.2, 
                 max_distance: float = 1.0, 
                 smooth_alpha: float = 0.15):
        """
        Inicializa el controlador de volumen con parámetros configurables.
        
        Args:
            min_distance (float): Distancia normalizada mínima (0% de volumen).
            max_distance (float): Distancia normalizada máxima (100% de volumen).
            smooth_alpha (float): Factor de suavizado para la media móvil exponencial (0.0 < alpha <= 1.0).
        """
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.smooth_alpha = smooth_alpha
        
        # Estado interno para el suavizado temporal (EMA)
        self.current_volume: Optional[float] = None

    def _get_coords(self, lm: Any) -> Optional[Tuple[float, float]]:
        """
        Extrae las coordenadas X e Y de un landmark de forma flexible.
        Prioriza coordenadas en píxeles ('pixel_x', 'pixel_y') para evitar distorsiones
        de relación de aspecto, pero permite fallback a coordenadas normalizadas ('x', 'y').
        
        Args:
            lm (Any): Un punto de referencia de la mano (objeto, diccionario, tupla, etc.)
            
        Returns:
            Optional[Tuple[float, float]]: Tupla (x, y) de coordenadas o None si es inválido.
        """
        if lm is None:
            return None
            
        # 1. Intentar con atributos de objeto (pixel_x, pixel_y)
        if hasattr(lm, 'pixel_x') and hasattr(lm, 'pixel_y'):
            return float(lm.pixel_x), float(lm.pixel_y)
            
        # 2. Intentar con diccionario (pixel_x, pixel_y)
        if isinstance(lm, dict) and 'pixel_x' in lm and 'pixel_y' in lm:
            return float(lm['pixel_x']), float(lm['pixel_y'])
            
        # 3. Intentar con atributos de objeto normalizados (x, y)
        if hasattr(lm, 'x') and hasattr(lm, 'y'):
            return float(lm.x), float(lm.y)
            
        # 4. Intentar con diccionario normalizado (x, y)
        if isinstance(lm, dict) and 'x' in lm and 'y' in lm:
            return float(lm['x']), float(lm['y'])
            
        # 5. Intentar si es lista/tupla de al menos 2 elementos
        if isinstance(lm, (list, tuple)) and len(lm) >= 2:
            return float(lm[0]), float(lm[1])
            
        return None

    def calculate_distance(self, p1: Any, p2: Any) -> float:
        """
        Calcula la distancia euclidiana en 2D entre dos landmarks.
        
        Args:
            p1 (Any): Landmark inicial.
            p2 (Any): Landmark final.
            
        Returns:
            float: Distancia euclidiana calculada. Si alguno es inválido, devuelve 0.0.
        """
        coords1 = self._get_coords(p1)
        coords2 = self._get_coords(p2)
        
        if coords1 is None or coords2 is None:
            return 0.0
            
        x1, y1 = coords1
        x2, y2 = coords2
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def normalize_distance(self, raw_dist: float, ref_dist: float) -> float:
        """
        Normaliza la distancia de control dividiéndola por la distancia de referencia estable.
        Evita la división por cero o por valores extremadamente pequeños.
        
        Args:
            raw_dist (float): Distancia cruda entre pulgar e índice.
            ref_dist (float): Distancia de referencia estable (ej: muñeca a base del índice).
            
        Returns:
            float: Distancia normalizada.
        """
        if ref_dist <= 1e-5:
            return 0.0
        return raw_dist / ref_dist

    def map_to_volume(self, norm_dist: float) -> float:
        """
        Mapea linealmente la distancia normalizada de [min_distance, max_distance]
        a un rango de volumen [0.0, 100.0] aplicando límites estrictos (clamping).
        
        Args:
            norm_dist (float): Distancia normalizada calculada.
            
        Returns:
            float: Volumen crudo mapeado (0.0 a 100.0).
        """
        if norm_dist <= self.min_distance:
            return 0.0
        if norm_dist >= self.max_distance:
            return 100.0
            
        # Mapeo lineal: (norm_dist - min) / (max - min) * 100
        vol_range = self.max_distance - self.min_distance
        if vol_range <= 1e-5:
            return 0.0
            
        raw_volume = ((norm_dist - self.min_distance) / vol_range) * 100.0
        return max(0.0, min(100.0, raw_volume))

    def smooth_volume(self, raw_volume: float) -> float:
        """
        Aplica suavizado temporal mediante Media Móvil Exponencial (EMA)
        para mitigar variaciones y temblores ligeros en los landmarks.
        
        Args:
            raw_volume (float): Volumen crudo calculado en el frame actual.
            
        Returns:
            float: Volumen suavizado actual.
        """
        if self.current_volume is None:
            # Inicialización en el primer frame válido
            self.current_volume = raw_volume
        else:
            # Fórmula EMA: alpha * raw + (1 - alpha) * prev
            self.current_volume = (self.smooth_alpha * raw_volume + 
                                   (1.0 - self.smooth_alpha) * self.current_volume)
        return self.current_volume

    def update(self, landmarks: List[Any]) -> Optional[float]:
        """
        Método principal del controlador. Recibe la lista de landmarks,
        realiza validaciones de seguridad, calcula, normaliza, mapea y suaviza el volumen.
        
        Args:
            landmarks (List[Any]): Lista de landmarks (ej: salida de HandDetector).
            
        Returns:
            Optional[float]: Volumen calculado y suavizado (0.0 a 100.0) o el último valor
                             válido si la entrada es inválida. Devuelve None si no hay
                             valores válidos históricos previos.
        """
        # Validación de seguridad de la estructura de entrada
        if not landmarks or not isinstance(landmarks, list):
            return self.current_volume

        # Buscamos landmarks por índice para soportar tanto listas indexadas como desordenadas
        wrist_lm = None
        thumb_tip_lm = None
        index_mcp_lm = None
        index_tip_lm = None

        # Si están en una lista estándar ordenados por índice de 0 a 20 (comportamiento por defecto de MediaPipe)
        # Hacemos una búsqueda segura basada en el atributo index o la posición en la lista.
        # Intentamos obtenerlos de forma segura:
        try:
            # Primero intentamos buscar por atributo index (LandmarkPoint de hand_detector.py lo tiene)
            for lm in landmarks:
                if hasattr(lm, 'index'):
                    idx = lm.index
                elif isinstance(lm, dict) and 'index' in lm:
                    idx = lm['index']
                else:
                    idx = None
                
                if idx == HandLandmark.WRIST:
                    wrist_lm = lm
                elif idx == HandLandmark.THUMB_TIP:
                    thumb_tip_lm = lm
                elif idx == HandLandmark.INDEX_FINGER_MCP:
                    index_mcp_lm = lm
                elif idx == HandLandmark.INDEX_FINGER_TIP:
                    index_tip_lm = lm
            
            # Si no se encontraron por atributo 'index', intentamos acceder directamente por posición
            # si la lista tiene al menos 9 elementos (para cubrir índice 8 de INDEX_FINGER_TIP)
            if (wrist_lm is None or thumb_tip_lm is None or 
                index_mcp_lm is None or index_tip_lm is None):
                if len(landmarks) >= 9:
                    wrist_lm = landmarks[HandLandmark.WRIST]
                    thumb_tip_lm = landmarks[HandLandmark.THUMB_TIP]
                    index_mcp_lm = landmarks[HandLandmark.INDEX_FINGER_MCP]
                    index_tip_lm = landmarks[HandLandmark.INDEX_FINGER_TIP]
        except Exception:
            # Ante cualquier error de indexación no contemplado, no rompemos el programa
            return self.current_volume

        # Validamos que los 4 landmarks requeridos existan y tengan coordenadas legibles
        if (wrist_lm is None or thumb_tip_lm is None or 
            index_mcp_lm is None or index_tip_lm is None):
            return self.current_volume

        # 1. Calcular distancia de control pulgar-índice (cruda)
        d_control = self.calculate_distance(thumb_tip_lm, index_tip_lm)
        
        # 2. Calcular distancia de referencia estable (muñeca-nudillo índice)
        d_ref = self.calculate_distance(wrist_lm, index_mcp_lm)

        # Si la referencia es inválida, retornar el último estado seguro
        if d_ref <= 1e-5:
            return self.current_volume

        # 3. Normalizar la distancia
        d_norm = self.normalize_distance(d_control, d_ref)

        # 4. Mapear al rango 0-100%
        v_raw = self.map_to_volume(d_norm)

        # 5. Aplicar suavizado temporal y actualizar estado
        return self.smooth_volume(v_raw)
