import unittest
import math
from src.volume_control import VolumeController, HandLandmark

class MockLandmark:
    """Clase Mock para emular la estructura de LandmarkPoint."""
    def __init__(self, index: int, pixel_x: float, pixel_y: float, x: float = 0.0, y: float = 0.0):
        self.index = index
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.x = x
        self.y = y

class TestVolumeController(unittest.TestCase):
    def setUp(self):
        # Inicializa un controlador de volumen con parámetros estándar
        self.controller = VolumeController(min_distance=0.2, max_distance=1.0, smooth_alpha=0.15)
        
        # Mano de referencia (escala base)
        # Distancia de referencia (WRIST 0 a INDEX_FINGER_MCP 5):
        # WRIST: (100, 400)
        # INDEX_FINGER_MCP: (100, 300) -> Distancia = 100 píxeles
        self.wrist = (100, 400)
        self.index_mcp = (100, 300)
        
    def _create_landmarks(self, thumb_coords, index_tip_coords):
        """Crea una lista mock de landmarks con los puntos requeridos."""
        return [
            MockLandmark(HandLandmark.WRIST, self.wrist[0], self.wrist[1]),
            MockLandmark(1, 0, 0),
            MockLandmark(2, 0, 0),
            MockLandmark(3, 0, 0),
            MockLandmark(HandLandmark.THUMB_TIP, thumb_coords[0], thumb_coords[1]),
            MockLandmark(HandLandmark.INDEX_FINGER_MCP, self.index_mcp[0], self.index_mcp[1]),
            MockLandmark(6, 0, 0),
            MockLandmark(7, 0, 0),
            MockLandmark(HandLandmark.INDEX_FINGER_TIP, index_tip_coords[0], index_tip_coords[1])
        ]

    def test_fingers_touching_minimum_volume(self):
        """Prueba que cuando el pulgar y el índice están juntos, el volumen es 0%."""
        # Distancia de control (THUMB_TIP a INDEX_FINGER_TIP):
        # Ambos en (100, 200) -> Distancia = 0
        # Distancia de referencia = 100
        # Distancia normalizada = 0 / 100 = 0.0 (menor que MIN_DISTANCE = 0.2)
        landmarks = self._create_landmarks(thumb_coords=(100, 200), index_tip_coords=(100, 200))
        volume = self.controller.update(landmarks)
        self.assertEqual(volume, 0.0)

    def test_fingers_intermediate_volume(self):
        """Prueba que una separación intermedia mapea a un volumen intermedio."""
        # Queremos una distancia normalizada de 0.6 (punto medio entre 0.2 y 1.0)
        # Si D_ref = 100, entonces D_control debe ser 60 píxeles.
        # THUMB_TIP: (70, 200)
        # INDEX_FINGER_TIP: (130, 200) -> Distancia = 60
        # Distancia normalizada = 60 / 100 = 0.6
        # Volumen esperado: (0.6 - 0.2) / (1.0 - 0.2) * 100 = 0.4 / 0.8 * 100 = 50.0%
        # Como es el primer frame, no se aplica EMA y se retorna directamente 50.0%
        landmarks = self._create_landmarks(thumb_coords=(70, 200), index_tip_coords=(130, 200))
        volume = self.controller.update(landmarks)
        self.assertAlmostEqual(volume, 50.0, places=2)

    def test_fingers_wide_apart_maximum_volume(self):
        """Prueba que cuando los dedos están muy separados, el volumen es 100%."""
        # D_ref = 100. Queremos distancia >= 100 píxeles para llegar al máximo (1.0).
        # THUMB_TIP: (50, 200)
        # INDEX_FINGER_TIP: (150, 200) -> Distancia = 100
        # Distancia normalizada = 100 / 100 = 1.0 (igual a MAX_DISTANCE)
        landmarks = self._create_landmarks(thumb_coords=(50, 200), index_tip_coords=(150, 200))
        volume = self.controller.update(landmarks)
        self.assertEqual(volume, 100.0)

    def test_limits_clamping(self):
        """Prueba que los límites inferior (0%) y superior (100%) se clamplean correctamente."""
        # Caso inferior al mínimo: distancia normalizada de 0.1 (menor que MIN_DISTANCE = 0.2)
        # D_control = 10 -> Distancia normalizada = 0.1
        landmarks_low = self._create_landmarks(thumb_coords=(100, 200), index_tip_coords=(100, 210))
        volume_low = self.controller.update(landmarks_low)
        self.assertEqual(volume_low, 0.0)

        # Caso superior al máximo: distancia normalizada de 1.5 (mayor que MAX_DISTANCE = 1.0)
        # D_control = 150 -> Distancia normalizada = 1.5
        # Re-inicializamos el controlador para no arrastrar el volumen del caso anterior en tests aislados
        controller = VolumeController(min_distance=0.2, max_distance=1.0)
        landmarks_high = self._create_landmarks(thumb_coords=(25, 200), index_tip_coords=(175, 200))
        volume_high = controller.update(landmarks_high)
        self.assertEqual(volume_high, 100.0)

    def test_temporal_smoothing_ema(self):
        """Prueba que el suavizado temporal (EMA) funcione y mitigue cambios bruscos."""
        # Primer frame: volumen crudo = 50.0% (distancia normalizada 0.6)
        landmarks1 = self._create_landmarks(thumb_coords=(70, 200), index_tip_coords=(130, 200))
        vol1 = self.controller.update(landmarks1)
        self.assertAlmostEqual(vol1, 50.0, places=2)

        # Segundo frame: cambio brusco a volumen crudo = 100.0% (distancia normalizada 1.0)
        # Con alpha = 0.15:
        # volumen_smooth = 0.15 * 100.0 + 0.85 * 50.0 = 15.0 + 42.5 = 57.5%
        landmarks2 = self._create_landmarks(thumb_coords=(50, 200), index_tip_coords=(150, 200))
        vol2 = self.controller.update(landmarks2)
        self.assertAlmostEqual(vol2, 57.5, places=2)

        # Tercer frame: mantenemos la posición para simular estabilidad
        # volumen_smooth = 0.15 * 100.0 + 0.85 * 57.5 = 15.0 + 48.875 = 63.875%
        vol3 = self.controller.update(landmarks2)
        self.assertAlmostEqual(vol3, 63.875, places=3)

    def test_small_landmark_variations(self):
        """Prueba que pequeñas variaciones se suavicen y no causen saltos bruscos."""
        # Frame 1: 50.0%
        landmarks = self._create_landmarks(thumb_coords=(70, 200), index_tip_coords=(130, 200))
        vol = self.controller.update(landmarks)
        
        # Frame 2: pequeña variación (ej: 1 píxel de ruido)
        # THUMB_TIP: (70, 201) en lugar de (70, 200)
        landmarks_noisy = self._create_landmarks(thumb_coords=(70, 201), index_tip_coords=(130, 200))
        vol_noisy = self.controller.update(landmarks_noisy)
        
        # La variación en la salida debe ser extremadamente pequeña debido a la EMA
        difference = abs(vol_noisy - vol)
        self.assertLess(difference, 2.0)

    def test_scale_independence(self):
        """Prueba que el volumen sea independiente de la escala (distancia a la cámara)."""
        # Escala 1 (Mano chica / lejos): D_ref = 100, D_control = 60 -> volumen crudo = 50.0%
        controller1 = VolumeController(min_distance=0.2, max_distance=1.0)
        landmarks_small = self._create_landmarks(thumb_coords=(70, 200), index_tip_coords=(130, 200))
        vol_small = controller1.update(landmarks_small)

        # Escala 2 (Mano duplicada en tamaño / cerca):
        # WRIST: (200, 800)
        # INDEX_FINGER_MCP: (200, 600) -> D_ref = 200 píxeles (el doble)
        # Para mantener la misma apertura de la mano, D_control debe ser 120 píxeles.
        # THUMB_TIP: (140, 400)
        # INDEX_FINGER_TIP: (260, 400) -> D_control = 120
        controller2 = VolumeController(min_distance=0.2, max_distance=1.0)
        
        landmarks_large = [
            MockLandmark(HandLandmark.WRIST, 200, 800),
            MockLandmark(1, 0, 0),
            MockLandmark(2, 0, 0),
            MockLandmark(3, 0, 0),
            MockLandmark(HandLandmark.THUMB_TIP, 140, 400),
            MockLandmark(HandLandmark.INDEX_FINGER_MCP, 200, 600),
            MockLandmark(6, 0, 0),
            MockLandmark(7, 0, 0),
            MockLandmark(HandLandmark.INDEX_FINGER_TIP, 260, 400)
        ]
        
        vol_large = controller2.update(landmarks_large)
        self.assertAlmostEqual(vol_small, vol_large, places=2)

    def test_invalid_or_incomplete_inputs(self):
        """Prueba que las entradas inválidas sean controladas sin excepciones."""
        # Caso 1: landmarks = None
        self.assertIsNone(self.controller.update(None))

        # Caso 2: lista vacía
        self.assertIsNone(self.controller.update([]))

        # Caso 3: lista incompleta (falta INDEX_FINGER_TIP)
        incomplete_landmarks = [
            MockLandmark(HandLandmark.WRIST, 100, 400),
            MockLandmark(HandLandmark.THUMB_TIP, 100, 200),
            MockLandmark(HandLandmark.INDEX_FINGER_MCP, 100, 300)
        ]
        self.assertIsNone(self.controller.update(incomplete_landmarks))

        # Caso 4: mantener el último valor válido ante una entrada inválida posterior
        # Frame 1: Válido (volumen 100.0%)
        valid_landmarks = self._create_landmarks(thumb_coords=(50, 200), index_tip_coords=(150, 200))
        vol_valid = self.controller.update(valid_landmarks)
        self.assertEqual(vol_valid, 100.0)

        # Frame 2: Inválido -> debe retornar el último volumen válido de la memoria (100.0)
        vol_after_invalid = self.controller.update(None)
        self.assertEqual(vol_after_invalid, 100.0)

if __name__ == '__main__':
    unittest.main()
