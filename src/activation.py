import math
import time
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@dataclass
class ActivationResult:
    """
    Contrato de datos de salida para el Módulo 4.
    Indica explícitamente el estado de la activación, el progreso actual
    y si se confirmó la activación en el frame actual.
    """
    is_activating: bool
    progress: float  # Rango de 0.0 a 1.0 (representando de 0% a 100%)
    activation_confirmed: bool

class ActivationController:
    """
    Controlador para el Módulo 4 - Gesto activador y validación temporal.
    Se encarga de evaluar si la presencia prolongada y estable de una palma abierta
    confirma la intención de activar el sistema AirDJ.
    """
    def __init__(
        self,
        activation_hold_time: float = 1.5,
        stability_threshold: float = 0.08,
        require_zone: bool = True
    ):
        """
        Inicializa el controlador con los umbrales correspondientes.

        Args:
            activation_hold_time (float): Tiempo en segundos que debe mantenerse la palma (ej: 1.5s).
            stability_threshold (float): Umbral de desplazamiento máximo permitido en coordenadas normalizadas.
            require_zone (bool): Si es True, requiere que inside_zone sea True para avanzar.
        """
        self.activation_hold_time = activation_hold_time
        self.stability_threshold = stability_threshold
        self.require_zone = require_zone
        
        # Inicializa variables de estado interno
        self.reset()

    def reset(self):
        """
        Reinicia el estado del controlador a su valor inicial predeterminado.
        Limpia temporizadores, posición de referencia, banderas de progreso y emisión.
        """
        self.start_time: Optional[float] = None
        self.reference_center: Optional[Tuple[float, float]] = None
        self.is_activating: bool = False
        self.progress: float = 0.0
        self.activation_emitted: bool = False

    def _is_stable(self, current_center: Tuple[float, float]) -> bool:
        """
        Calcula la distancia euclidiana entre el centro de la mano actual y la de referencia.
        Determina si el desplazamiento es menor o igual al umbral de estabilidad configurado.

        Args:
            current_center (Tuple[float, float]): Coordenadas normalizadas (x, y) del centro de la mano actual.

        Returns:
            bool: True si la mano se mantiene dentro del umbral de estabilidad, False en caso contrario.
        """
        if self.reference_center is None:
            return True
        
        ref_x, ref_y = self.reference_center
        cur_x, cur_y = current_center
        
        # Distancia Euclidiana
        distance = math.sqrt((cur_x - ref_x) ** 2 + (cur_y - ref_y) ** 2)
        return distance <= self.stability_threshold

    def _validate_inputs(self, gesture: Optional[str], hand_center: Optional[Tuple[float, float]], timestamp: Optional[float]) -> bool:
        """
        Valida que los tipos de datos de las entradas sean válidos y seguros para evitar excepciones.

        Args:
            gesture (Optional[str]): Gesto recibido.
            hand_center (Optional[Tuple[float, float]]): Centro de la mano recibido.
            timestamp (Optional[float]): Marca de tiempo recibida.

        Returns:
            bool: True si los tipos de datos mínimos obligatorios son válidos, False de lo contrario.
        """
        # Validar gesture
        if gesture is not None and not isinstance(gesture, str):
            return False
            
        # Validar hand_center
        if hand_center is not None:
            if not isinstance(hand_center, (tuple, list)) or len(hand_center) != 2:
                return False
            try:
                x, y = hand_center
                if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
                    return False
                if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
                    return False
            except (ValueError, TypeError):
                return False
                
        # Validar timestamp
        if timestamp is not None:
            if not isinstance(timestamp, (int, float)) or math.isnan(timestamp) or math.isinf(timestamp):
                return False
                
        return True

    def update(
        self,
        gesture: Optional[str],
        hand_center: Optional[Tuple[float, float]],
        timestamp: float,
        inside_zone: bool = True
    ) -> ActivationResult:
        """
        Procesa el estado de un frame de video, actualizando el temporizador de activación
        y el cálculo de estabilidad espacial.

        Args:
            gesture (Optional[str]): Gesto actual detectado (ej: "PALMA").
            hand_center (Optional[Tuple[float, float]]): Posición (x, y) normalizada del centro de la mano.
            timestamp (float): Tiempo actual en segundos (ej: time.time()).
            inside_zone (bool): Indica si la mano se encuentra dentro de la zona delimitada.

        Returns:
            ActivationResult: Objeto indicando el estado del proceso de activación.
        """
        # 1. Validación robusta de tipos de entrada para evitar excepciones por Nones o tipos inválidos
        if not self._validate_inputs(gesture, hand_center, timestamp):
            self.start_time = None
            self.reference_center = None
            self.is_activating = False
            self.progress = 0.0
            return ActivationResult(is_activating=False, progress=0.0, activation_confirmed=False)

        # Tratar timestamp None o inválido de forma segura usando tiempo de sistema
        if timestamp is None:
            timestamp = time.time()

        # Coerción y validación de la zona de interacción
        inside_valid_zone = bool(inside_zone) if isinstance(inside_zone, (bool, int)) else True
        effective_zone = inside_valid_zone or not self.require_zone

        # 2. Condiciones de reinicio / cancelación inmediata
        if gesture != "PALMA" or hand_center is None or not effective_zone:
            # Si el gesto ya fue confirmado, preservamos la bandera de emisión pero reseteamos el tracking
            self.start_time = None
            self.reference_center = None
            self.is_activating = False
            self.progress = 0.0
            return ActivationResult(
                is_activating=False,
                progress=0.0,
                activation_confirmed=False
            )

        # 3. Si ya se confirmó la activación previamente, no volvemos a procesar ni a emitir el evento.
        # Esperamos a que la máquina de estados ejecute un reset() explícito.
        if self.activation_emitted:
            return ActivationResult(
                is_activating=False,
                progress=1.0,
                activation_confirmed=False
            )

        # 4. Validar estabilidad si ya se inició el proceso
        if self.start_time is not None:
            if not self._is_stable(hand_center):
                # Desplazamiento excede el umbral: cancelar y reiniciar el proceso
                self.start_time = None
                self.reference_center = None
                self.is_activating = False
                self.progress = 0.0
                return ActivationResult(
                    is_activating=False,
                    progress=0.0,
                    activation_confirmed=False
                )

        # 5. Inicialización del proceso al detectar PALMA por primera vez
        if self.start_time is None:
            self.start_time = timestamp
            self.reference_center = hand_center
            self.is_activating = True
            self.progress = 0.0
            return ActivationResult(
                is_activating=True,
                progress=0.0,
                activation_confirmed=False
            )

        # 6. Progreso temporal
        elapsed_time = timestamp - self.start_time
        if elapsed_time < 0.0:
            elapsed_time = 0.0  # Control ante inconsistencias de tiempo

        self.progress = min(elapsed_time / self.activation_hold_time, 1.0)

        # 7. Comprobación del hold time
        if elapsed_time >= self.activation_hold_time:
            # Confirmación de la activación por primera vez
            confirmed = not self.activation_emitted
            if confirmed:
                self.activation_emitted = True
                self.is_activating = False  # Transiciona a confirmado
            
            return ActivationResult(
                is_activating=False,
                progress=1.0,
                activation_confirmed=confirmed
            )

        return ActivationResult(
            is_activating=True,
            progress=self.progress,
            activation_confirmed=False
        )
