import unittest
from src.hand_detector import HandDetectionResult
from src.dynamic_gestures import SwipeDetector

class TestSwipeDetector(unittest.TestCase):
    def setUp(self):
        """
        Inicializa un SwipeDetector con valores de prueba controlados.
        """
        self.detector = SwipeDetector(
            min_dist=0.20,
            max_time_window=0.4,
            max_vertical_ratio=0.5,
            min_points=5,
            grace_time=0.0
        )

    def _make_result(self, detected: bool, x: float = 0.0, y: float = 0.0) -> HandDetectionResult:
        """
        Helper para crear un objeto HandDetectionResult simulado.
        """
        return HandDetectionResult(
            detected=detected,
            landmarks=[],
            center_normalized=(x, y) if detected else None,
            center_pixel=(int(x * 640), int(y * 480)) if detected else None
        )

    def test_no_hand_clears_history(self):
        """
        Verifica que al no detectarse la mano, el historial se limpie.
        """
        # Empezamos agregando un punto
        self.detector.update(self._make_result(True, 0.1, 0.5), current_time=1.0)
        self.assertEqual(len(self.detector.history), 1)

        # Ahora enviamos detected=False
        res = self.detector.update(self._make_result(False), current_time=1.1)
        self.assertIsNone(res)
        self.assertEqual(len(self.detector.history), 0)

    def test_swipe_derecha_success(self):
        """
        Verifica la correcta detección de un swipe rápido hacia la derecha.
        """
        # Simulamos 5 frames con movimiento continuo de izquierda (0.1) a derecha (0.35)
        # a lo largo de 0.2 segundos (dentro de la ventana de 0.4s)
        frames = [
            (0.10, 0.50, 1.00),
            (0.15, 0.50, 1.05),
            (0.20, 0.51, 1.10),
            (0.28, 0.49, 1.15),
            (0.35, 0.50, 1.20)
        ]

        for i, (x, y, t) in enumerate(frames):
            res = self.detector.update(self._make_result(True, x, y), current_time=t)
            if i < len(frames) - 1:
                self.assertIsNone(res, f"No debería detectar swipe en el frame {i}")
            else:
                self.assertEqual(res, "SWIPE_DERECHA", "Debería detectar SWIPE_DERECHA en el último frame")

        # El historial debe quedar vacío después de una detección exitosa
        self.assertEqual(len(self.detector.history), 0)

    def test_swipe_izquierda_success(self):
        """
        Verifica la correcta detección de un swipe rápido hacia la izquierda.
        """
        # Simulamos 5 frames de derecha (0.60) a izquierda (0.35) en 0.2 segundos
        frames = [
            (0.60, 0.40, 1.00),
            (0.55, 0.40, 1.05),
            (0.48, 0.41, 1.10),
            (0.41, 0.39, 1.15),
            (0.35, 0.40, 1.20)
        ]

        for i, (x, y, t) in enumerate(frames):
            res = self.detector.update(self._make_result(True, x, y), current_time=t)
            if i < len(frames) - 1:
                self.assertIsNone(res)
            else:
                self.assertEqual(res, "SWIPE_IZQUIERDA")

        self.assertEqual(len(self.detector.history), 0)

    def test_swipe_too_slow(self):
        """
        Verifica que un movimiento lento (que excede max_time_window) no dispare swipe.
        """
        # Movimiento lento constante de 0.10 a 0.32 (dx total = 0.22 >= 0.20) en 0.5s.
        # La velocidad es de 0.44/s. En cualquier ventana de 0.4s la distancia recorrida es de 0.176 (< 0.20).
        frames = [
            (0.100, 0.50, 1.00),
            (0.144, 0.50, 1.10),
            (0.188, 0.50, 1.20),
            (0.232, 0.50, 1.30),
            (0.276, 0.50, 1.40),
            (0.320, 0.50, 1.50)
        ]

        for x, y, t in frames:
            res = self.detector.update(self._make_result(True, x, y), current_time=t)
            self.assertIsNone(res)

    def test_swipe_too_short(self):
        """
        Verifica que un movimiento corto (dx < min_dist) no dispare swipe.
        """
        # Movimiento de 0.1 a 0.25 (dx = 0.15 < 0.20) en 0.2 segundos
        frames = [
            (0.10, 0.50, 1.00),
            (0.13, 0.50, 1.05),
            (0.17, 0.50, 1.10),
            (0.21, 0.50, 1.15),
            (0.25, 0.50, 1.20)
        ]

        for x, y, t in frames:
            res = self.detector.update(self._make_result(True, x, y), current_time=t)
            self.assertIsNone(res)

    def test_predominantly_vertical_rejected(self):
        """
        Verifica que movimientos diagonales o verticales con gran dy sean descartados.
        """
        # Movimiento de (0.1, 0.1) a (0.35, 0.7) -> dx = 0.25, dy = 0.60
        # dy/dx = 2.4 > max_vertical_ratio (0.5)
        frames = [
            (0.10, 0.10, 1.00),
            (0.15, 0.25, 1.05),
            (0.20, 0.40, 1.10),
            (0.28, 0.55, 1.15),
            (0.35, 0.70, 1.20)
        ]

        for x, y, t in frames:
            res = self.detector.update(self._make_result(True, x, y), current_time=t)
            self.assertIsNone(res)

    def test_insufficient_points(self):
        """
        Verifica que no se dispare un swipe con menos de min_points.
        """
        # Movimiento rápido de 0.1 a 0.4 (dx = 0.3) en 0.15s pero con solo 4 puntos
        frames = [
            (0.10, 0.50, 1.00),
            (0.20, 0.50, 1.05),
            (0.30, 0.50, 1.10),
            (0.40, 0.50, 1.15)
        ]

        for x, y, t in frames:
            res = self.detector.update(self._make_result(True, x, y), current_time=t)
            self.assertIsNone(res)

    def test_grace_period_retains_history(self):
        """
        Verifica que perder el tracking por un tiempo menor al grace_time
        retenga el historial y permita completar el swipe.
        """
        # Detector con grace_time = 0.2 segundos
        detector = SwipeDetector(
            min_dist=0.20,
            max_time_window=0.5,
            max_vertical_ratio=0.5,
            min_points=3,
            grace_time=0.20
        )

        # 1. Agregamos primer punto
        detector.update(self._make_result(True, 0.1, 0.5), current_time=1.0)
        self.assertEqual(len(detector.history), 1)

        # 2. Perder tracking durante 0.1s (menor que grace_time=0.20)
        res_loss = detector.update(self._make_result(False), current_time=1.1)
        self.assertIsNone(res_loss)
        # El historial se retiene
        self.assertEqual(len(detector.history), 1)

        # 3. Recuperar tracking y completar el swipe
        detector.update(self._make_result(True, 0.22, 0.5), current_time=1.2)
        res_final = detector.update(self._make_result(True, 0.35, 0.5), current_time=1.3)
        self.assertEqual(res_final, "SWIPE_DERECHA", "Debería detectar el swipe tras recuperarse")

    def test_grace_period_expires_clears_history(self):
        """
        Verifica que si la pérdida de tracking supera el grace_time,
        el historial se limpie por completo.
        """
        detector = SwipeDetector(
            min_dist=0.20,
            max_time_window=0.5,
            max_vertical_ratio=0.5,
            min_points=3,
            grace_time=0.20
        )

        # 1. Agregamos punto
        detector.update(self._make_result(True, 0.1, 0.5), current_time=1.0)
        self.assertEqual(len(detector.history), 1)

        # 2. Perder tracking durante 0.25s (mayor que grace_time=0.20)
        res_loss = detector.update(self._make_result(False), current_time=1.25)
        self.assertIsNone(res_loss)
        # El historial debe haberse limpiado
        self.assertEqual(len(detector.history), 0)

if __name__ == '__main__':
    unittest.main()
