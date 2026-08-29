import cv2
import time
import sys
import os
from dotenv import load_dotenv

# Asegurar que el directorio raíz está en el path para poder importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.camera import CameraManager
from src.hand_detector import HandDetector
from src.activation import ActivationController, ActivationResult

def is_palm_demo_only(landmarks) -> bool:
    """
    Heurística de demostración aislada para detectar si la mano corresponde a una palma abierta.
    Esta función es exclusiva para pruebas visuales en este archivo demo.
    Verifica que los dedos índice, medio, anular y meñique estén extendidos.
    """
    try:
        # Puntos de MediaPipe:
        # Índice: punta=8, articulación intermedia (PIP)=6
        # Medio: punta=12, articulación intermedia (PIP)=10
        # Anular: punta=16, articulación intermedia (PIP)=14
        # Meñique: punta=20, articulación intermedia (PIP)=18
        index_open = landmarks[8].y < landmarks[6].y
        middle_open = landmarks[12].y < landmarks[10].y
        ring_open = landmarks[16].y < landmarks[14].y
        pinky_open = landmarks[20].y < landmarks[18].y

        return index_open and middle_open and ring_open and pinky_open
    except Exception:
        return False

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

    # Inicializar detector e interface del módulo 4 con umbral de 0.04
    detector = HandDetector(static_image_mode=False, max_num_hands=1)
    
    activation_hold_time = 1.5
    stability_threshold = 0.04  # Umbral más conservador
    
    activation = ActivationController(
        activation_hold_time=activation_hold_time,
        stability_threshold=stability_threshold,
        require_zone=True,
        window_size=10
    )

    props = camera.get_properties()
    w = props["width"]
    h = props["height"]

    # Definir la zona de comandos (caja central en coordenadas normalizadas)
    zone_x_min, zone_x_max = 0.3, 0.7
    zone_y_min, zone_y_max = 0.25, 0.75

    window_name = "AirDJ - Demo Modulo 4: Activacion y Estabilidad (Monotonica)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1024, 768)

    # Mensaje temporal de activación confirmada (usando tiempo monotónico)
    confirmation_display_until = 0.0

    print("\n=======================================================")
    print("DEMO INICIADA: Muestra una PALMA ABIERTA dentro de la zona.")
    print("Controles del teclado:")
    print("  R - Reiniciar activador manualmente (reset)")
    print("  Q - Salir")
    print("=======================================================\n")

    try:
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            # Detectar mano
            result = detector.detect(frame)
            gesture = "NEUTRO"
            inside_zone = False
            hand_center = None

            if result.detected:
                detector.draw_landmarks(frame, result, draw_center=True)
                hand_center = result.center_normalized
                
                # Clasificar gesto con la función de demo aislada
                if is_palm_demo_only(result.landmarks):
                    gesture = "PALMA"

                # Comprobar si está en la zona de comandos
                if hand_center is not None:
                    hx, hy = hand_center
                    if zone_x_min <= hx <= zone_x_max and zone_y_min <= hy <= zone_y_max:
                        inside_zone = True

            # Actualizar módulo de activación usando tiempo monotónico
            current_time = time.monotonic()
            act_res = activation.update(
                gesture=gesture,
                hand_center=hand_center,
                timestamp=current_time,
                inside_zone=inside_zone
            )

            # Si se confirma la activación, guardamos tiempo para mostrar cartel por 2.5s
            if act_res.activation_confirmed:
                confirmation_display_until = current_time + 2.5
                print("[EVENTO] ¡ACTIVACION_CONFIRMADA! El sistema esta desbloqueado.")

            # --- DIBUJAR LA ZONA DE COMANDOS ---
            box_color = (0, 255, 0) if (inside_zone and result.detected) else (0, 165, 255)
            thickness = 2 if inside_zone else 1
            
            p_min = (int(zone_x_min * w), int(zone_y_min * h))
            p_max = (int(zone_x_max * w), int(zone_y_max * h))
            cv2.rectangle(frame, p_min, p_max, box_color, thickness)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(
                frame, 
                "ZONA DE COMANDOS", 
                (p_min[0] + 10, p_min[1] + 25), 
                font, 
                0.5, 
                box_color, 
                1, 
                cv2.LINE_AA
            )

            # --- RENDER OVERLAY HUD ---
            hud_x1, hud_y1 = 15, 15
            hud_x2, hud_y2 = 420, 230
            overlay = frame.copy()
            cv2.rectangle(overlay, (hud_x1, hud_y1), (hud_x2, hud_y2), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)

            # Determinar estado para mostrar en el HUD a partir del campo status de la salida
            status_color = (100, 100, 100)  # Gris por defecto
            status_text = "BLOQUEADO"

            if act_res.status == "CONFIRMED" or current_time < confirmation_display_until:
                status_text = "ACTIVACION CONFIRMADA"
                status_color = (0, 255, 0)
            elif act_res.status == "ACTIVATING":
                status_text = f"ACTIVANDO... {int(act_res.progress * 100)}%"
                status_color = (0, 165, 255)
            elif act_res.status == "CANCELLED":
                status_text = "ACTIVACION CANCELADA"
                status_color = (0, 0, 255)  # Rojo
            elif activation.activation_emitted:
                status_text = "SISTEMA DESBLOQUEADO"
                status_color = (0, 255, 0)

            # Render de líneas del HUD
            lines = [
                "AirDJ - Demo Gesto Activador (Mod 4)",
                f"Gesto Detectado: {gesture if result.detected else 'SIN MANO'}",
                f"Dentro de Zona: {'SI' if inside_zone else 'NO'}",
                f"Estado Sistema: {status_text}",
                f"Progreso Activador:",
                "Controles: R = Resetear | Q = Salir"
            ]

            start_y = 40
            line_spacing = 25
            for i, line in enumerate(lines):
                line_color = (255, 255, 255)
                if i == 0:
                    line_color = (255, 255, 100)
                elif i == 3:
                    line_color = status_color
                elif i == 1:
                    line_color = (0, 255, 255) if gesture == "PALMA" else (255, 255, 255)

                cv2.putText(
                    frame, 
                    line, 
                    (hud_x1 + 15, start_y + (i * line_spacing)), 
                    font, 
                    0.55, 
                    line_color, 
                    1, 
                    cv2.LINE_AA
                )

            # --- DIBUJAR BARRA DE PROGRESO ---
            bar_x = hud_x1 + 15
            bar_y = start_y + (4 * line_spacing) + 12
            bar_w = 370
            bar_h = 12
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), 1)
            fill_w = int(act_res.progress * bar_w)
            if fill_w > 0:
                cv2.rectangle(
                    frame, 
                    (bar_x + 1, bar_y + 1), 
                    (bar_x + fill_w - 1, bar_y + bar_h - 1), 
                    status_color, 
                    -1
                )

            # --- CARTEL DE CONFIRMACIÓN EN EL CENTRO ---
            if current_time < confirmation_display_until:
                cv2.putText(
                    frame,
                    "SISTEMA ACTIVADO",
                    (int(w * 0.25), int(h * 0.5)),
                    font,
                    1.2,
                    (0, 255, 0),
                    3,
                    cv2.LINE_AA
                )
                cv2.putText(
                    frame,
                    "¡ACTIVACION CONFIRMADA!",
                    (int(w * 0.22), int(h * 0.58)),
                    font,
                    0.8,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

            # Mostrar frame
            cv2.imshow(window_name, frame)

            # Detectar teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("Cerrando demo...")
                break
            elif key == ord('r') or key == ord('R'):
                activation.reset()
                confirmation_display_until = 0.0
                print("[INFO] Módulo de activación reiniciado manualmente (reset).")

            # Reset automático si se quita la mano tras haber sido activado
            if activation.activation_emitted and not result.detected:
                activation.reset()
                print("[INFO] Mano retirada. Módulo reiniciado automáticamente.")

    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        detector.close()
        cv2.destroyAllWindows()
        print("Demo finalizada.")

if __name__ == "__main__":
    main()
