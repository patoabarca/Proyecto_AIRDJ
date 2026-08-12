import unittest
import numpy as np
from src.hand_detector import HandDetector, LandmarkPoint, HandDetectionResult, HandLandmark

class TestHandDetector(unittest.TestCase):
    def setUp(self):
        """
        Inicializa el detector de mano en modo imagen estática para las pruebas.
        """
        self.detector = HandDetector(static_image_mode=True, max_num_hands=1)

    def test_empty_or_none_frame(self):
        """
        Prueba que un frame None o vacío no cause excepciones y devuelva detected=False.
        """
        result = self.detector.detect(None)
        self.assertFalse(result.detected)
        self.assertEqual(len(result.landmarks), 0)
        self.assertIsNone(result.center_normalized)
        self.assertIsNone(result.center_pixel)

        # Frame vacío (resolución 0x0)
        empty_frame = np.zeros((0, 0, 3), dtype=np.uint8)
        result_empty = self.detector.detect(empty_frame)
        self.assertFalse(result_empty.detected)
        self.assertEqual(len(result_empty.landmarks), 0)

    def test_landmark_pixel_conversion(self):
        """
        Comprueba que la conversión matemática de normalizado a píxel funcione
        según el ancho y alto del frame, controlando límites correctamente (clamping).
        """
        w, h = 640, 480
        
        # Caso 1: Centro exacto (0.5, 0.5)
        x_norm, y_norm = 0.5, 0.5
        pixel_x = int(min(max(0, x_norm * w), w - 1))
        pixel_y = int(min(max(0, y_norm * h), h - 1))
        self.assertEqual(pixel_x, 320)
        self.assertEqual(pixel_y, 240)

        # Caso 2: Límites superiores (1.0, 1.0) -> Deben quedar en w-1, h-1 para no desbordar índices
        x_norm, y_norm = 1.0, 1.0
        pixel_x = int(min(max(0, x_norm * w), w - 1))
        pixel_y = int(min(max(0, y_norm * h), h - 1))
        self.assertEqual(pixel_x, 639)
        self.assertEqual(pixel_y, 479)

        # Caso 3: Fuera de rango negativo (-0.1, -0.5) -> Debe clamplearse a 0
        x_norm, y_norm = -0.1, -0.5
        pixel_x = int(min(max(0, x_norm * w), w - 1))
        pixel_y = int(min(max(0, y_norm * h), h - 1))
        self.assertEqual(pixel_x, 0)
        self.assertEqual(pixel_y, 0)

        # Caso 4: Fuera de rango superior (1.2, 1.5) -> Debe clamplearse a w-1, h-1
        x_norm, y_norm = 1.2, 1.5
        pixel_x = int(min(max(0, x_norm * w), w - 1))
        pixel_y = int(min(max(0, y_norm * h), h - 1))
        self.assertEqual(pixel_x, 639)
        self.assertEqual(pixel_y, 479)

    def test_hand_center_calculation(self):
        """
        Prueba que el centro de la mano se calcule correctamente como el baricentro (promedio)
        de todos los landmarks tanto en coordenadas normalizadas como en píxeles.
        """
        landmarks = []
        w, h = 640, 480
        
        # Simulamos 21 landmarks distribuidos linealmente para calcular de forma predecible el promedio.
        # Punto i colocado en (i * 0.01, i * 0.02, 0.0)
        sum_x, sum_y = 0.0, 0.0
        for idx in range(21):
            x = idx * 0.01
            y = idx * 0.02
            z = 0.0
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
            sum_x += x
            sum_y += y
            
        # El promedio esperado
        expected_x_norm = sum_x / 21.0
        expected_y_norm = sum_y / 21.0
        expected_x_pixel = int(min(max(0, expected_x_norm * w), w - 1))
        expected_y_pixel = int(min(max(0, expected_y_norm * h), h - 1))
        
        # Creamos la estructura resultado
        res = HandDetectionResult(
            detected=True,
            landmarks=landmarks,
            center_normalized=(expected_x_norm, expected_y_norm),
            center_pixel=(expected_x_pixel, expected_y_pixel)
        )
        
        self.assertTrue(res.detected)
        self.assertAlmostEqual(res.center_normalized[0], expected_x_norm)
        self.assertAlmostEqual(res.center_normalized[1], expected_y_norm)
        self.assertEqual(res.center_pixel[0], expected_x_pixel)
        self.assertEqual(res.center_pixel[1], expected_y_pixel)

    def test_landmark_enum_access(self):
        """
        Verifica que se pueda acceder a landmarks específicos usando la enumeración de nombres descriptivos.
        """
        landmarks = [
            LandmarkPoint(index=i, x=0.1, y=0.1, z=0.0, pixel_x=10, pixel_y=10)
            for i in range(21)
        ]
        
        res = HandDetectionResult(
            detected=True,
            landmarks=landmarks,
            center_normalized=(0.1, 0.1),
            center_pixel=(10, 10)
        )
        
        # Comprobar acceso usando HandLandmark Enum
        wrist = res.landmarks[HandLandmark.WRIST]
        index_tip = res.landmarks[HandLandmark.INDEX_FINGER_TIP]
        
        self.assertEqual(wrist.index, 0)
        self.assertEqual(index_tip.index, 8)

if __name__ == '__main__':
    unittest.main()
