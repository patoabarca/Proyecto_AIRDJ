"""
Módulo 7: Máquina de Estados y Control de Timeouts.

Este módulo implementa la lógica de control de estados de AirDJ.
Decide cuándo los comandos deben ser aceptados, ejecutados, ignorados o descartados.

No realiza detección de gestos, cálculo de estabilidad ni acciones multimedia reales.
Solo consume resultados del Módulo 4 (ActivationController) y emite comandos lógicos.
"""

import math
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict

from src.activation import ActivationResult


class SystemState(Enum):
    """Estados posibles de la máquina de estados de AirDJ."""
    BLOQUEADO = "BLOQUEADO"
    ACTIVANDO = "ACTIVANDO"
    ACTIVO = "ACTIVO"
    EJECUTANDO = "EJECUTANDO"
    COOLDOWN = "COOLDOWN"


@dataclass
class StateMachineResult:
    """
    Contrato de datos de salida del Módulo 7.
    
    Propiedades:
        state: Estado actual de la máquina.
        action: Comando lógico autorizado (ej. "PLAY_PAUSA") o None.
        activation_progress: Progreso de activación [0.0, 1.0].
        time_left: Segundos restantes del timeout o cooldown.
        volume_value: Valor de volumen [0, 100] si está en modo continuo.
    """
    state: SystemState
    action: Optional[str]
    activation_progress: float
    time_left: float
    volume_value: Optional[float] = None


class StateMachine:
    """
    Máquina de estados principal de AirDJ.
    
    Gestiona:
    - Activación del sistema (transición BLOQUEADO → ACTIVO)
    - Ventana de comandos de 5 segundos
    - Ejecución única de comandos discretos
    - Control continuo de volumen
    - Cooldown post-ejecución
    
    Esta clase NO:
    - Reconoce gestos
    - Calcula estabilidad de palmaa
    - Ejecuta comandos multimedia reales
    - Modifica el estado del sistema operativo
    """
    
    # Mapeo de gestos discretos a comandos lógicos
    DISCRETE_GESTURE_MAP: Dict[str, str] = {
        "PUÑO": "PLAY_PAUSA",
        "SWIPE_DERECHA": "SIGUIENTE",
        "SWIPE_IZQUIERDA": "ANTERIOR",
        "INDICE": "ACCION_ADICIONAL"
    }

    def __init__(
        self,
        command_timeout: float = 5.0,
        cooldown_time: float = 1.5
    ):
        """
        Inicializa la máquina de estados.
        
        Args:
            command_timeout (float): Ventana de comandos en segundos (default 5.0).
            cooldown_time (float): Tiempo de espera post-ejecución en segundos (default 1.5).
        """
        self.command_timeout = command_timeout
        self.cooldown_time = cooldown_time
        self.reset()

    def reset(self):
        """
        Reinicia completamente la máquina al estado BLOQUEADO.
        Limpia todos los timers, flags y comandos pendientes.
        """
        self.state = SystemState.BLOQUEADO
        self.active_start_time: Optional[float] = None
        self.cooldown_start_time: Optional[float] = None
        self.action_to_execute: Optional[str] = None
        self.volume_adjusting: bool = False
        self.time_left: float = 0.0

    def update(
        self,
        activation_result: Optional[ActivationResult],
        command: Optional[str] = None,
        command_value: Optional[float] = None,
        timestamp: Optional[float] = None
    ) -> StateMachineResult:
        """
        Actualiza la máquina de estados en base a entrada y tiempo actual.
        
        Args:
            activation_result: Salida del Módulo 4 (ActivationController).
            command: Gesto de comando (ej. "PUÑO", "VOLUMEN", "SWIPE_DERECHA").
            command_value: Valor continuo asociado (ej. volumen 0-100).
            timestamp: Marca de tiempo en segundos (ej. time.monotonic()).
        
        Returns:
            StateMachineResult: Estado y acción autorizada del frame actual.
        """
        # Sanitizar timestamp
        if timestamp is None or not isinstance(timestamp, (int, float)):
            timestamp = time.monotonic()
        elif math.isnan(timestamp) or math.isinf(timestamp):
            timestamp = time.monotonic()

        # Sanitizar activation_result
        if activation_result is None or not isinstance(activation_result, ActivationResult):
            activation_result = ActivationResult(
                is_activating=False,
                progress=0.0,
                activation_confirmed=False,
                status="IDLE"
            )

        # Sanitizar command
        if command is not None and not isinstance(command, str):
            command = None

        # Sanitizar command_value
        if command_value is not None:
            if not isinstance(command_value, (int, float)) or math.isnan(command_value) or math.isinf(command_value):
                command_value = None

        # Lógica de transiciones según estado actual
        if self.state == SystemState.BLOQUEADO:
            return self._handle_bloqueado(activation_result, timestamp)
        elif self.state == SystemState.ACTIVANDO:
            return self._handle_activando(activation_result, timestamp)
        elif self.state == SystemState.ACTIVO:
            return self._handle_activo(activation_result, command, command_value, timestamp)
        elif self.state == SystemState.EJECUTANDO:
            return self._handle_ejecutando(timestamp)
        elif self.state == SystemState.COOLDOWN:
            return self._handle_cooldown(timestamp)
        else:
            # Fallback seguro
            return StateMachineResult(
                state=SystemState.BLOQUEADO,
                action=None,
                activation_progress=0.0,
                time_left=0.0
            )

    def _handle_bloqueado(
        self,
        activation_result: ActivationResult,
        timestamp: float
    ) -> StateMachineResult:
        """Maneja transiciones desde estado BLOQUEADO."""
        if activation_result.activation_confirmed:
            # Usuario completó la activación: transicionar a ACTIVO
            self.state = SystemState.ACTIVO
            self.active_start_time = timestamp
            self.time_left = self.command_timeout
            self.volume_adjusting = False
            return StateMachineResult(
                state=SystemState.ACTIVO,
                action=None,
                activation_progress=1.0,
                time_left=self.time_left
            )
        elif activation_result.is_activating or activation_result.status == "ACTIVATING":
            # Usuario comenzó a activar: transicionar a ACTIVANDO
            self.state = SystemState.ACTIVANDO
            return StateMachineResult(
                state=SystemState.ACTIVANDO,
                action=None,
                activation_progress=activation_result.progress,
                time_left=0.0
            )
        else:
            # Permanecer bloqueado
            return StateMachineResult(
                state=SystemState.BLOQUEADO,
                action=None,
                activation_progress=0.0,
                time_left=0.0
            )

    def _handle_activando(
        self,
        activation_result: ActivationResult,
        timestamp: float
    ) -> StateMachineResult:
        """Maneja transiciones desde estado ACTIVANDO."""
        if activation_result.activation_confirmed:
            # Activación completada: pasar a ACTIVO
            self.state = SystemState.ACTIVO
            self.active_start_time = timestamp
            self.time_left = self.command_timeout
            self.volume_adjusting = False
            return StateMachineResult(
                state=SystemState.ACTIVO,
                action=None,
                activation_progress=1.0,
                time_left=self.time_left
            )
        elif activation_result.is_activating or activation_result.status == "ACTIVATING":
            # Continuar en proceso de activación
            return StateMachineResult(
                state=SystemState.ACTIVANDO,
                action=None,
                activation_progress=activation_result.progress,
                time_left=0.0
            )
        else:
            # Activación cancelada: volver a BLOQUEADO
            self.state = SystemState.BLOQUEADO
            return StateMachineResult(
                state=SystemState.BLOQUEADO,
                action=None,
                activation_progress=0.0,
                time_left=0.0
            )

    def _handle_activo(
        self,
        activation_result: ActivationResult,
        command: Optional[str],
        command_value: Optional[float],
        timestamp: float
    ) -> StateMachineResult:
        """Maneja transiciones desde estado ACTIVO."""
        # Si ya está en modo de volumen continuo
        if self.volume_adjusting:
            if command == "VOLUMEN":
                # Continuar en modo volumen
                return StateMachineResult(
                    state=SystemState.ACTIVO,
                    action="CONTROL_VOLUMEN",
                    activation_progress=1.0,
                    time_left=self.command_timeout,
                    volume_value=command_value
                )
            else:
                # Gesto terminó: pasar a COOLDOWN
                self.state = SystemState.COOLDOWN
                self.cooldown_start_time = timestamp
                self.volume_adjusting = False
                self.time_left = self.cooldown_time
                return StateMachineResult(
                    state=SystemState.COOLDOWN,
                    action=None,
                    activation_progress=0.0,
                    time_left=self.time_left
                )

        # Verificar timeout de la ventana de comandos
        if self.active_start_time is None:
            # Seguridad: reinicializar si algo salió mal
            self.state = SystemState.BLOQUEADO
            return StateMachineResult(
                state=SystemState.BLOQUEADO,
                action=None,
                activation_progress=0.0,
                time_left=0.0
            )

        elapsed = timestamp - self.active_start_time
        self.time_left = max(0.0, self.command_timeout - elapsed)

        if elapsed >= self.command_timeout:
            # Timeout: volver a BLOQUEADO sin ejecutar comando
            self.state = SystemState.BLOQUEADO
            self.active_start_time = None
            return StateMachineResult(
                state=SystemState.BLOQUEADO,
                action=None,
                activation_progress=0.0,
                time_left=0.0
            )

        # Procesar comando
        if command in self.DISCRETE_GESTURE_MAP:
            # Comando discreto reconocido: pasar a EJECUTANDO
            self.state = SystemState.EJECUTANDO
            self.action_to_execute = self.DISCRETE_GESTURE_MAP[command]
            return StateMachineResult(
                state=SystemState.EJECUTANDO,
                action=self.action_to_execute,
                activation_progress=1.0,
                time_left=0.0
            )
        elif command == "VOLUMEN":
            # Iniciar sesión de volumen continuo
            self.volume_adjusting = True
            return StateMachineResult(
                state=SystemState.ACTIVO,
                action="CONTROL_VOLUMEN",
                activation_progress=1.0,
                time_left=self.command_timeout,
                volume_value=command_value
            )
        else:
            # Ningún comando reconocido: esperar en ACTIVO
            return StateMachineResult(
                state=SystemState.ACTIVO,
                action=None,
                activation_progress=1.0,
                time_left=self.time_left
            )

    def _handle_ejecutando(self, timestamp: float) -> StateMachineResult:
        """Maneja transiciones desde estado EJECUTANDO (duración de 1 frame)."""
        # Este estado es transitorio: emitir acción una vez y pasar a COOLDOWN
        self.state = SystemState.COOLDOWN
        self.cooldown_start_time = timestamp
        self.action_to_execute = None
        self.time_left = self.cooldown_time
        return StateMachineResult(
            state=SystemState.COOLDOWN,
            action=None,
            activation_progress=0.0,
            time_left=self.time_left
        )

    def _handle_cooldown(self, timestamp: float) -> StateMachineResult:
        """Maneja transiciones desde estado COOLDOWN."""
        if self.cooldown_start_time is None:
            # Seguridad: reinicializar si algo salió mal
            self.state = SystemState.BLOQUEADO
            return StateMachineResult(
                state=SystemState.BLOQUEADO,
                action=None,
                activation_progress=0.0,
                time_left=0.0
            )

        elapsed = timestamp - self.cooldown_start_time
        self.time_left = max(0.0, self.cooldown_time - elapsed)

        if elapsed >= self.cooldown_time:
            # Cooldown completado: volver a BLOQUEADO
            self.state = SystemState.BLOQUEADO
            self.cooldown_start_time = None
            return StateMachineResult(
                state=SystemState.BLOQUEADO,
                action=None,
                activation_progress=0.0,
                time_left=0.0
            )
        else:
            # Aún en cooldown: ignorar todas las entradas
            return StateMachineResult(
                state=SystemState.COOLDOWN,
                action=None,
                activation_progress=0.0,
                time_left=self.time_left
            )
