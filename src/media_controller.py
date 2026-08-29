"""
Módulo 8: Controlador Multimedia.

Este módulo mapea comandos lógicos autorizados (del Módulo 7) a acciones multimedia reales.

No realiza:
- Validación de estados del sistema (eso lo hace Módulo 7)
- Reconocimiento de gestos
- Cálculo de volumen

Solo ejecuta:
- Comandos play/pause, siguiente, anterior
- Ajuste de volumen continuo
- Modo simulado para testing

El módulo está completamente desacoplado del Módulo 7 y puede testearse aisladamente.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ActionType(str, Enum):
    """Tipos de acciones multimedia soportadas."""
    PLAY_PAUSA = "PLAY_PAUSA"
    SIGUIENTE = "SIGUIENTE"
    ANTERIOR = "ANTERIOR"
    CONTROL_VOLUMEN = "CONTROL_VOLUMEN"


@dataclass
class MediaControllerResult:
    """
    Contrato de datos de salida del Módulo 8.
    
    Propiedades:
        success: True si se ejecutó correctamente.
        action_attempted: Acción que se intentó ejecutar.
        value_used: Valor asociado (ej. volumen aplicado).
        error: Mensaje de error si ocurrió algo.
    """
    success: bool
    action_attempted: Optional[str]
    value_used: Optional[float] = None
    error: Optional[str] = None


class MediaController:
    """
    Controlador multimedia para AirDJ.
    
    Responsabilidades:
    - Ejecutar comandos multimedia autorizados
    - Validar rangos de entrada (ej. volumen 0-100)
    - Soportar modo simulado para testing
    
    No:
    - Decide cuándo ejecutar (eso lo hace Módulo 7)
    - Mantiene estado del sistema
    - Modifica configuraciones del OS directamente sin abstracción
    """

    def __init__(self, dry_run: bool = True):
        """
        Inicializa el controlador multimedia.
        
        Args:
            dry_run (bool): Si True, solo registra acciones sin ejecutar
                           comandos multimedia reales (default True para testing).
        """
        self.dry_run = dry_run
        self.execution_log: list[dict] = []

    def execute(self, command: Optional[str]) -> MediaControllerResult:
        """
        Ejecuta un comando multimedia discreto.
        
        Args:
            command: Comando a ejecutar ("PLAY_PAUSA", "SIGUIENTE", "ANTERIOR", etc.)
        
        Returns:
            MediaControllerResult: Resultado de la ejecución.
        """
        if command is None:
            return MediaControllerResult(
                success=False,
                action_attempted=None,
                error="Comando None recibido"
            )

        if not isinstance(command, str):
            return MediaControllerResult(
                success=False,
                action_attempted=str(command),
                error=f"Comando no es string: {type(command)}"
            )

        command = command.upper()

        # Validar que sea un comando conocido
        if command not in [ac.value for ac in ActionType]:
            return MediaControllerResult(
                success=False,
                action_attempted=command,
                error=f"Comando desconocido: {command}"
            )

        # Ejecutar comando
        if command == ActionType.PLAY_PAUSA.value:
            return self._execute_play_pause()
        elif command == ActionType.SIGUIENTE.value:
            return self._execute_next()
        elif command == ActionType.ANTERIOR.value:
            return self._execute_previous()
        else:
            return MediaControllerResult(
                success=False,
                action_attempted=command,
                error=f"No está implementado: {command}"
            )

    def set_volume(self, value: Optional[float]) -> MediaControllerResult:
        """
        Ajusta el volumen del reproductor.
        
        Args:
            value: Nivel de volumen en rango [0, 100].
        
        Returns:
            MediaControllerResult: Resultado de la operación.
        """
        if value is None:
            return MediaControllerResult(
                success=False,
                action_attempted="CONTROL_VOLUMEN",
                error="Valor de volumen es None"
            )

        if not isinstance(value, (int, float)):
            return MediaControllerResult(
                success=False,
                action_attempted="CONTROL_VOLUMEN",
                error=f"Volumen debe ser número, recibido: {type(value)}"
            )

        # Aplicar límites defensivos
        clamped_value = max(0.0, min(100.0, float(value)))

        # Ejecutar
        if self.dry_run:
            result = MediaControllerResult(
                success=True,
                action_attempted="CONTROL_VOLUMEN",
                value_used=clamped_value
            )
            self.execution_log.append({
                "action": "CONTROL_VOLUMEN",
                "value": clamped_value,
                "dry_run": True
            })
            return result
        else:
            # En modo real, aquí iría la lógica para controlar el volumen
            # del reproductor usando bibliotecas multimedia
            # Por ahora, registramos la intención
            result = MediaControllerResult(
                success=True,
                action_attempted="CONTROL_VOLUMEN",
                value_used=clamped_value
            )
            self.execution_log.append({
                "action": "CONTROL_VOLUMEN",
                "value": clamped_value,
                "dry_run": False
            })
            return result

    def _execute_play_pause(self) -> MediaControllerResult:
        """Ejecuta comando play/pause."""
        if self.dry_run:
            self.execution_log.append({
                "action": "PLAY_PAUSA",
                "dry_run": True
            })
            return MediaControllerResult(
                success=True,
                action_attempted="PLAY_PAUSA"
            )
        else:
            # Aquí iría lógica real para reproducir/pausar
            self.execution_log.append({
                "action": "PLAY_PAUSA",
                "dry_run": False
            })
            return MediaControllerResult(
                success=True,
                action_attempted="PLAY_PAUSA"
            )

    def _execute_next(self) -> MediaControllerResult:
        """Ejecuta comando siguiente canción."""
        if self.dry_run:
            self.execution_log.append({
                "action": "SIGUIENTE",
                "dry_run": True
            })
            return MediaControllerResult(
                success=True,
                action_attempted="SIGUIENTE"
            )
        else:
            # Aquí iría lógica real para siguiente canción
            self.execution_log.append({
                "action": "SIGUIENTE",
                "dry_run": False
            })
            return MediaControllerResult(
                success=True,
                action_attempted="SIGUIENTE"
            )

    def _execute_previous(self) -> MediaControllerResult:
        """Ejecuta comando canción anterior."""
        if self.dry_run:
            self.execution_log.append({
                "action": "ANTERIOR",
                "dry_run": True
            })
            return MediaControllerResult(
                success=True,
                action_attempted="ANTERIOR"
            )
        else:
            # Aquí iría lógica real para canción anterior
            self.execution_log.append({
                "action": "ANTERIOR",
                "dry_run": False
            })
            return MediaControllerResult(
                success=True,
                action_attempted="ANTERIOR"
            )

    def get_execution_log(self) -> list[dict]:
        """
        Retorna el registro de acciones ejecutadas (útil para testing).
        
        Returns:
            Lista de diccionarios con registro de ejecuciones.
        """
        return self.execution_log.copy()

    def clear_execution_log(self) -> None:
        """Limpia el registro de ejecuciones."""
        self.execution_log.clear()
