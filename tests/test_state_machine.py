"""
Pruebas unitarias para el Módulo 7 (StateMachine).

Estas pruebas son completamente independientes:
- No requieren webcam
- No requieren MediaPipe
- No modifican el sistema operativo
- No ejecutan comandos multimedia reales

Se simulan timestamps y eventos para validar toda la lógica.
"""

import unittest
import time
from src.state_machine import StateMachine, SystemState, StateMachineResult
from src.activation import ActivationResult


class TestStateMachineBasics(unittest.TestCase):
    """Pruebas básicas de la máquina de estados."""

    def setUp(self):
        """Inicializa la máquina antes de cada prueba."""
        self.sm = StateMachine(command_timeout=5.0, cooldown_time=1.5)
        self.base_time = 1000.0  # Timestamp simulado en segundos

    def test_initial_state_is_bloqueado(self):
        """Verifica que el estado inicial sea BLOQUEADO."""
        result = self.sm.update(
            activation_result=None,
            command=None,
            timestamp=self.base_time
        )
        self.assertEqual(result.state, SystemState.BLOQUEADO)
        self.assertIsNone(result.action)
        self.assertEqual(result.activation_progress, 0.0)

    def test_commands_ignored_when_bloqueado(self):
        """Verifica que los comandos sean ignorados en estado BLOQUEADO."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=0.0,
            activation_confirmed=False,
            status="IDLE"
        )
        result = self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time
        )
        self.assertEqual(result.state, SystemState.BLOQUEADO)
        self.assertIsNone(result.action)

    def test_transition_to_activando_on_activation_progress(self):
        """Verifica transición a ACTIVANDO cuando hay progreso de activación."""
        activation_result = ActivationResult(
            is_activating=True,
            progress=0.5,
            activation_confirmed=False,
            status="ACTIVATING"
        )
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.assertEqual(result.state, SystemState.ACTIVANDO)
        self.assertEqual(result.activation_progress, 0.5)

    def test_transition_to_activo_on_activation_confirmed(self):
        """Verifica transición a ACTIVO cuando se confirma activación."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.assertEqual(result.state, SystemState.ACTIVO)
        self.assertGreater(result.time_left, 0.0)  # Timeout debe ser > 0

    def test_command_timeout_window(self):
        """Verifica que la ventana de comandos sea de 5 segundos."""
        # Activar sistema
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Verificar time_left al inicio
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.assertAlmostEqual(result.time_left, 5.0, delta=0.1)

    def test_single_discrete_command_execution(self):
        """Verifica que un comando discreto se ejecute exactamente una vez."""
        # Activar
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Enviar comando PUÑO
        result = self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time
        )
        self.assertEqual(result.state, SystemState.EJECUTANDO)
        self.assertEqual(result.action, "PLAY_PAUSA")

    def test_transition_ejecutando_to_cooldown(self):
        """Verifica que EJECUTANDO pase a COOLDOWN en el siguiente frame."""
        # Activar y enviar comando
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time
        )
        # Siguiente frame: debe estar en COOLDOWN
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 0.01
        )
        self.assertEqual(result.state, SystemState.COOLDOWN)
        self.assertIsNone(result.action)

    def test_commands_ignored_during_cooldown(self):
        """Verifica que los comandos sean ignorados durante COOLDOWN."""
        # Activar, ejecutar comando y entrar en cooldown
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 0.01
        )
        # Intentar enviar otro comando durante cooldown
        result = self.sm.update(
            activation_result=activation_result,
            command="SWIPE_DERECHA",
            timestamp=self.base_time + 0.5
        )
        self.assertEqual(result.state, SystemState.COOLDOWN)
        self.assertIsNone(result.action)

    def test_automatic_return_to_bloqueado_after_cooldown(self):
        """Verifica retorno automático a BLOQUEADO al finalizar cooldown."""
        # Ejecutar ciclo completo: activar → comando → cooldown → bloqueado
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 0.01
        )
        # Pasar tiempo de cooldown (1.5 segundos)
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 1.6
        )
        self.assertEqual(result.state, SystemState.BLOQUEADO)

    def test_timeout_without_command(self):
        """Verifica que timeout sin comando regrese a BLOQUEADO."""
        # Activar
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Esperar 5+ segundos sin enviar comando
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 5.1
        )
        self.assertEqual(result.state, SystemState.BLOQUEADO)
        self.assertIsNone(result.action)


class TestStateMachineSwipeGestures(unittest.TestCase):
    """Pruebas de gestos discretos (swipes)."""

    def setUp(self):
        self.sm = StateMachine()
        self.base_time = 1000.0

    def test_swipe_right_maps_to_siguiente(self):
        """Verifica que SWIPE_DERECHA mapee a SIGUIENTE."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        result = self.sm.update(
            activation_result=activation_result,
            command="SWIPE_DERECHA",
            timestamp=self.base_time
        )
        self.assertEqual(result.action, "SIGUIENTE")

    def test_swipe_left_maps_to_anterior(self):
        """Verifica que SWIPE_IZQUIERDA mapee a ANTERIOR."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        result = self.sm.update(
            activation_result=activation_result,
            command="SWIPE_IZQUIERDA",
            timestamp=self.base_time
        )
        self.assertEqual(result.action, "ANTERIOR")

    def test_index_gesture_maps_to_accion_adicional(self):
        """Verifica que INDICE mapee a ACCION_ADICIONAL."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        result = self.sm.update(
            activation_result=activation_result,
            command="INDICE",
            timestamp=self.base_time
        )
        self.assertEqual(result.action, "ACCION_ADICIONAL")

    def test_swipe_return_without_duplicate_execution(self):
        """Verifica que retorno de swipe no genere ejecuciones duplicadas."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Enviar swipe
        self.sm.update(
            activation_result=activation_result,
            command="SWIPE_DERECHA",
            timestamp=self.base_time
        )
        # Sistema pasa a cooldown
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 0.01
        )
        # Intentar enviar el mismo swipe nuevamente (usuario hace retorno)
        result = self.sm.update(
            activation_result=activation_result,
            command="SWIPE_DERECHA",
            timestamp=self.base_time + 0.5
        )
        # Debe estar en cooldown sin acción
        self.assertEqual(result.state, SystemState.COOLDOWN)
        self.assertIsNone(result.action)


class TestStateMachineContinuousVolume(unittest.TestCase):
    """Pruebas de control continuo de volumen."""

    def setUp(self):
        self.sm = StateMachine()
        self.base_time = 1000.0

    def test_volume_session_begins(self):
        """Verifica que una sesión de volumen pueda iniciarse."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        result = self.sm.update(
            activation_result=activation_result,
            command="VOLUMEN",
            command_value=50.0,
            timestamp=self.base_time
        )
        self.assertEqual(result.state, SystemState.ACTIVO)
        self.assertEqual(result.action, "CONTROL_VOLUMEN")
        self.assertEqual(result.volume_value, 50.0)

    def test_multiple_continuous_volume_values(self):
        """Verifica múltiples valores continuos de volumen en una sesión."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Inicio sesión volumen
        self.sm.update(
            activation_result=activation_result,
            command="VOLUMEN",
            command_value=30.0,
            timestamp=self.base_time
        )
        # Múltiples valores consecutivos
        for value in [40.0, 50.0, 60.0, 70.0]:
            result = self.sm.update(
                activation_result=activation_result,
                command="VOLUMEN",
                command_value=value,
                timestamp=self.base_time + 0.1
            )
            self.assertEqual(result.state, SystemState.ACTIVO)
            self.assertEqual(result.volume_value, value)
            self.assertEqual(result.action, "CONTROL_VOLUMEN")

    def test_volume_does_not_generate_discrete_commands(self):
        """Verifica que volumen no genere comandos discretos duplicados."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            command="VOLUMEN",
            command_value=50.0,
            timestamp=self.base_time
        )
        # Enviar múltiples valores: no debe haber transición a EJECUTANDO
        for _ in range(5):
            result = self.sm.update(
                activation_result=activation_result,
                command="VOLUMEN",
                command_value=50.0,
                timestamp=self.base_time + 0.1
            )
            self.assertNotEqual(result.state, SystemState.EJECUTANDO)

    def test_volume_gesture_end_triggers_cooldown(self):
        """Verifica que fin del gesto de volumen cause transición a COOLDOWN."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Iniciar volumen
        self.sm.update(
            activation_result=activation_result,
            command="VOLUMEN",
            command_value=50.0,
            timestamp=self.base_time
        )
        # Gesto termina (comando cambia)
        result = self.sm.update(
            activation_result=activation_result,
            command="PUÑO",  # Gesto diferente
            timestamp=self.base_time + 0.1
        )
        self.assertEqual(result.state, SystemState.COOLDOWN)

    def test_timeout_does_not_restart_during_volume_session(self):
        """Verifica que timeout de 5s no se reinicie en cada frame de volumen."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Iniciar volumen
        self.sm.update(
            activation_result=activation_result,
            command="VOLUMEN",
            command_value=50.0,
            timestamp=self.base_time
        )
        # Verificar time_left después de varios frames de volumen
        result = self.sm.update(
            activation_result=activation_result,
            command="VOLUMEN",
            command_value=50.0,
            timestamp=self.base_time + 0.5
        )
        # El time_left debe seguir siendo aproximadamente 5 segundos
        # (no reiniciado por cada frame)
        self.assertGreater(result.time_left, 4.0)


class TestStateMachineInputValidation(unittest.TestCase):
    """Pruebas de validación robusta de entradas."""

    def setUp(self):
        self.sm = StateMachine()
        self.base_time = 1000.0

    def test_none_timestamp_uses_system_time(self):
        """Verifica que timestamp None se reemplace con time.monotonic()."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=0.0,
            activation_confirmed=False,
            status="IDLE"
        )
        # Debe no lanzar excepción
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=None
        )
        self.assertIsNotNone(result)

    def test_none_activation_result_creates_idle_state(self):
        """Verifica que ActivationResult None se maneje como estado IDLE."""
        result = self.sm.update(
            activation_result=None,
            timestamp=self.base_time
        )
        self.assertEqual(result.state, SystemState.BLOQUEADO)
        self.assertIsNone(result.action)

    def test_unknown_command_ignored(self):
        """Verifica que comando desconocido sea ignorado de forma segura."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        result = self.sm.update(
            activation_result=activation_result,
            command="COMANDO_INVENTADO",
            timestamp=self.base_time
        )
        # Debe permanecer en ACTIVO sin ejecutar nada
        self.assertEqual(result.state, SystemState.ACTIVO)
        self.assertIsNone(result.action)

    def test_invalid_command_value_handled(self):
        """Verifica que valores inválidos de comando se saniticen."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Valor NaN
        result = self.sm.update(
            activation_result=activation_result,
            command="VOLUMEN",
            command_value=float('nan'),
            timestamp=self.base_time
        )
        self.assertIsNone(result.volume_value)

    def test_time_left_never_negative(self):
        """Verifica que time_left nunca sea negativo."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Pasar mucho tiempo
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 100.0
        )
        self.assertGreaterEqual(result.time_left, 0.0)


class TestStateMachineReset(unittest.TestCase):
    """Pruebas de reset desde cualquier estado."""

    def setUp(self):
        self.sm = StateMachine()
        self.base_time = 1000.0

    def test_reset_from_bloqueado(self):
        """Verifica reset desde BLOQUEADO."""
        self.sm.reset()
        self.assertEqual(self.sm.state, SystemState.BLOQUEADO)

    def test_reset_from_activo(self):
        """Verifica reset desde ACTIVO limpia todos los timers."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.assertEqual(self.sm.state, SystemState.ACTIVO)
        
        self.sm.reset()
        
        self.assertEqual(self.sm.state, SystemState.BLOQUEADO)
        self.assertIsNone(self.sm.active_start_time)
        self.assertFalse(self.sm.volume_adjusting)

    def test_reset_from_cooldown(self):
        """Verifica reset desde COOLDOWN."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 0.01
        )
        self.assertEqual(self.sm.state, SystemState.COOLDOWN)
        
        self.sm.reset()
        
        self.assertEqual(self.sm.state, SystemState.BLOQUEADO)
        self.assertIsNone(self.sm.cooldown_start_time)

    def test_new_activation_after_reset(self):
        """Verifica que pueda activarse nuevamente después de reset."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        # Primera activación
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.sm.reset()
        
        # Segunda activación después de reset
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 10.0
        )
        self.assertEqual(result.state, SystemState.ACTIVO)

    def test_gesture_maintained_without_duplicate_execution(self):
        """Verifica que mantener gesto no cause ejecuciones duplicadas."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        # Enviar gesto
        result1 = self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time
        )
        self.assertEqual(result1.state, SystemState.EJECUTANDO)
        
        # Mantener gesto (comando sigue siendo PUÑO)
        result2 = self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time + 0.01
        )
        # Sistema debe estar en COOLDOWN, no en EJECUTANDO nuevamente
        self.assertEqual(result2.state, SystemState.COOLDOWN)

    def test_new_activation_after_cooldown(self):
        """Verifica que se pueda activar nuevamente después de cooldown."""
        activation_result = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        # Ciclo completo
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            command="PUÑO",
            timestamp=self.base_time
        )
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 0.01
        )
        # Pasar cooldown
        self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 1.6
        )
        self.assertEqual(self.sm.state, SystemState.BLOQUEADO)
        
        # Activación debe ser posible nuevamente
        # (pero el usuario necesita hacer palm activation de nuevo)
        result = self.sm.update(
            activation_result=activation_result,
            timestamp=self.base_time + 10.0
        )
        self.assertEqual(result.state, SystemState.ACTIVO)


class TestStateMachineActivationCancellation(unittest.TestCase):
    """Pruebas de cancelación de activación."""

    def setUp(self):
        self.sm = StateMachine()
        self.base_time = 1000.0

    def test_activation_cancelled_goes_back_to_bloqueado(self):
        """Verifica que cancelación de activación regrese a BLOQUEADO."""
        # Iniciar activación
        activation_activating = ActivationResult(
            is_activating=True,
            progress=0.5,
            activation_confirmed=False,
            status="ACTIVATING"
        )
        self.sm.update(
            activation_result=activation_activating,
            timestamp=self.base_time
        )
        self.assertEqual(self.sm.state, SystemState.ACTIVANDO)
        
        # Cancelar activación
        activation_cancelled = ActivationResult(
            is_activating=False,
            progress=0.0,
            activation_confirmed=False,
            status="CANCELLED"
        )
        result = self.sm.update(
            activation_result=activation_cancelled,
            timestamp=self.base_time + 0.1
        )
        self.assertEqual(result.state, SystemState.BLOQUEADO)

    def test_activation_continues_correctly(self):
        """Verifica que activación continúe correctamente si no es cancelada."""
        # Primera actualización: progreso 50%
        activation_activating = ActivationResult(
            is_activating=True,
            progress=0.5,
            activation_confirmed=False,
            status="ACTIVATING"
        )
        result1 = self.sm.update(
            activation_result=activation_activating,
            timestamp=self.base_time
        )
        self.assertEqual(result1.activation_progress, 0.5)
        
        # Segunda actualización: progreso 75%
        activation_continuing = ActivationResult(
            is_activating=True,
            progress=0.75,
            activation_confirmed=False,
            status="ACTIVATING"
        )
        result2 = self.sm.update(
            activation_result=activation_continuing,
            timestamp=self.base_time + 0.1
        )
        self.assertEqual(result2.activation_progress, 0.75)
        self.assertEqual(result2.state, SystemState.ACTIVANDO)

    def test_confirmed_activation_from_activando_state(self):
        """Verifica transición correcta de ACTIVANDO a ACTIVO."""
        # Iniciar activación
        activation_activating = ActivationResult(
            is_activating=True,
            progress=0.8,
            activation_confirmed=False,
            status="ACTIVATING"
        )
        self.sm.update(
            activation_result=activation_activating,
            timestamp=self.base_time
        )
        
        # Confirmar activación
        activation_confirmed = ActivationResult(
            is_activating=False,
            progress=1.0,
            activation_confirmed=True,
            status="CONFIRMED"
        )
        result = self.sm.update(
            activation_result=activation_confirmed,
            timestamp=self.base_time + 0.1
        )
        self.assertEqual(result.state, SystemState.ACTIVO)
        self.assertEqual(result.activation_progress, 1.0)


if __name__ == "__main__":
    unittest.main()
