import cv2
import time
import sys
import os
import math
from dotenv import load_dotenv

# Asegurar que el directorio raíz está en el path para poder importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.camera import CameraManager
from src.hand_detector import HandDetector
from src.activation import ActivationController
from src.state_machine import StateMachine, SystemState

def is_palm_demo_only(landmarks) -> bool:
    """
    Heurística de demo para detectar si la mano corresponde a una palma abierta.
    """
    try:
        index_open = landmarks[8].y < landmarks[6].y
        middle_open = landmarks[12].y < landmarks[10].y
        ring_open = landmarks[16].y < landmarks[14].y
        pinky_open = landmarks[20].y < landmarks[18].y
        return index_open and middle_open and ring_open and pinky_open
    except Exception:
        return False

def is_fist_demo_only(landmarks) -> bool:
    """
    Heurística de demo para detectar si la mano corresponde a un puño cerrado.
    """
    try:
        index_closed = landmarks[8].y >= landmarks[6].y
        middle_closed = landmarks[12].y >= landmarks[10].y
        ring_closed = landmarks[16].y >= landmarks[14].y
        pinky_closed = landmarks[20].y >= landmarks[18].y
        return index_closed and middle_closed and ring_closed and pinky_closed
    except Exception:
        return False

def detect_gesture_and_value(landmarks):
    """
    Heurística de demo aislada para clasificar gestos:
    - PALMA (abierta)
    - PUÑO (cerrado)
    - INDICE (levantado)
    - VOLUMEN (pulgar e índice extendidos, los otros tres cerrados)
    """
    if is_palm_demo_only(landmarks):
        return "PALMA", None
    if is_fist_demo_only(landmarks):
        return "PUÑO", None
        
    try:
        index_open = landmarks[8].y < landmarks[6].y
        middle_closed = landmarks[12].y >= landmarks[10].y
        ring_closed = landmarks[16].y >= landmarks[14].y
        pinky_closed = landmarks[20].y >= landmarks[18].y
        
        # INDICE
        if index_open and middle_closed and ring_closed and pinky_closed:
            # Comprobar que no sea pinza (distancia grande entre pulgar e índice)
            dx = landmarks[4].x - landmarks[8].x
            dy = landmarks[4].y - landmarks[8].y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0.08:
                return "INDICE", None

        # VOLUMEN (Pinza)
        # Medio, anular y meñique cerrados
        if middle_closed and ring_closed and pinky_closed:
            # Medimos distancia entre punta del pulgar (4) y punta del índice (8)
            dx = landmarks[4].x - landmarks[8].x
            dy = landmarks[4].y - landmarks[8].y
            dist = math.sqrt(dx*dx + dy*dy)
            # Mapeamos distancia a volumen 0-100%
            # Pellizco completo (~0.02) -> 0%, apertura máxima (~0.14) -> 100%
            vol = min(max((dist - 0.02) / (0.12 - 0.02), 0.0), 1.0) * 100.0
            return "VOLUMEN", vol

    except Exception:
        pass
        
    return "NEUTRO", None

def main():
    load_dotenv()

    # Buscar cámaras disponibles
    available = CameraManager.find_available_cameras(max_to_check=3)
    if not available:
        print("[ERROR] No se detecto ninguna camara activa.", file=sys.stderr)
        sys.exit(1)
    
    camera_index = available[0][0]
    print(f"Iniciando camara {available[0][1]} (Indice: {camera_index})...")
    camera = CameraManager(device_index=camera_index)

    if not camera.open():
        print(f"[ERROR] No se pudo abrir la camara.", file=sys.stderr)
        sys.exit(1)

    # Componentes modulares
    detector = HandDetector(static_image_mode=False, max_num_hands=1)
    activation = ActivationController(activation_hold_time=1.5, stability_threshold=0.04, require_zone=True)
    state_machine = StateMachine(command_timeout=5.0, cooldown_time=1.5)

    props = camera.get_properties()
    w = props["width"]
    h = props["height"]

    # Zona de comandos (caja central)
    zone_x_min, zone_x_max = 0.3, 0.7
    zone_y_min, zone_y_max = 0.25, 0.75

    window_name = "AirDJ - Demo Modulo 7: Maquina de Estados"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1024, 768)

    # Control de popups y simulaciones por teclado
    last_action_executed = None
    action_display_until = 0.0
    simulated_command = None

    print("\n=======================================================")
    print("DEMO INICIADA: Muestra PALMA estable para activar el sistema.")
    print("Una vez ACTIVO, realiza un gesto de comando:")
    print("  - PUÑO (Play/Pausa)")
    print("  - INDICE (Acción Adicional)")
    print("  - PINZA Pulgar-Indice (Ajustar volumen continuo)")
    print("Controles del teclado:")
    print("  Flecha Derecha - Simular Swipe Derecha (Siguiente)")
    print("  Flecha Izquierda - Simular Swipe Izquierda (Anterior)")
    print("  R - Reiniciar máquina (reset)")
    print("  Q - Salir")
    print("=======================================================\n")

    try:
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            current_time = time.monotonic()

            # 1. Procesamiento de Mano
            result = detector.detect(frame)
            gesture = "NEUTRO"
            inside_zone = False
            hand_center = None
            gesture_value = None

            if result.detected:
                detector.draw_landmarks(frame, result, draw_center=True)
                hand_center = result.center_normalized
                
                # Clasificar con la heurística de demo
                gesture, gesture_value = detect_gesture_and_value(result.landmarks)

                # Verificar si está en la zona de comandos
                if hand_center is not None:
                    hx, hy = hand_center
                    if zone_x_min <= hx <= zone_x_max and zone_y_min <= hy <= zone_y_max:
                        inside_zone = True

            # 2. Actualizar Módulo de Activación (Módulo 4)
            act_res = activation.update(
                gesture=gesture,
                hand_center=hand_center,
                timestamp=current_time,
                inside_zone=inside_zone
            )

            # 3. Determinar comando a enviar a la Máquina de Estados
            # Prioriza comandos simulados por teclado
            cmd_to_send = simulated_command if simulated_command else gesture
            val_to_send = gesture_value if simulated_command is None else None

            # 4. Actualizar Máquina de Estados (Módulo 7)
            state_res = state_machine.update(
                activation_result=act_res,
                command=cmd_to_send,
                command_value=val_to_send,
                timestamp=current_time
            )

            # Limpiar el comando simulado una vez enviado
            simulated_command = None

            # Si transiciona a EJECUTANDO, registrar evento para popup visual
            if state_res.state == SystemState.EJECUTANDO and state_res.action:
                last_action_executed = state_res.action
                action_display_until = current_time + 1.8
                print(f"[COMANDO EJECUTADO] -> {last_action_executed}")

            # Sincronizar el reset del activador si la máquina de estados volvió a BLOQUEADO
            if state_res.state == SystemState.BLOQUEADO and activation.activation_emitted:
                activation.reset()

            # --- DIBUJAR LA ZONA DE COMANDOS ---
            box_color = (0, 255, 0) if (inside_zone and result.detected) else (0, 165, 255)
            thickness = 2 if inside_zone else 1
            p_min = (int(zone_x_min * w), int(zone_y_min * h))
            p_max = (int(zone_x_max * w), int(zone_y_max * h))
            cv2.rectangle(frame, p_min, p_max, box_color, thickness)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, "ZONA DE COMANDOS", (p_min[0] + 10, p_min[1] + 25), font, 0.5, box_color, 1, cv2.LINE_AA)

            # --- RENDER OVERLAY HUD ---
            hud_x1, hud_y1 = 15, 15
            hud_x2, hud_y2 = 420, 260
            overlay = frame.copy()
            cv2.rectangle(overlay, (hud_x1, hud_y1), (hud_x2, hud_y2), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)

            # Asignar colores según el estado
            state_colors = {
                SystemState.BLOQUEADO: (120, 120, 120),
                SystemState.ACTIVANDO: (0, 165, 255),
                SystemState.ACTIVO: (0, 255, 0),
                SystemState.EJECUTANDO: (255, 255, 0),
                SystemState.COOLDOWN: (0, 0, 255)
            }
            state_color = state_colors.get(state_res.state, (255, 255, 255))

            lines = [
                "AirDJ - Control de Estados (Mod 7)",
                f"Gesto Detectado: {gesture if result.detected else 'SIN MANO'}",
                f"Estado Maquina: {state_res.state.value}",
                f"Progreso Actividad:",
                f"Tiempo Restante: {state_res.time_left:.1f} s",
                "Teclado: Flechas = Swipes | R = Reset | Q = Salir"
            ]

            start_y = 40
            line_spacing = 25
            for i, line in enumerate(lines):
                line_color = (255, 255, 255)
                if i == 0:
                    line_color = (255, 255, 100)
                elif i == 2:
                    line_color = state_color
                elif i == 1:
                    line_color = (0, 255, 255) if gesture != "NEUTRO" and result.detected else (255, 255, 255)

                cv2.putText(frame, line, (hud_x1 + 15, start_y + (i * line_spacing)), font, 0.55, line_color, 1, cv2.LINE_AA)

            # --- DIBUJAR BARRA DE PROGRESO DE ACTIVIDAD EN EL HUD ---
            bar_x = hud_x1 + 15
            bar_y = start_y + (3 * line_spacing) + 12
            bar_w = 370
            bar_h = 10
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), 1)

            # Relleno de la barra según el estado
            progress_ratio = 0.0
            if state_res.state in (SystemState.BLOQUEADO, SystemState.ACTIVANDO):
                progress_ratio = state_res.activation_progress
            elif state_res.state == SystemState.ACTIVO:
                progress_ratio = state_res.time_left / state_machine.command_timeout
            elif state_res.state == SystemState.COOLDOWN:
                progress_ratio = state_res.time_left / state_machine.cooldown_time

            fill_w = int(progress_ratio * bar_w)
            if fill_w > 0:
                cv2.rectangle(frame, (bar_x + 1, bar_y + 1), (bar_x + fill_w - 1, bar_y + bar_h - 1), state_color, -1)

            # --- FEEDBACK DE VOLUMEN CONTINUO ---
            if state_res.action == "CONTROL_VOLUMEN" and state_res.volume_value is not None:
                vol_val = state_res.volume_value
                # Dibujar barra vertical de volumen en el lado derecho
                vol_bar_x = w - 50
                vol_bar_y = 150
                vol_bar_h = h - 300
                vol_bar_w = 20
                cv2.rectangle(frame, (vol_bar_x, vol_bar_y), (vol_bar_x + vol_bar_w, vol_bar_y + vol_bar_h), (100, 100, 100), 1)
                
                # Relleno de volumen
                vol_fill_h = int((vol_val / 100.0) * vol_bar_h)
                cv2.rectangle(frame, (vol_bar_x + 1, vol_bar_y + vol_bar_h - vol_fill_h), (vol_bar_x + vol_bar_w - 1, vol_bar_y + vol_bar_h - 1), (0, 255, 255), -1)
                cv2.putText(frame, f"VOL: {int(vol_val)}%", (vol_bar_x - 30, vol_bar_y - 15), font, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

            # --- POPUP CENTRAL DE ACCION EJECUTADA ---
            if current_time < action_display_until and last_action_executed:
                cv2.putText(frame, "ACCION MULTIMEDIA", (int(w * 0.28), int(h * 0.45)), font, 1.0, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"[{last_action_executed}]", (int(w * 0.32), int(h * 0.55)), font, 1.2, (0, 255, 255), 3, cv2.LINE_AA)

            # Mostrar frame
            cv2.imshow(window_name, frame)

            # Teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('r') or key == ord('R'):
                state_machine.reset()
                activation.reset()
                last_action_executed = None
                action_display_until = 0.0
                print("[INFO] Reinicio completo de activador y maquina de estados.")
            # Simular Swipes
            elif key == 83 or key == ord('d') or key == ord('D'):  # Flecha derecha o D
                simulated_command = "SWIPE_DERECHA"
            elif key == 81 or key == ord('a') or key == ord('A'):  # Flecha izquierda o A
                simulated_command = "SWIPE_IZQUIERDA"

            # Auto-reset del activador si la mano se retira estando desbloqueado
            if state_res.state == SystemState.BLOQUEADO and not result.detected and activation.activation_emitted:
                activation.reset()

    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        detector.close()
        cv2.destroyAllWindows()
        print("Demo finalizada.")

if __name__ == "__main__":
    main()
