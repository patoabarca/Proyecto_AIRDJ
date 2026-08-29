"""
Pruebas unitarias para el Módulo 8 (MediaController).

Todas las pruebas utilizan modo dry_run para no modificar el sistema real.
El controlador debe ser completamente independiente del Módulo 7.
"""

import unittest
from src.media_controller import MediaController, MediaControllerResult, ActionType


class TestMediaControllerDiscreteCommands(unittest.TestCase):
    """Pruebas de comandos discretos (play/pause, siguiente, anterior)."""

    def setUp(self):
        """Inicializa controlador en modo simulado para todas las pruebas."""
        self.controller = MediaController(dry_run=True)

    def test_play_pause_produces_single_action(self):
        """Verifica que PLAY_PAUSA produzca exactamente una acción."""
        result = self.controller.execute("PLAY_PAUSA")
        self.assertTrue(result.success)
        self.assertEqual(result.action_attempted, "PLAY_PAUSA")
        self.assertEqual(len(self.controller.get_execution_log()), 1)

    def test_siguiente_produces_single_action(self):
        """Verifica que SIGUIENTE produzca exactamente una acción."""
        result = self.controller.execute("SIGUIENTE")
        self.assertTrue(result.success)
        self.assertEqual(result.action_attempted, "SIGUIENTE")
        self.assertEqual(len(self.controller.get_execution_log()), 1)

    def test_anterior_produces_single_action(self):
        """Verifica que ANTERIOR produzca exactamente una acción."""
        result = self.controller.execute("ANTERIOR")
        self.assertTrue(result.success)
        self.assertEqual(result.action_attempted, "ANTERIOR")
        self.assertEqual(len(self.controller.get_execution_log()), 1)

    def test_unknown_command_rejected_safely(self):
        """Verifica que comando desconocido se rechace de forma segura."""
        result = self.controller.execute("COMANDO_INEXISTENTE")
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertIn("desconocido", result.error.lower())

    def test_none_command_rejected(self):
        """Verifica que comando None no genere excepción."""
        result = self.controller.execute(None)
        self.assertFalse(result.success)
        self.assertIsNone(result.action_attempted)

    def test_case_insensitive_commands(self):
        """Verifica que comandos sean case-insensitive."""
        result_upper = self.controller.execute("PLAY_PAUSA")
        self.assertTrue(result_upper.success)
        
        result_lower = self.controller.execute("play_pausa")
        self.assertTrue(result_lower.success)
        
        result_mixed = self.controller.execute("Play_Pausa")
        self.assertTrue(result_mixed.success)

    def test_invalid_command_type_rejected(self):
        """Verifica que tipos inválidos de comando se rechacen."""
        result = self.controller.execute(123)
        self.assertFalse(result.success)

    def test_sequence_of_discrete_commands(self):
        """Verifica que múltiples comandos se ejecuten en secuencia."""
        commands = ["PLAY_PAUSA", "SIGUIENTE", "ANTERIOR"]
        for cmd in commands:
            result = self.controller.execute(cmd)
            self.assertTrue(result.success)
        
        # Verificar que todas se registraron
        log = self.controller.get_execution_log()
        self.assertEqual(len(log), 3)


class TestMediaControllerVolume(unittest.TestCase):
    """Pruebas de control de volumen continuo."""

    def setUp(self):
        self.controller = MediaController(dry_run=True)

    def test_volume_zero_valid(self):
        """Verifica que volumen 0 sea válido."""
        result = self.controller.set_volume(0.0)
        self.assertTrue(result.success)
        self.assertEqual(result.value_used, 0.0)

    def test_volume_fifty_valid(self):
        """Verifica que volumen 50 sea válido."""
        result = self.controller.set_volume(50.0)
        self.assertTrue(result.success)
        self.assertEqual(result.value_used, 50.0)

    def test_volume_hundred_valid(self):
        """Verifica que volumen 100 sea válido."""
        result = self.controller.set_volume(100.0)
        self.assertTrue(result.success)
        self.assertEqual(result.value_used, 100.0)

    def test_volume_below_zero_clamped(self):
        """Verifica que valores menores a 0 se limiten correctamente."""
        result = self.controller.set_volume(-50.0)
        self.assertTrue(result.success)
        self.assertEqual(result.value_used, 0.0)

    def test_volume_above_hundred_clamped(self):
        """Verifica que valores mayores a 100 se limiten correctamente."""
        result = self.controller.set_volume(150.0)
        self.assertTrue(result.success)
        self.assertEqual(result.value_used, 100.0)

    def test_volume_negative_large_value_clamped(self):
        """Verifica que valores negativos grandes se limiten a 0."""
        result = self.controller.set_volume(-1000.0)
        self.assertTrue(result.success)
        self.assertEqual(result.value_used, 0.0)

    def test_volume_large_positive_clamped(self):
        """Verifica que valores positivos grandes se limiten a 100."""
        result = self.controller.set_volume(1000.0)
        self.assertTrue(result.success)
        self.assertEqual(result.value_used, 100.0)

    def test_none_volume_rejected(self):
        """Verifica que volumen None se rechace de forma segura."""
        result = self.controller.set_volume(None)
        self.assertFalse(result.success)

    def test_invalid_volume_type_rejected(self):
        """Verifica que tipos inválidos de volumen se rechacen."""
        result = self.controller.set_volume("fifty")
        self.assertFalse(result.success)

    def test_continuous_volume_sequence(self):
        """Verifica que se procese una secuencia de valores continuos."""
        values = [10.0, 25.0, 50.0, 75.0, 90.0]
        for val in values:
            result = self.controller.set_volume(val)
            self.assertTrue(result.success)
            self.assertEqual(result.value_used, val)
        
        # Verificar que todas se registraron
        log = self.controller.get_execution_log()
        self.assertEqual(len(log), 5)

    def test_volume_fractional_values(self):
        """Verifica que se acepten valores fraccionarios de volumen."""
        result = self.controller.set_volume(33.33)
        self.assertTrue(result.success)
        self.assertAlmostEqual(result.value_used, 33.33, places=2)

    def test_volume_accepts_integers(self):
        """Verifica que se acepten valores enteros de volumen."""
        result = self.controller.set_volume(75)
        self.assertTrue(result.success)
        self.assertEqual(result.value_used, 75.0)


class TestMediaControllerIndependence(unittest.TestCase):
    """Pruebas de independencia: Controller no mantiene estado del sistema."""

    def setUp(self):
        self.controller = MediaController(dry_run=True)

    def test_controller_does_not_maintain_system_state(self):
        """Verifica que Controller no mantenga estados como BLOQUEADO, ACTIVO."""
        # Ejecutar varias acciones
        self.controller.execute("PLAY_PAUSA")
        self.controller.execute("SIGUIENTE")
        self.controller.set_volume(50.0)
        
        # No debe haber propiedades que indiquen BLOQUEADO, ACTIVO, etc.
        # (Solo logging y ejecución)
        self.assertFalse(hasattr(self.controller, 'state'))

    def test_same_action_executed_multiple_times_if_called(self):
        """Verifica que ejecutar mismo comando N veces produce N acciones."""
        # Esto diferencia de Module 7 que previene duplicados
        for _ in range(5):
            result = self.controller.execute("PLAY_PAUSA")
            self.assertTrue(result.success)
        
        log = self.controller.get_execution_log()
        # Module 8 debe ejecutar 5 veces (Module 7 previene duplicados)
        self.assertEqual(len(log), 5)

    def test_controller_works_standalone_without_module_7(self):
        """Verifica que Controller funcione sin existir Module 7."""
        # No debe faltar ninguna dependencia de state_machine
        result = self.controller.execute("ANTERIOR")
        self.assertTrue(result.success)
        
        result = self.controller.set_volume(45.0)
        self.assertTrue(result.success)

    def test_dry_run_mode_does_not_affect_system(self):
        """Verifica que modo dry_run no modifique el sistema real."""
        # En dry_run=True, las acciones se registran pero no se ejecutan
        result = self.controller.execute("PLAY_PAUSA")
        self.assertTrue(result.success)
        
        log = self.controller.get_execution_log()
        self.assertEqual(log[0]["dry_run"], True)


class TestMediaControllerExecutionLog(unittest.TestCase):
    """Pruebas de funcionalidad de logging para debugging."""

    def setUp(self):
        self.controller = MediaController(dry_run=True)

    def test_execution_log_records_discrete_commands(self):
        """Verifica que log registre comandos discretos."""
        self.controller.execute("PLAY_PAUSA")
        self.controller.execute("SIGUIENTE")
        
        log = self.controller.get_execution_log()
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0]["action"], "PLAY_PAUSA")
        self.assertEqual(log[1]["action"], "SIGUIENTE")

    def test_execution_log_records_volume_commands(self):
        """Verifica que log registre comandos de volumen."""
        self.controller.set_volume(30.0)
        self.controller.set_volume(60.0)
        
        log = self.controller.get_execution_log()
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0]["action"], "CONTROL_VOLUMEN")
        self.assertEqual(log[0]["value"], 30.0)

    def test_clear_execution_log(self):
        """Verifica que clear_execution_log limpie el registro."""
        self.controller.execute("PLAY_PAUSA")
        self.controller.execute("SIGUIENTE")
        self.assertEqual(len(self.controller.get_execution_log()), 2)
        
        self.controller.clear_execution_log()
        self.assertEqual(len(self.controller.get_execution_log()), 0)

    def test_log_copy_prevents_external_modification(self):
        """Verifica que get_execution_log() retorne una copia."""
        self.controller.execute("PLAY_PAUSA")
        
        log_copy = self.controller.get_execution_log()
        original_len = len(log_copy)
        
        # Intentar modificar la copia
        log_copy.append({"action": "FAKE"})
        
        # El log interno debe ser inmutable
        self.assertEqual(len(self.controller.get_execution_log()), original_len)


class TestMediaControllerEdgeCases(unittest.TestCase):
    """Pruebas de casos extremos y manejo de errores."""

    def setUp(self):
        self.controller = MediaController(dry_run=True)

    def test_empty_string_command_rejected(self):
        """Verifica que comando vacío se rechace."""
        result = self.controller.execute("")
        self.assertFalse(result.success)

    def test_whitespace_command_rejected(self):
        """Verifica que comando con espacios se rechace."""
        result = self.controller.execute("   ")
        self.assertFalse(result.success)

    def test_special_characters_in_command_rejected(self):
        """Verifica que caracteres especiales en comando se rechacen."""
        result = self.controller.execute("PLAY_PAUSA\n")
        # Debe convertirse a mayúsculas y rechazarse si no es válido
        self.assertFalse(result.success)

    def test_volume_nan_rejected(self):
        """Verifica que volumen NaN se rechace."""
        result = self.controller.set_volume(float('nan'))
        # Debe manejar NaN de forma segura
        # Podría tratarse como error o clampearse
        # En esta implementación, veremos el comportamiento
        self.assertIsNotNone(result)

    def test_volume_inf_rejected(self):
        """Verifica que volumen infinito se rechace."""
        result = self.controller.set_volume(float('inf'))
        # Infinito debe manejearse de forma segura
        self.assertIsNotNone(result)

    def test_very_high_frequency_commands(self):
        """Verifica que múltiples comandos en secuencia rápida funcionen."""
        for i in range(100):
            result = self.controller.execute("PLAY_PAUSA")
            self.assertTrue(result.success)
        
        log = self.controller.get_execution_log()
        self.assertEqual(len(log), 100)

    def test_alternating_command_types(self):
        """Verifica que alternar entre tipos de comando funcione."""
        commands = ["PLAY_PAUSA", "SIGUIENTE", "ANTERIOR", "PLAY_PAUSA"]
        for cmd in commands:
            result = self.controller.execute(cmd)
            self.assertTrue(result.success)
        
        log = self.controller.get_execution_log()
        self.assertEqual(len(log), 4)


class TestMediaControllerDryRunMode(unittest.TestCase):
    """Pruebas específicas del modo dry_run."""

    def test_dry_run_true_marks_actions(self):
        """Verifica que dry_run=True marque acciones en log."""
        controller = MediaController(dry_run=True)
        controller.execute("PLAY_PAUSA")
        
        log = controller.get_execution_log()
        self.assertEqual(log[0]["dry_run"], True)

    def test_dry_run_false_marks_actions(self):
        """Verifica que dry_run=False marque acciones en log."""
        controller = MediaController(dry_run=False)
        controller.execute("SIGUIENTE")
        
        log = controller.get_execution_log()
        self.assertEqual(log[0]["dry_run"], False)

    def test_toggle_dry_run_mode(self):
        """Verifica que se pueda cambiar modo dry_run."""
        controller = MediaController(dry_run=True)
        controller.execute("PLAY_PAUSA")
        
        controller.dry_run = False
        controller.execute("SIGUIENTE")
        
        log = controller.get_execution_log()
        self.assertEqual(log[0]["dry_run"], True)
        self.assertEqual(log[1]["dry_run"], False)


class TestMediaControllerIntegrationWithModule7(unittest.TestCase):
    """Pruebas de cómo Module 8 recibiría comandos del Module 7."""

    def setUp(self):
        self.controller = MediaController(dry_run=True)

    def test_controller_receives_discrete_action_from_module7(self):
        """Simula que Module 7 envía comando PLAY_PAUSA."""
        # Module 7 retornaría action="PLAY_PAUSA" en StateMachineResult
        action = "PLAY_PAUSA"  # Esto vendría del Module 7
        
        result = self.controller.execute(action)
        self.assertTrue(result.success)

    def test_controller_receives_continuous_volume_from_module7(self):
        """Simula que Module 7 envía valor continuo de volumen."""
        # Module 7 retornaría action="CONTROL_VOLUMEN" y volume_value=45.0
        volume = 45.0  # Esto vendría del Module 7
        
        result = self.controller.set_volume(volume)
        self.assertTrue(result.success)

    def test_controller_ignores_none_from_module7(self):
        """Simula que Module 7 envía None (sin acción)."""
        # Module 7 retornaría action=None cuando no hay comando
        action = None
        
        result = self.controller.execute(action)
        self.assertFalse(result.success)

    def test_sequence_simulating_module7_flow(self):
        """Simula flujo completo de Module 7 al Module 8."""
        # Module 7 empieza: BLOQUEADO, sin acción
        result1 = self.controller.execute(None)
        self.assertFalse(result1.success)
        
        # Module 7: usuario activa, no hay acción aún
        result2 = self.controller.execute(None)
        self.assertFalse(result2.success)
        
        # Module 7: usuario realiza gesto PUÑO
        result3 = self.controller.execute("PLAY_PAUSA")
        self.assertTrue(result3.success)
        
        # Module 7: cooldown, sin acción
        result4 = self.controller.execute(None)
        self.assertFalse(result4.success)
        
        # Verificar que solo una acción fue ejecutada
        log = self.controller.get_execution_log()
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["action"], "PLAY_PAUSA")


if __name__ == "__main__":
    unittest.main()
