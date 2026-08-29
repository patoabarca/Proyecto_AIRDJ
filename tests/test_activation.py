import unittest
import time
from src.activation import ActivationController, ActivationResult

class TestActivationController(unittest.TestCase):
    def setUp(self):
        """
        Inicializa un ActivationController con valores estándar para las pruebas.
        """
        # Usamos hold_time de 1.5s y umbral de estabilidad de 0.08
        self.controller = ActivationController(
            activation_hold_time=1.5,
            stability_threshold=0.08,
            require_zone=True
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

        # Transcurrido 1.0s (menor a 1.5s)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.0)
        self.assertTrue(res.is_activating)
        self.assertAlmostEqual(res.progress, 1.0 / 1.5)
        self.assertFalse(res.activation_confirmed)

        # Transcurrido 1.49s (menor a 1.5s)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.49)
        self.assertTrue(res.is_activating)
        self.assertAlmostEqual(res.progress, 1.49 / 1.5)
        self.assertFalse(res.activation_confirmed)

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

        # Frame siguiente t=1.6, sigue siendo PALMA estable
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.6)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 1.0)
        # No debe volver a emitirse la confirmación
        self.assertFalse(res.activation_confirmed)

    def test_palma_unstable_cancellation(self):
        """
        3. Mantener PALMA pero desplazar considerablemente el centro antes de
        completar 1,5 segundos y comprobar que cancele o reinicie la activación.
        """
        # Inicio t=0.0 en (0.5, 0.5)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        self.assertTrue(res.is_activating)

        # t=1.0. Desplazamiento grande a (0.7, 0.5) -> dist = 0.2 > 0.08
        res = self.controller.update(gesture="PALMA", hand_center=(0.7, 0.5), timestamp=1.0)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 0.0)
        self.assertFalse(res.activation_confirmed)
        self.assertIsNone(self.controller.start_time)
        self.assertIsNone(self.controller.reference_center)

    def test_palma_fist_cancellation(self):
        """
        4. Probar una secuencia PALMA -> PALMA -> PUÑO antes de alcanzar el tiempo
        y comprobar que cancele.
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

    def test_palma_micro_movements(self):
        """
        6. Simular pequeñas variaciones naturales del centro de la mano y verificar
        que la activación continúe.
        """
        # Inicio t=0.0 en (0.5, 0.5)
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)

        # t=0.5. Pequeña variación a (0.52, 0.49) -> dist = sqrt(0.02^2 + 0.01^2) = 0.022 < 0.08
        res = self.controller.update(gesture="PALMA", hand_center=(0.52, 0.49), timestamp=0.5)
        self.assertTrue(res.is_activating)
        self.assertAlmostEqual(res.progress, 0.5 / 1.5)
        self.assertFalse(res.activation_confirmed)

        # t=1.5. Otra pequeña variación a (0.49, 0.51) respecto al centro original (0.5, 0.5)
        # dist = sqrt(0.01^2 + 0.01^2) = 0.014 < 0.08
        res = self.controller.update(gesture="PALMA", hand_center=(0.49, 0.51), timestamp=1.5)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 1.0)
        self.assertTrue(res.activation_confirmed)

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

        # t=2.0 (Hold prolongado)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=2.0)
        self.assertFalse(res.activation_confirmed) # No se vuelve a emitir
        self.assertEqual(res.progress, 1.0)

        # t=3.0 (Hold prolongado)
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=3.0)
        self.assertFalse(res.activation_confirmed) # No se vuelve a emitir
        self.assertEqual(res.progress, 1.0)

    def test_reset_after_activation(self):
        """
        8. Después de una activación confirmada ejecutar reset() y comprobar
        que pueda realizarse una nueva activación.
        """
        # Completar activación 1
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0)
        self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.5)
        
        # Confirmar que está en estado emitido
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=2.0)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.progress, 1.0)

        # Ejecutar reset()
        self.controller.reset()
        self.assertFalse(self.controller.activation_emitted)
        self.assertEqual(self.controller.progress, 0.0)

        # Iniciar activación 2
        res = self.controller.update(gesture="PALMA", hand_center=(0.6, 0.6), timestamp=3.0)
        self.assertTrue(res.is_activating)
        self.assertEqual(res.progress, 0.0)
        self.assertFalse(res.activation_confirmed)

        # Confirmar activación 2 a los 1.5s (t=4.5s)
        res = self.controller.update(gesture="PALMA", hand_center=(0.6, 0.6), timestamp=4.5)
        self.assertTrue(res.activation_confirmed)
        self.assertEqual(res.progress, 1.0)

    def test_inside_zone_validation(self):
        """
        9. Probar inside_zone=False durante más de 1,5 segundos y confirmar que no se active.
        """
        # Intentar iniciar con inside_zone=False
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0, inside_zone=False)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 0.0)

        # Intentar avanzar t=1.0 con inside_zone=False
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.0, inside_zone=False)
        self.assertFalse(res.is_activating)
        self.assertEqual(res.progress, 0.0)

        # Intentar completar t=1.5 con inside_zone=False
        res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.5, inside_zone=False)
        self.assertFalse(res.activation_confirmed)
        self.assertEqual(res.progress, 0.0)

        # Probar que si desactivamos require_zone=False sí funciona
        controller_no_zone = ActivationController(require_zone=False)
        res = controller_no_zone.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=0.0, inside_zone=False)
        self.assertTrue(res.is_activating)
        res = controller_no_zone.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=1.5, inside_zone=False)
        self.assertTrue(res.activation_confirmed)

    def test_robustness_invalid_inputs(self):
        """
        10. Probar entradas inválidas o incompletas y comprobar que no generen excepciones no controladas.
        """
        # Entrada None en gesto
        try:
            res = self.controller.update(gesture=None, hand_center=(0.5, 0.5), timestamp=0.0)
            self.assertFalse(res.is_activating)
            
            # Entrada None en centro
            res = self.controller.update(gesture="PALMA", hand_center=None, timestamp=0.0)
            self.assertFalse(res.is_activating)

            # Entrada timestamp inválido o None
            res = self.controller.update(gesture="PALMA", hand_center=(0.5, 0.5), timestamp=None)
            # Debe correr de forma segura sin excepciones

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
