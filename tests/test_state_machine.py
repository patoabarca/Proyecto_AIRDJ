import unittest
from src.state_machine import StateMachine, SystemState, StateMachineResult
from src.activation import ActivationResult

class TestStateMachine(unittest.TestCase):
    def setUp(self):
        """
        Inicializa una StateMachine para las pruebas.
        """
        self.state_machine = StateMachine(command_timeout=5.0, cooldown_time=1.5)

    def test_initial_state_locked(self):
        """
        1. Verificar que el estado inicial del sistema sea BLOQUEADO.
        """
        self.assertEqual(self.state_machine.state, SystemState.BLOQUEADO)

    def test_commands_ignored_while_locked(self):
        """
        2. Verificar que los comandos multimedia se ignoren cuando el sistema está bloqueado.
        """
        act_res = ActivationResult(is_activating=False, progress=0.0, activation_confirmed=False, status="IDLE")
        
        # Enviar comando PUÑO estando bloqueado
        res = self.state_machine.update(activation_result=act_res, command="PUÑO", timestamp=0.0)
        
        self.assertEqual(res.state, SystemState.BLOQUEADO)
        self.assertIsNone(res.action)
        self.assertEqual(res.activation_progress, 0.0)
        self.assertEqual(res.time_left, 0.0)

    def test_transition_to_activating(self):
        """
        3. Comprobar la transición a ACTIVANDO basada en la entrada del Módulo 4.
        """
        # Entrada que indica activación en progreso con un 40% de progreso
        act_res = ActivationResult(is_activating=True, progress=0.4, activation_confirmed=False, status="ACTIVATING")
        
        res = self.state_machine.update(activation_result=act_res, command=None, timestamp=0.0)
        
        self.assertEqual(res.state, SystemState.ACTIVANDO)
        self.assertEqual(res.activation_progress, 0.4)
        self.assertEqual(self.state_machine.state, SystemState.ACTIVANDO)

    def test_transition_to_active(self):
        """
        4. Comprobar que transiciona a ACTIVO cuando llega activation_confirmed=True.
        """
        # Transición directa desde bloqueado (o desde activando) al recibir confirmación
        act_res = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=True, status="CONFIRMED")
        
        res = self.state_machine.update(activation_result=act_res, command=None, timestamp=10.0)
        
        self.assertEqual(res.state, SystemState.ACTIVO)
        self.assertTrue(self.state_machine.state == SystemState.ACTIVO)
        self.assertEqual(res.time_left, 5.0)
        self.assertEqual(self.state_machine.active_start_time, 10.0)

    def test_discrete_command_execution(self):
        """
        5. Comprobar que se acepta un único comando discreto, transiciona a EJECUTANDO,
        emite la acción una sola vez, y en el ciclo siguiente pasa a COOLDOWN.
        """
        # 1. Activar
        act_res_confirmed = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=True, status="CONFIRMED")
        self.state_machine.update(activation_result=act_res_confirmed, command=None, timestamp=0.0)
        
        # 2. Enviar comando discreto PUÑO a t=1.0
        act_res_idle = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=False, status="CONFIRMED")
        res_exec = self.state_machine.update(activation_result=act_res_idle, command="PUÑO", timestamp=1.0)
        
        self.assertEqual(res_exec.state, SystemState.EJECUTANDO)
        self.assertEqual(res_exec.action, "PLAY_PAUSA")  # Acción emitida
        self.assertEqual(res_exec.time_left, 0.0)

        # 3. Siguiente ciclo t=1.1 -> Debe transicionar a COOLDOWN
        res_cooldown = self.state_machine.update(activation_result=act_res_idle, command="PUÑO", timestamp=1.1)
        self.assertEqual(res_cooldown.state, SystemState.COOLDOWN)
        self.assertIsNone(res_cooldown.action)  # Ya no se emite la acción
        self.assertEqual(res_cooldown.time_left, 1.5)  # Cooldown time restante

    def test_commands_rejected_during_cooldown(self):
        """
        6. Comprobar que se rechacen comandos y que sean ignorados durante el cooldown.
        """
        # Poner la máquina directamente en estado COOLDOWN a t=0.0
        self.state_machine.state = SystemState.COOLDOWN
        self.state_machine.cooldown_start_time = 0.0
        
        act_res = ActivationResult(is_activating=False, progress=0.0, activation_confirmed=False, status="IDLE")
        
        # Intentar enviar comando PUÑO a t=0.5
        res = self.state_machine.update(activation_result=act_res, command="PUÑO", timestamp=0.5)
        
        self.assertEqual(res.state, SystemState.COOLDOWN)
        self.assertIsNone(res.action)
        self.assertEqual(res.time_left, 1.0)  # Queda 1.0s de cooldown

        # t=1.5 -> Cooldown finaliza, debe volver a BLOQUEADO
        res_end = self.state_machine.update(activation_result=act_res, command=None, timestamp=1.5)
        self.assertEqual(res_end.state, SystemState.BLOQUEADO)

    def test_timeout_after_5_seconds(self):
        """
        7. Comprobar que si pasan los 5 segundos en ACTIVO sin comando,
        vuelve directamente a BLOQUEADO sin pasar por cooldown.
        """
        # Activar a t=0.0
        act_res_confirmed = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=True, status="CONFIRMED")
        self.state_machine.update(activation_result=act_res_confirmed, command=None, timestamp=0.0)
        
        act_res_idle = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=False, status="CONFIRMED")
        
        # t=4.0 -> Sigue activo, faltan 1s
        res = self.state_machine.update(activation_result=act_res_idle, command=None, timestamp=4.0)
        self.assertEqual(res.state, SystemState.ACTIVO)
        self.assertAlmostEqual(res.time_left, 1.0)

        # t=5.0 -> Se cumple el timeout
        res_timeout = self.state_machine.update(activation_result=act_res_idle, command=None, timestamp=5.0)
        self.assertEqual(res_timeout.state, SystemState.BLOQUEADO)
        self.assertEqual(res_timeout.time_left, 0.0)

    def test_new_activation_after_timeout(self):
        """
        8. Comprobar que es posible realizar una nueva activación tras volver a bloqueado.
        """
        # 1. Activar y provocar timeout
        act_res_confirmed = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=True, status="CONFIRMED")
        self.state_machine.update(activation_result=act_res_confirmed, command=None, timestamp=0.0)
        
        act_res_idle = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=False, status="CONFIRMED")
        self.state_machine.update(activation_result=act_res_idle, command=None, timestamp=5.0) # Vuelve a BLOQUEADO
        
        # 2. Iniciar activación de nuevo
        act_res_activating = ActivationResult(is_activating=True, progress=0.2, activation_confirmed=False, status="ACTIVATING")
        res = self.state_machine.update(activation_result=act_res_activating, command=None, timestamp=6.0)
        self.assertEqual(res.state, SystemState.ACTIVANDO)

    def test_reset_from_any_state(self):
        """
        9. Comprobar que reset() limpia todo y transiciona a BLOQUEADO desde cualquier estado.
        """
        # Poner en ACTIVO
        self.state_machine.state = SystemState.ACTIVO
        self.state_machine.active_start_time = 10.0
        self.state_machine.volume_adjusting = True
        
        self.state_machine.reset()
        
        self.assertEqual(self.state_machine.state, SystemState.BLOQUEADO)
        self.assertIsNone(self.state_machine.active_start_time)
        self.assertFalse(self.state_machine.volume_adjusting)
        self.assertEqual(self.state_machine.time_left, 0.0)

    def test_robustness_invalid_inputs(self):
        """
        10. Comprobar entradas None o desconocidas sin lanzar excepciones.
        """
        try:
            # Inputs nulos
            res = self.state_machine.update(activation_result=None, command=None, timestamp=None)
            self.assertEqual(res.state, SystemState.BLOQUEADO)

            # Comandos desconocidos
            self.state_machine.state = SystemState.ACTIVO
            self.state_machine.active_start_time = 0.0
            res = self.state_machine.update(activation_result=None, command="DESCONOCIDO", timestamp=1.0)
            self.assertEqual(res.state, SystemState.ACTIVO)
            
            # Tipos incorrectos
            res = self.state_machine.update(activation_result="invalido", command=123, command_value="mal_valor", timestamp="invalido")
            # Debe procesar de forma segura sin fallar

        except Exception as e:
            self.fail(f" update() arrojó una excepción ante entradas inválidas: {e}")

    def test_time_left_no_negative(self):
        """
        11. Comprobar que time_left nunca tome valores negativos.
        """
        # Activar a t=0.0
        act_res_confirmed = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=True, status="CONFIRMED")
        self.state_machine.update(activation_result=act_res_confirmed, command=None, timestamp=0.0)
        
        # Consultar en t=10.0 (superando los 5s de timeout)
        act_res_idle = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=False, status="CONFIRMED")
        res = self.state_machine.update(activation_result=act_res_idle, command=None, timestamp=10.0)
        
        self.assertEqual(res.state, SystemState.BLOQUEADO)
        self.assertEqual(res.time_left, 0.0)

    def test_continuous_volume_flow(self):
        """
        12. Comprobar el flujo continuo de volumen: múltiples valores continuos
        sin pasar inmediatamente a EJECUTANDO/COOLDOWN, y pase a COOLDOWN
        cuando finalice el gesto de volumen.
        """
        # 1. Activar
        act_res_confirmed = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=True, status="CONFIRMED")
        self.state_machine.update(activation_result=act_res_confirmed, command=None, timestamp=0.0)
        
        act_res_idle = ActivationResult(is_activating=False, progress=1.0, activation_confirmed=False, status="CONFIRMED")
        
        # 2. Iniciar gesto "VOLUMEN" a t=1.0 con volumen 30.0
        res = self.state_machine.update(activation_result=act_res_idle, command="VOLUMEN", command_value=30.0, timestamp=1.0)
        self.assertEqual(res.state, SystemState.ACTIVO)
        self.assertEqual(res.action, "CONTROL_VOLUMEN")
        self.assertEqual(res.volume_value, 30.0)
        self.assertTrue(self.state_machine.volume_adjusting)

        # 3. Continuar gesto "VOLUMEN" a t=2.0 con volumen 45.0
        res = self.state_machine.update(activation_result=act_res_idle, command="VOLUMEN", command_value=45.0, timestamp=2.0)
        self.assertEqual(res.state, SystemState.ACTIVO)
        self.assertEqual(res.action, "CONTROL_VOLUMEN")
        self.assertEqual(res.volume_value, 45.0)
        
        # 4. Finalizar gesto de volumen (command=None) a t=3.0 -> Debe pasar a COOLDOWN
        res = self.state_machine.update(activation_result=act_res_idle, command=None, timestamp=3.0)
        self.assertEqual(res.state, SystemState.COOLDOWN)
        self.assertIsNone(res.action)
        self.assertFalse(self.state_machine.volume_adjusting)
        self.assertEqual(res.time_left, 1.5)

    def test_consumes_module4_outputs(self):
        """
        13. Confirmar que el Módulo 7 consume la salida del Módulo 4
        y no duplica su lógica interna (timers de 1.5s ni estabilidad).
        """
        # Comprobar que StateMachine interactúa directamente con objetos de tipo ActivationResult
        act_res = ActivationResult(is_activating=True, progress=0.75, activation_confirmed=False, status="ACTIVATING")
        res = self.state_machine.update(activation_result=act_res, command=None, timestamp=0.0)
        
        self.assertEqual(res.state, SystemState.ACTIVANDO)
        self.assertEqual(res.activation_progress, 0.75)

if __name__ == '__main__':
    unittest.main()
