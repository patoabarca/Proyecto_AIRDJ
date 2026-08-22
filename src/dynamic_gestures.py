import time
from collections import deque
from typing import Optional, Tuple
from src.hand_detector import HandDetectionResult

class SwipeDetector:
    """
    Clase para detectar gestos dinámicos de desplazamiento horizontal (swipes) 
    a partir del historial de posiciones del centro de la mano en coordenadas normalizadas.
    """
    def __init__(self, 
                 min_dist: float = 0.15, 
                 max_time_window: float = 0.8, 
                 max_vertical_ratio: float = 0.6,
                 min_points: int = 3,
                 grace_time: float = 0.20):
        """
        Inicializa el detector de swipes.

        Args:
            min_dist (float): Distancia horizontal mínima acumulada en coordenadas 
                              normalizadas (0.0 a 1.0) para considerar un swipe.
            max_time_window (float): Tiempo máximo en segundos para completar el gesto.
            max_vertical_ratio (float): Relación máxima entre desplazamiento vertical y 
                                        horizontal. Si dy/dx supera este valor, el 
                                        movimiento no se considera horizontal.
            min_points (int): Número mínimo de posiciones en el historial para 
                              validar el gesto.
            grace_time (float): Tiempo de gracia en segundos que se retiene el historial 
                                tras perder el tracking de la mano antes de limpiarlo.
        """
        self.min_dist = min_dist
        self.max_time_window = max_time_window
        self.max_vertical_ratio = max_vertical_ratio
        self.min_points = min_points
        self.grace_time = grace_time
        
        # Historial de posiciones: almacena tuplas de (x, y, timestamp)
        self.history = deque()
        self.last_seen_time = 0.0

    def update(self, result: HandDetectionResult, current_time: Optional[float] = None) -> Optional[str]:
        """
        Actualiza el historial con la posición actual de la mano y comprueba 
        si se ha realizado un gesto de swipe.

        Args:
            result (HandDetectionResult): Resultado de la detección del frame actual.
            current_time (Optional[float]): Marca de tiempo actual para control determinista en pruebas.

        Returns:
            Optional[str]: 'SWIPE_DERECHA', 'SWIPE_IZQUIERDA' o None si no se detecta.
        """
        if current_time is None:
            current_time = time.time()

        # Si la mano no fue detectada, retenemos el historial durante grace_time
        # para tolerar dropouts puntuales causados por desenfoque de movimiento (motion blur).
        if not result.detected or result.center_normalized is None:
            if current_time - self.last_seen_time > self.grace_time:
                self.clear()
            return None

        self.last_seen_time = current_time
        x, y = result.center_normalized
        self.history.append((x, y, current_time))

        # Limpiar puntos antiguos que excedan la ventana de tiempo máxima
        while self.history and (current_time - self.history[0][2] > self.max_time_window):
            self.history.popleft()

        # Validar si tenemos suficientes puntos e historial temporal
        if len(self.history) < self.min_points:
            return None

        duration = self.history[-1][2] - self.history[0][2]
        if duration < 0.05:  # Duración mínima de 50ms para evitar ruidos instantáneos
            return None

        # Coordenadas iniciales y finales en el historial filtrado
        x_start, y_start, _ = self.history[0]
        x_end, y_end, _ = self.history[-1]

        # Desplazamiento neto horizontal (dx) y vertical (dy)
        dx = x_end - x_start
        dy = y_end - y_start

        abs_dx = abs(dx)
        abs_dy = abs(dy)

        # Comprobar si cumple con la distancia horizontal mínima
        if abs_dx >= self.min_dist:
            # Comprobar si el movimiento es predominantemente horizontal
            # Evita divisiones por cero comparando con el ratio
            if abs_dy <= self.max_vertical_ratio * abs_dx:
                # Determinar dirección del swipe
                gesture = "SWIPE_DERECHA" if dx > 0 else "SWIPE_IZQUIERDA"
                # Limpiar el historial para evitar detectar el mismo swipe repetidamente
                self.clear()
                return gesture

        return None

    def clear(self):
        """
        Limpia el historial de posiciones de la mano.
        """
        self.history.clear()
