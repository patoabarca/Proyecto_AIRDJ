import unittest
import math
from src.activation import ActivationController, ActivationResult

class TestActivationController(unittest.TestCase):
    def setUp(self):
        """
        Inicializa un ActivationController con valores estándar para las pruebas.
        """
        # Usamos hold_time de 1.5s y umbral de estabilidad de 0.04
        self.controller = ActivationController(
            activation_hold_time=1.5,
            stability_threshold=0.04,
            require_zone=True,
            window_size=10
        )

    def test_palma_short_time(self):
        """
        1. Mostrar PALMA durante menos de 1,5 segundos y comprobar que no se active.
        """
        # Inicio a t=0.0
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        self.assertTrue(res.is_activating)
        self.assertEqual(res.progress, 0.0)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.status, "ACTIVATING")

        # Transcurrido 1.0s (menor a 1.5s)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.0)
        self.assertTrue(res.is_activating)
        self.assertAlmostEqual(res.progress, 1.0 / 1.5)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.status, "ACTIVATING")

        # Transcurrido 1.49s (menor a 1.5s)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.49)
        self.assertTrue(res.is_activating)
        self.assertAlmostEqual(res.progress, 1.49 / 1.5)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.status, "ACTIVATING")

    def test_palma_stable_activation(self):
        """
        2. Mantener PALMA estable durante al menos 1,5 segundos y comprobar
        que genere ACTIVACION_CONFIRMADA exactamente una vez.
        """
        # Inicio t=0.0
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        
        # t=1.0
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.0)
        
        # t=1.5 (se alcanza el tiempo)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.5)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 1.0)
        self.assertTrue(res.activation_confirmed)
        self.assertEqual(res.status, "CONFIRMED")

        # Frame siguiente t=1.6, sigue siendo PALMA estable
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.6)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 1.0)
        # No debe volver a emitirse la confirmación en los updates siguientes
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.status, "CONFIRMED")

    def test_palma_unstable_cancellation(self):
        """
        3. Mantener PALMA pero desplazar considerablemente el centro antes de
        completar 1,5 segundos y comprobar que cancele la activación.
        """
        # Inicio t=0.0 en (0.5, 0.5)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        self.assertTrue(res.is_activating)

        # t=0.1 en (0.5, 0.5)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.1)
        self.assertTrue(res.is_activating)

        # t=0.2. Desplazamiento brusco a (0.55, 0.5) -> dist = 0.05 > 0.04 (umbral)
        res = self.controller.update(gesture="PALMA", hand_center=(0.55, 0.5), timestamp=0.2)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 0.0)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.status, "CANCELLED")
        self.assertIsNone(self.controller.start_time)
        self.assertEqual(len(self.controller.position_history), 0)

    def test_palma_fist_cancellation(self):
        """
        4. Probar una secuencia PALMA -> PALMA -> PUÑO antes de alcanzar el tiempo
        y comprobar que cancele regresando el progreso a cero.
        """
        # t=0.0 PALMA
        res1 = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        self.assertTrue(res1.is_activating)

        # t=0.5 PALMA
        res2 = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.5)
        self.assertTrue(res2.is_activating)
        self.assertAlmostEqual(res2.progress, 0.5 / 1.5)

        # t=1.0 PUÑO
        res3 = self.controller.update(gesture="PUÑO", hand_center=(0.5, 0.5), timestamp=1.0)
        self.assertFalse(res3.is_activating)
        self.assertEqual(res3.progress, 0.0)
        self.assertFalse(res3.activation_confirmed)
        self.assertEqual(res3.status, "CANCELLED")

    def test_palma_none_cancellation(self):
        """
        5. Probar PALMA -> PALMA -> None y comprobar que el progreso vuelva a cero.
        """
        # t=0.0 PALMA
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        
        # t=0.5 PALMA
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.5)
        self.assertAlmostEqual(res.progress, 0.5 / 1.5)

        # t=1.0 None (deja de detectarse mano)
        res = self.controller.update(gesture=None, hand_center=None, timestamp=1.0)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 0.0)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.status, "CANCELLED")

    def test_palma_micro_movements(self):
        """
        6. Simular pequeñas variaciones naturales del centro de la mano y verificar
        que la activación continúe sin cancelarse (deriva lenta).
        """
        # Inicio t=0.0 en (0.5, 0.5)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        self.assertTrue(res.is_activating)

        # Simulamos una deriva lenta de 0.003 por frame durante 14 frames
        # La ventana es de tamaño 10, la máxima separación de puntos dentro de la ventana
        # es de 9 * 0.003 = 0.027 < 0.04. Por lo tanto, la activación debe continuar.
        for i in range(1, 15):
            pos_x = 0.5 + (0.003 * i)
            res = self.controller.update(
                gesture="PALMA",
                hand_center=(pos_x, 0.5),
                timestamp=0.1 * i
            )
            self.assertTrue(res.is_activating, f"Falló en el frame {i} con posición {pos_x}")
            self.assertEqual(res.status, "ACTIVATING")

        # El frame 15 (t=1.5) debe confirmar la activación
        res = self.controller.update(
            gesture="PALMA",
            hand_center=(0.5 + 0.003 * 15, 0.5),
            timestamp=1.5
        )
        self.assertFalse(res.is_activating)
        self.assertTrue(res.activation_confirmed)
        self.assertEqual(res.status, "CONFIRMED")

    def test_palma_long_hold_single_emission(self):
        """
        7. Mantener la palma durante aproximadamente 3 segundos y verificar
        que ACTIVACION_CONFIRMADA se emita una sola vez y no se repita frame a frame.
        """
        # t=0.0
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        
        # t=1.0
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.0)

        # t=1.5 (Confirmado)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.5)
        self.assertTrue(res.activation_confirmed)
        self.assertEqual(res.status, "CONFIRMED")

        # t=2.0 (Hold prolongado)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=2.0)
        self.assertFalse(res.activation_confirmed) # No se vuelve a emitir
        self.assertEqual(res.progress, 1.0)
        self.assertEqual(res.status, "CONFIRMED")

        # t=3.0 (Hold prolongado)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=3.0)
        self.assertFalse(res.activation_confirmed) # No se vuelve a emitir
        self.assertEqual(res.progress, 1.0)
        self.assertEqual(res.status, "CONFIRMED")

    def test_reset_after_activation(self):
        """
        8. Después de una activación confirmada ejecutar reset() y comprobar
        que el controlador quede totalmente limpio y permita una nueva activación.
        """
        # Completar activación 1
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.5)
        
        # Confirmar que está en estado emitido
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=2.0)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.status, "CONFIRMED")

        # Ejecutar reset()
        self.controller.reset()
        self.assertFalse(self.controller.activation_emitted)
        self.assertEqual(self.controller.progress, 0.0)
        self.assertIsNone(self.controller.start_time)
        self.assertEqual(len(self.controller.position_history), 0)

        # Iniciar activación 2
        res = self.controller.update(gesture="PALMA", hand_center=(0.6, 0.6), timestamp=3.0)
        self.assertTrue(res.is_activating)
        self.assertEqual(res.progress, 0.0)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.status, "ACTIVATING")

    def test_inside_zone_validation(self):
        """
        9. Probar require_zone=False permite activar aunque inside_zone=False,
        y require_zone=True impide la activación si inside_zone=False.
        """
        # Caso A: require_zone=True (Predeterminado)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0, inside_zone=False)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 0.0)
        self.assertEqual(res.status, "IDLE")

        # Caso B: require_zone=False
        controller_no_zone = ActivationController(require_zone=False)
        res = controller_no_zone.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0, inside_zone=False)
        self.assertTrue(res.is_activating)
        self.assertEqual(res.status, "ACTIVATING")
        
        res = controller_no_zone.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.5, inside_zone=False)
        self.assertTrue(res.activation_confirmed)
        self.assertEqual(res.status, "CONFIRMED")

    def test_robustness_invalid_inputs(self):
        """
        10. Probar entradas inválidas o incompletas y comprobar que no generen excepciones no controladas.
        """
        try:
            # Entrada None en gesto
            res = self.controller.update(gesture=None, hand_center=(0.5, 0.5), timestamp=0.0)
            self.assertFalse(res.is_activating)
            self.assertEqual(res.status, "IDLE")
            
            # Entrada None en centro
            res = self.controller.update(gesture="PALMA", hand_center=None, timestamp=0.0)
            self.assertFalse(res.is_activating)

            # Entrada timestamp inválido o None
            res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=None)

            # Estructuras de centro incorrectas
            res = self.controller.update(gesture="PALMA", hand_center=(0.5,), timestamp=0.0)
            res = self.controller.update(gesture="PALMA", hand_center="centro", timestamp=0.0)
            res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5, 0.5), timestamp=0.0)
            res = self.controller.update(gesture="PALMA", hand_center=(float('nan'), 0.5), timestamp=0.0)

            # Tipos de entrada inválidos para gesture y inside_zone
            res = self.controller.update(gesture=123, hand_center=(0.5, 0.5), timestamp=0.0)
            res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0, inside_zone="invalido")

        except Exception as e:
            self.fail(f"La llamada update() arrojó una excepción no controlada: {e}")

if __name__ == '__main__':
    unittest.main()
