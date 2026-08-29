import time
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict

from src.activation import ActivationResult

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SystemState(Enum):
    """
    Representa los estados de la máquina de estados de AirDJ.
    """
    BLOQUEADO = "BLOQUEADO"
    ACTIVANDO = "ACTIVANDO"
    ACTIVO = "ACTIVO"
    EJECUTANDO = "EJECUTANDO"
    COOLDOWN = "COOLDOWN"

@dataclass
class StateMachineResult:
    """
    Contrato de datos de salida para la máquina de estados de AirDJ (Módulo 7).
    """
    state: SystemState
    action: Optional[str]            # Comando a ejecutar (ej. "PLAY_PAUSA") o None
    activation_progress: float       # Progreso del gesto activador en el rango [0.0, 1.0]
    time_left: float                 # Segundos restantes para timeout o cooldown
    volume_value: Optional[float] = None  # Valor de volumen en modo continuo si corresponde

class StateMachine:
    """
    Máquina de estados principal para AirDJ.
    Controla el flujo de interacción, los timeouts de la ventana de comandos,
    la ejecución única de comandos discretos y el ajuste continuo del volumen.
    """
    # Mapeo de gestos de entrada discretos a acciones de salida multimedia
    DISCRETE_GESTURE_MAP: Dict[str, str] = {
        "PUÑO": "PLAY_PAUSA",
        "SWIPE_DERECHA": "SIGUIENTE",
        "SWIPE_IZQUIERDA": "ANTERIOR",
        "INDICE": "ACCION_ADICIONAL"
    }

    def __init__(self, command_timeout: float = 5.0, cooldown_time: float = 1.5):
        """
        Inicializa la máquina de estados.

        Args:
            command_timeout (float): Tiempo en segundos que dura la ventana de comandos activa (timeout).
            cooldown_time (float): Tiempo en segundos de espera post-ejecución (cooldown).
        """
        self.command_timeout = command_timeout
        self.cooldown_time = cooldown_time
        
        # Inicializa variables de estado interno
        self.reset()

    def reset(self):
        """
        Restablece la máquina de estados a un estado inicial completamente limpio y bloqueado.
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
        Procesa el estado del sistema en base a los eventos ya interpretados y el tiempo actual.

        Args:
            activation_result (Optional[ActivationResult]): Resultado de la validación del activador del Módulo 4.
            command (Optional[str]): Gesto de comando actual (ej. "PUÑO", "VOLUMEN", "SWIPE_DERECHA", etc.).
            command_value (Optional[float]): Valor continuo asociado al comando (ej. 0-100 para volumen).
            timestamp (Optional[float]): Marca de tiempo en segundos (ej. time.monotonic()).

        Returns:
            StateMachineResult: El estado resultante del sistema en el frame actual.
        """
        # 1. Tratamiento robusto de timestamp
        if timestamp is None or not isinstance(timestamp, (int, float)) or math.isnan(timestamp) or math.isinf(timestamp):
            timestamp = time.monotonic()

        # 2. Tratamiento robusto de inputs None o inválidos
        if activation_result is None or not isinstance(activation_result, ActivationResult):
            # Si no hay datos del Módulo 4, simulamos una entrada inactiva por seguridad
            activation_result = ActivationResult(
                is_activating=False,
                progress=0.0,
                activation_confirmed=False,
                status="IDLE"
            )

        # Sanitizar strings de comando
        if command is not None and not isinstance(command, str):
            command = None

        # Sanitizar valores de volumen
        if command_value is not None:
            if not isinstance(command_value, (int, float)) or math.isnan(command_value) or math.isinf(command_value):
                command_value = None

        # 3. Evaluar transiciones según el estado actual de la máquina de estados
        
        # --- ESTADO: BLOQUEADO ---
        if self.state == SystemState.BLOQUEADO:
            if activation_result.activation_confirmed:
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
                self.state = SystemState.ACTIVANDO
                return StateMachineResult(
                    state=SystemState.ACTIVANDO,
                    action=None,
                    activation_progress=activation_result.progress,
                    time_left=0.0
                )
            else:
                return StateMachineResult(
                    state=SystemState.BLOQUEADO,
                    action=None,
                    activation_progress=0.0,
                    time_left=0.0
                )

        # --- ESTADO: ACTIVANDO ---
        elif self.state == SystemState.ACTIVANDO:
            if activation_result.activation_confirmed:
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
                # Seguimos activando
                return StateMachineResult(
                    state=SystemState.ACTIVANDO,
                    action=None,
                    activation_progress=activation_result.progress,
                    time_left=0.0
                )
            else:
                # Se interrumpió la activación
                self.state = SystemState.BLOQUEADO
                return StateMachineResult(
                    state=SystemState.BLOQUEADO,
                    action=None,
                    activation_progress=0.0,
                    time_left=0.0
                )

        # --- ESTADO: ACTIVO ---
        elif self.state == SystemState.ACTIVO:
            # Control de Volumen Continuo
            if self.volume_adjusting:
                if command == "VOLUMEN":
                    # Mantiene el modo de ajuste de volumen continuo mientras siga el gesto.
                    # No restamos el timeout en cada frame, se mantiene suspendido.
                    return StateMachineResult(
                        state=SystemState.ACTIVO,
                        action="CONTROL_VOLUMEN",
                        activation_progress=1.0,
                        time_left=self.command_timeout,
                        volume_value=command_value
                    )
                else:
                    # El gesto finalizó o cambió: pasar inmediatamente a COOLDOWN
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

            # Control de Timeout de la ventana de comandos
            elapsed = timestamp - self.active_start_time
            self.time_left = max(0.0, self.command_timeout - elapsed)

            if elapsed >= self.command_timeout:
                # Ventana temporal vencida sin gestos, volvemos a BLOQUEADO
                self.state = SystemState.BLOQUEADO
                self.active_start_time = None
                return StateMachineResult(
                    state=SystemState.BLOQUEADO,
                    action=None,
                    activation_progress=0.0,
                    time_left=0.0
                )

            # Evaluar comandos entrantes
            if command in self.DISCRETE_GESTURE_MAP:
                # Transicionar al estado EJECUTANDO por un ciclo
                self.state = SystemState.EJECUTANDO
                self.action_to_execute = self.DISCRETE_GESTURE_MAP[command]
                return StateMachineResult(
                    state=SystemState.EJECUTANDO,
                    action=self.action_to_execute,
                    activation_progress=1.0,
                    time_left=0.0
                )
            elif command == "VOLUMEN":
                # Inicia el modo de ajuste continuo de volumen
                self.volume_adjusting = True
                return StateMachineResult(
                    state=SystemState.ACTIVO,
                    action="CONTROL_VOLUMEN",
                    activation_progress=1.0,
                    time_left=self.command_timeout,
                    volume_value=command_value
                )
            else:
                # No llegó ningún comando reconocido, seguimos esperando en ACTIVO
                return StateMachineResult(
                    state=SystemState.ACTIVO,
                    action=None,
                    activation_progress=1.0,
                    time_left=self.time_left
                )

        # --- ESTADO: EJECUTANDO ---
        elif self.state == SystemState.EJECUTANDO:
            # Este estado dura un único frame. Transiciona automáticamente a COOLDOWN.
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

        # --- ESTADO: COOLDOWN ---
        elif self.state == SystemState.COOLDOWN:
            elapsed = timestamp - self.cooldown_start_time
            self.time_left = max(0.0, self.cooldown_time - elapsed)

            if elapsed >= self.cooldown_time:
                # Cooldown completado, volver a BLOQUEADO
                self.state = SystemState.BLOQUEADO
                self.cooldown_start_time = None
                return StateMachineResult(
                    state=SystemState.BLOQUEADO,
                    action=None,
                    activation_progress=0.0,
                    time_left=0.0
                )
            else:
                # Ignorar todas las entradas mientras esté en cooldown
                return StateMachineResult(
                    state=SystemState.COOLDOWN,
                    action=None,
                    activation_progress=0.0,
                    time_left=self.time_left
                )

import math
