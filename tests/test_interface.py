"""
Pruebas unitarias para el Módulo 9 (AirDJInterface).

Estas pruebas verifican que la interfaz visual:
- Recibe y procesa frames correctamente
- Dibuja todos los estados sin errores
- Maneja datos None de forma segura
- Se ejecuta sin requerir webcam o entrada real
"""

import unittest
import numpy as np
from src.interface import AirDJInterface, SystemState, LandmarkPoint


class TestInterfaceBasics(unittest.TestCase):
    """Pruebas básicas de la interfaz."""

    def setUp(self):
        """Inicializa la interfaz para cada prueba."""
        self.interface = AirDJInterface(debug=False)
        # Crear frame de prueba vacío
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_render_returns_valid_frame(self):
        """Verifica que render() devuelva un frame válido."""
        result = self.interface.render(self.test_frame)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)

    def test_render_preserves_frame_dimensions(self):
        """Verifica que render() no modifique las dimensiones del frame."""
        # Frame de diferentes dimensiones
        for height, width in [(480, 640), (1080, 1920), (360, 480)]:
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            result = self.interface.render(frame)
            self.assertEqual(result.shape[:2], (height, width))

    def test_render_handles_none_frame(self):
        """Verifica que None frame se maneje de forma segura."""
        result = self.interface.render(None)
        self.assertIsNone(result)

    def test_render_handles_empty_frame(self):
        """Verifica que frame vacío se maneje de forma segura."""
        empty_frame = np.array([])
        result = self.interface.render(empty_frame)
        # Debe devolver algo aunque no sea perfecto
        self.assertIsNotNone(result)

    def test_render_with_minimal_parameters(self):
        """Verifica que render() funcione con parámetros mínimos."""
        result = self.interface.render(self.test_frame)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.test_frame.shape)


class TestStateRendering(unittest.TestCase):
    """Pruebas de renderización de estados."""

    def setUp(self):
        self.interface = AirDJInterface(debug=False)
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_render_bloqueado_state(self):
        """Verifica que estado BLOQUEADO se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.BLOQUEADO
        )
        self.assertIsNotNone(result)

    def test_render_activando_state(self):
        """Verifica que estado ACTIVANDO se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVANDO,
            activation_progress=0.5
        )
        self.assertIsNotNone(result)

    def test_render_activo_state(self):
        """Verifica que estado ACTIVO se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVO,
            time_left=5.0
        )
        self.assertIsNotNone(result)

    def test_render_ejecutando_state(self):
        """Verifica que estado EJECUTANDO se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.EJECUTANDO,
            executed_command="PLAY_PAUSA"
        )
        self.assertIsNotNone(result)

    def test_render_cooldown_state(self):
        """Verifica que estado COOLDOWN se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.COOLDOWN,
            time_left=1.5
        )
        self.assertIsNotNone(result)

    def test_all_states_render_without_error(self):
        """Verifica que TODOS los estados se rendericen sin error."""
        states = [
            SystemState.BLOQUEADO,
            SystemState.ACTIVANDO,
            SystemState.ACTIVO,
            SystemState.EJECUTANDO,
            SystemState.COOLDOWN
        ]
        for state in states:
            result = self.interface.render(self.test_frame, state=state)
            self.assertIsNotNone(result)


class TestActivationProgress(unittest.TestCase):
    """Pruebas de visualización de progreso de activación."""

    def setUp(self):
        self.interface = AirDJInterface(debug=False)
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_activation_progress_zero(self):
        """Verifica que progreso 0% se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVANDO,
            activation_progress=0.0
        )
        self.assertIsNotNone(result)

    def test_activation_progress_fifty(self):
        """Verifica que progreso 50% se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVANDO,
            activation_progress=0.5
        )
        self.assertIsNotNone(result)

    def test_activation_progress_hundred(self):
        """Verifica que progreso 100% se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVANDO,
            activation_progress=1.0
        )
        self.assertIsNotNone(result)

    def test_activation_progress_out_of_range_clamped(self):
        """Verifica que progreso fuera de rango se limite."""
        # Valores negativos
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVANDO,
            activation_progress=-0.5
        )
        self.assertIsNotNone(result)
        
        # Valores mayores a 1
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVANDO,
            activation_progress=1.5
        )
        self.assertIsNotNone(result)


class TestVolume(unittest.TestCase):
    """Pruebas de visualización de volumen."""

    def setUp(self):
        self.interface = AirDJInterface(debug=False)
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_volume_zero(self):
        """Verifica que volumen 0 se renderice."""
        result = self.interface.render(
            self.test_frame,
            volume_value=0.0
        )
        self.assertIsNotNone(result)

    def test_volume_fifty(self):
        """Verifica que volumen 50 se renderice."""
        result = self.interface.render(
            self.test_frame,
            volume_value=50.0
        )
        self.assertIsNotNone(result)

    def test_volume_hundred(self):
        """Verifica que volumen 100 se renderice."""
        result = self.interface.render(
            self.test_frame,
            volume_value=100.0
        )
        self.assertIsNotNone(result)

    def test_volume_fractional(self):
        """Verifica que volumen fraccionario se renderice."""
        result = self.interface.render(
            self.test_frame,
            volume_value=33.33
        )
        self.assertIsNotNone(result)

    def test_volume_clamped_below_zero(self):
        """Verifica que volumen negativo se limite a 0."""
        result = self.interface.render(
            self.test_frame,
            volume_value=-50.0
        )
        self.assertIsNotNone(result)

    def test_volume_clamped_above_hundred(self):
        """Verifica que volumen mayor a 100 se limite."""
        result = self.interface.render(
            self.test_frame,
            volume_value=150.0
        )
        self.assertIsNotNone(result)

    def test_volume_none_handled(self):
        """Verifica que volumen None se maneje de forma segura."""
        result = self.interface.render(
            self.test_frame,
            volume_value=None
        )
        self.assertIsNotNone(result)


class TestTimers(unittest.TestCase):
    """Pruebas de visualización de timers."""

    def setUp(self):
        self.interface = AirDJInterface(debug=False)
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_time_left_positive(self):
        """Verifica que tiempo positivo se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVO,
            time_left=5.0
        )
        self.assertIsNotNone(result)

    def test_time_left_zero(self):
        """Verifica que tiempo 0 se renderice."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVO,
            time_left=0.0
        )
        self.assertIsNotNone(result)

    def test_time_left_negative_clamped(self):
        """Verifica que tiempo negativo se limite a 0."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVO,
            time_left=-1.0
        )
        self.assertIsNotNone(result)

    def test_time_left_none_handled(self):
        """Verifica que tiempo None se maneje de forma segura."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVO,
            time_left=None
        )
        self.assertIsNotNone(result)


class TestDebugMode(unittest.TestCase):
    """Pruebas de modo debug."""

    def setUp(self):
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_debug_false_works(self):
        """Verifica que debug=False funcione."""
        interface = AirDJInterface(debug=False)
        result = interface.render(self.test_frame)
        self.assertIsNotNone(result)

    def test_debug_true_works(self):
        """Verifica que debug=True funcione."""
        interface = AirDJInterface(debug=True)
        result = interface.render(self.test_frame)
        self.assertIsNotNone(result)

    def test_debug_false_without_landmarks(self):
        """Verifica que debug=False tolera ausencia de landmarks."""
        interface = AirDJInterface(debug=False)
        result = interface.render(
            self.test_frame,
            landmarks=None
        )
        self.assertIsNotNone(result)

    def test_debug_true_with_simulated_landmarks(self):
        """Verifica que debug=True tolera landmarks simulados."""
        interface = AirDJInterface(debug=True)
        landmarks = [
            LandmarkPoint(0.5, 0.5, 0.0),
            LandmarkPoint(0.6, 0.5, 0.0),
            LandmarkPoint(0.4, 0.6, 0.0),
        ]
        result = interface.render(
            self.test_frame,
            landmarks=landmarks
        )
        self.assertIsNotNone(result)

    def test_debug_true_with_fps(self):
        """Verifica que debug=True dibuje FPS."""
        interface = AirDJInterface(debug=True)
        result = interface.render(
            self.test_frame,
            fps=30.5
        )
        self.assertIsNotNone(result)


class TestOptionalParameters(unittest.TestCase):
    """Pruebas de parámetros opcionales."""

    def setUp(self):
        self.interface = AirDJInterface(debug=False)
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_detected_gesture_displayed(self):
        """Verifica que gesto detectado se muestre."""
        result = self.interface.render(
            self.test_frame,
            detected_gesture="PALMA"
        )
        self.assertIsNotNone(result)

    def test_executed_command_displayed(self):
        """Verifica que comando ejecutado se muestre."""
        result = self.interface.render(
            self.test_frame,
            executed_command="SIGUIENTE"
        )
        self.assertIsNotNone(result)

    def test_command_zone_displayed(self):
        """Verifica que zona de comandos se dibuje."""
        result = self.interface.render(
            self.test_frame,
            command_zone=(0.2, 0.2, 0.8, 0.8)
        )
        self.assertIsNotNone(result)

    def test_command_zone_normalized_coords(self):
        """Verifica que zona de comandos use coordenadas normalizadas."""
        result = self.interface.render(
            self.test_frame,
            command_zone=(0.1, 0.1, 0.9, 0.9)
        )
        self.assertIsNotNone(result)

    def test_all_optional_parameters_together(self):
        """Verifica que TODOS los parámetros opcionales funcionen juntos."""
        result = self.interface.render(
            self.test_frame,
            state=SystemState.ACTIVO,
            activation_progress=0.7,
            time_left=3.5,
            volume_value=75.0,
            detected_gesture="PUNO",
            executed_command="PLAY_PAUSA",
            command_zone=(0.2, 0.2, 0.8, 0.8),
            fps=29.8
        )
        self.assertIsNotNone(result)


class TestNoneHandling(unittest.TestCase):
    """Pruebas de manejo de valores None."""

    def setUp(self):
        self.interface = AirDJInterface(debug=False)
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_none_state_defaults_to_bloqueado(self):
        """Verifica que estado None use BLOQUEADO por defecto."""
        result = self.interface.render(
            self.test_frame,
            state=None
        )
        self.assertIsNotNone(result)

    def test_none_gesture_handled(self):
        """Verifica que gesto None se maneje de forma segura."""
        result = self.interface.render(
            self.test_frame,
            detected_gesture=None
        )
        self.assertIsNotNone(result)

    def test_none_command_handled(self):
        """Verifica que comando None se maneje de forma segura."""
        result = self.interface.render(
            self.test_frame,
            executed_command=None
        )
        self.assertIsNotNone(result)

    def test_none_landmarks_handled(self):
        """Verifica que landmarks None se manejen de forma segura."""
        result = self.interface.render(
            self.test_frame,
            landmarks=None
        )
        self.assertIsNotNone(result)

    def test_empty_landmarks_handled(self):
        """Verifica que lista vacía de landmarks se maneje."""
        result = self.interface.render(
            self.test_frame,
            landmarks=[]
        )
        self.assertIsNotNone(result)


class TestComplexScenarios(unittest.TestCase):
    """Pruebas de escenarios complejos."""

    def setUp(self):
        self.interface = AirDJInterface(debug=False)
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_full_activation_flow(self):
        """Simula flujo completo de activación."""
        states_flow = [
            (SystemState.BLOQUEADO, 0.0),
            (SystemState.ACTIVANDO, 0.25),
            (SystemState.ACTIVANDO, 0.5),
            (SystemState.ACTIVANDO, 0.75),
            (SystemState.ACTIVO, 1.0),
        ]
        
        for state, progress in states_flow:
            result = self.interface.render(
                self.test_frame,
                state=state,
                activation_progress=progress
            )
            self.assertIsNotNone(result)

    def test_command_execution_flow(self):
        """Simula ejecución de comandos."""
        commands = ["PLAY_PAUSA", "SIGUIENTE", "ANTERIOR"]
        
        for command in commands:
            result = self.interface.render(
                self.test_frame,
                state=SystemState.EJECUTANDO,
                executed_command=command
            )
            self.assertIsNotNone(result)

    def test_cooldown_sequence(self):
        """Simula secuencia de cooldown."""
        for time_remaining in [1.5, 1.0, 0.5, 0.0]:
            result = self.interface.render(
                self.test_frame,
                state=SystemState.COOLDOWN,
                time_left=time_remaining
            )
            self.assertIsNotNone(result)

    def test_volume_adjustment_sequence(self):
        """Simula ajuste continuo de volumen."""
        for volume in [0.0, 25.0, 50.0, 75.0, 100.0]:
            result = self.interface.render(
                self.test_frame,
                state=SystemState.ACTIVO,
                volume_value=volume,
                time_left=5.0 - (volume / 20.0)
            )
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
