"""
Demo del Módulo 9: Interfaz Visual de AirDJ.

Este script demuestra la interfaz visual simulando una secuencia completa de estados.
No requiere webcam ni entrada real.
"""

import cv2
import numpy as np
import time
from src.interface import AirDJInterface, SystemState, LandmarkPoint


def create_blank_frame(height=480, width=640):
    """Crea un frame vacío (fondo oscuro)."""
    return np.zeros((height, width, 3), dtype=np.uint8)


def simulate_activation_sequence():
    """Simula una secuencia completa de activación y ejecución."""
    print("Demo del Módulo 9 - Interfaz Visual de AirDJ")
    print("=" * 50)
    
    interface = AirDJInterface(debug=True)
    height, width = 480, 640
    
    # Secuencia de estados y valores
    sequence = [
        # BLOQUEADO
        {
            "duration": 2.0,
            "state": SystemState.BLOQUEADO,
            "gesture": "Sin mano",
            "description": "Sistema bloqueado - esperando activación"
        },
        # ACTIVANDO (progresivo)
        {
            "duration": 0.5,
            "state": SystemState.ACTIVANDO,
            "activation_progress": 0.25,
            "gesture": "PALMA",
            "description": "Activando 25%"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVANDO,
            "activation_progress": 0.5,
            "gesture": "PALMA",
            "description": "Activando 50%"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVANDO,
            "activation_progress": 0.75,
            "gesture": "PALMA",
            "description": "Activando 75%"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVANDO,
            "activation_progress": 1.0,
            "gesture": "PALMA",
            "description": "Activando 100%"
        },
        # ACTIVO (esperando comando)
        {
            "duration": 0.5,
            "state": SystemState.ACTIVO,
            "time_left": 5.0,
            "gesture": "Esperando gesto",
            "description": "Sistema activo - esperando comando"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVO,
            "time_left": 4.0,
            "gesture": "Esperando gesto",
            "description": "Tiempo: 4.0s"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVO,
            "time_left": 3.0,
            "gesture": "Esperando gesto",
            "description": "Tiempo: 3.0s"
        },
        # EJECUTANDO (comando detectado)
        {
            "duration": 0.3,
            "state": SystemState.EJECUTANDO,
            "executed_command": "PLAY_PAUSA",
            "description": "Ejecutando: PLAY / PAUSA"
        },
        # COOLDOWN
        {
            "duration": 0.3,
            "state": SystemState.COOLDOWN,
            "time_left": 1.5,
            "description": "Cooldown: 1.5s"
        },
        {
            "duration": 0.3,
            "state": SystemState.COOLDOWN,
            "time_left": 1.0,
            "description": "Cooldown: 1.0s"
        },
        {
            "duration": 0.3,
            "state": SystemState.COOLDOWN,
            "time_left": 0.5,
            "description": "Cooldown: 0.5s"
        },
        # BLOQUEADO (volvió)
        {
            "duration": 0.5,
            "state": SystemState.BLOQUEADO,
            "gesture": "Sistema listo",
            "description": "Sistema bloqueado nuevamente"
        },
        # VOLUMEN (nueva activación para demostrar volumen)
        {
            "duration": 0.5,
            "state": SystemState.ACTIVO,
            "time_left": 5.0,
            "volume_value": 0.0,
            "description": "Control de volumen: 0%"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVO,
            "time_left": 5.0,
            "volume_value": 25.0,
            "description": "Control de volumen: 25%"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVO,
            "time_left": 5.0,
            "volume_value": 50.0,
            "description": "Control de volumen: 50%"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVO,
            "time_left": 5.0,
            "volume_value": 75.0,
            "description": "Control de volumen: 75%"
        },
        {
            "duration": 0.5,
            "state": SystemState.ACTIVO,
            "time_left": 5.0,
            "volume_value": 100.0,
            "description": "Control de volumen: 100%"
        },
        # EJECUTANDO SIGUIENTE
        {
            "duration": 0.3,
            "state": SystemState.EJECUTANDO,
            "executed_command": "SIGUIENTE",
            "description": "Ejecutando: SIGUIENTE CANCIÓN"
        },
        # Final
        {
            "duration": 1.0,
            "state": SystemState.BLOQUEADO,
            "gesture": "Demo completada",
            "description": "Demo completada"
        },
    ]
    
    window_name = "AirDJ - Demostración Módulo 9 (Interfaz Visual)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    print("\nEjecutando secuencia de demostración...")
    print("Presiona cualquier tecla para avanzar, o ESC para salir\n")
    
    for i, step in enumerate(sequence):
        print(f"[{i+1}/{len(sequence)}] {step['description']}")
        
        # Crear frame para este paso
        frame = create_blank_frame(height, width)
        
        # Dibujar con los parámetros de este paso
        frame = interface.render(
            frame,
            state=step.get("state"),
            activation_progress=step.get("activation_progress", 0.0),
            time_left=step.get("time_left", 0.0),
            volume_value=step.get("volume_value"),
            detected_gesture=step.get("gesture"),
            executed_command=step.get("executed_command"),
            command_zone=(0.1, 0.1, 0.9, 0.9),
            fps=30.0
        )
        
        # Mostrar frame
        cv2.imshow(window_name, frame)
        
        # Esperar tiempo especificado o hasta que el usuario presione una tecla
        duration_ms = int(step["duration"] * 1000)
        key = cv2.waitKey(duration_ms)
        
        if key == 27:  # ESC
            print("\nDemo cancelada por el usuario.")
            break
    
    cv2.destroyAllWindows()
    print("\nDemo completada exitosamente.")


def simulate_multiple_commands():
    """Simula ejecución de múltiples comandos diferentes."""
    print("\n" + "=" * 50)
    print("Demo 2: Múltiples Comandos")
    print("=" * 50)
    
    interface = AirDJInterface(debug=False)
    height, width = 480, 640
    
    commands = [
        ("PLAY_PAUSA", "Reproducir / Pausar"),
        ("SIGUIENTE", "Siguiente Canción"),
        ("ANTERIOR", "Canción Anterior"),
        ("ACCION_ADICIONAL", "Acción Adicional"),
    ]
    
    window_name = "AirDJ - Comandos Multimedia"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    for command, description in commands:
        print(f"\nEjecutando: {description}")
        
        frame = create_blank_frame(height, width)
        frame = interface.render(
            frame,
            state=SystemState.EJECUTANDO,
            executed_command=command
        )
        
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1000)  # Mostrar por 1 segundo
        
        if key == 27:
            break
    
    cv2.destroyAllWindows()
    print("\nDemo 2 completada.")


def simulate_volume_transition():
    """Simula transición suave de volumen."""
    print("\n" + "=" * 50)
    print("Demo 3: Transición de Volumen")
    print("=" * 50)
    
    interface = AirDJInterface(debug=True)
    height, width = 480, 640
    
    window_name = "AirDJ - Control de Volumen"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    print("\nTransición de volumen de 0 a 100...")
    
    for volume in range(0, 101, 5):
        frame = create_blank_frame(height, width)
        frame = interface.render(
            frame,
            state=SystemState.ACTIVO,
            time_left=5.0 - (volume / 100.0 * 5.0),
            volume_value=float(volume),
            fps=60.0
        )
        
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(50)  # 50ms por frame para efecto suave
        
        if key == 27:
            break
    
    cv2.destroyAllWindows()
    print("Demo 3 completada.")


if __name__ == "__main__":
    try:
        simulate_activation_sequence()
        simulate_multiple_commands()
        simulate_volume_transition()
        
        print("\n" + "=" * 50)
        print("TODAS LAS DEMOSTRACIONES COMPLETADAS")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrumpida por el usuario.")
    except Exception as e:
        print(f"\nError durante la demo: {e}")
        import traceback
        traceback.print_exc()
