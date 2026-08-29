import cv2
import time
import sys
import argparse
import os
from dotenv import load_dotenv

# Importar managers y controladores del proyecto
from src.camera import CameraManager
from src.hand_detector import HandDetector, HandLandmark
from src.static_gestures import GestureLabel, StaticGestureRecognizer
from src.dynamic_gestures import SwipeDetector
from src.volume_control import VolumeController
from src.activation import ActivationController
from src.state_machine import StateMachine
from src.media_controller import MediaController
from src.interface import AirDJInterface, SystemState as UISystemState

def parse_args():
    """
    Parsea los argumentos de la línea de comandos.
    """
    parser = argparse.ArgumentParser(description="AirDJ - Bucle Principal Integrado (Módulos 1 a 9)")
    parser.add_argument(
        "-c", "--camera",
        type=int,
        default=None,
        help="Indice de la camara a utilizar (ej. 0, 1, 2)."
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Ejecutar el controlador multimedia en modo simulador (sin controlar el volumen o teclas del OS real)."
    )
    return parser.parse_args()

def main():
    # Cargar variables de entorno
    load_dotenv()

    # Parsear argumentos
    args = parse_args()
    camera_index = args.camera
    dry_run_mode = args.dry_run

    # Si no se especificó la cámara por CLI, leer la de .env
    if camera_index is None:
        env_cam_index = os.getenv("DEFAULT_CAMERA_INDEX")
        if env_cam_index is not None and env_cam_index.strip() != "":
            try:
                camera_index = int(env_cam_index)
                print(f"Usando camara por defecto desde .env: {camera_index}")
            except ValueError:
                pass

    # Si no se detectó índice, buscar cámaras activas
    if camera_index is None:
        available = CameraManager.find_available_cameras(max_to_check=5)
        if not available:
            print("[ERROR] No se detecto ninguna camara activa en los indices del 0 al 4.", file=sys.stderr)
            sys.exit(1)
        elif len(available) == 1:
            camera_index = available[0][0]
            print(f"Camara detectada automaticamente: {available[0][1]} (Indice: {camera_index})")
        else:
            print("\n=== Multiples camaras detectadas ===")
            valid_indices = [item[0] for item in available]
            default_index = valid_indices[0]
            
            for idx, name in available:
                print(f"[{idx}] {name}")
            
            try:
                user_input = input(f"Selecciona el indice de la camara a usar {valid_indices} [por defecto {default_index}]: ").strip()
                if user_input == "":
                    camera_index = default_index
                else:
                    selected = int(user_input)
                    if selected in valid_indices:
                        camera_index = selected
                    else:
                        print(f"Opcion no valida. Usando camara por defecto: {available[0][1]} (Indice: {default_index})")
                        camera_index = default_index
            except (ValueError, KeyboardInterrupt, EOFError):
                print(f"\nEntrada cancelada. Usando camara por defecto: {available[0][1]} (Indice: {default_index})")
                camera_index = default_index
    
    print(f"Iniciando CameraManager con camara indice: {camera_index}...")
    camera = CameraManager(device_index=camera_index)

    if not camera.open():
        print(f"[ERROR] No se pudo abrir la camara con indice {camera_index}.", file=sys.stderr)
        sys.exit(1)

    # --- INICIALIZACIÓN DE MÓDULOS DE AIRDJ ---
    
    # Módulo 2: Detección de Mano y Landmarks
    detector = HandDetector(static_image_mode=False, max_num_hands=1)
    
    # Módulo 3: Reconocedor de Gestos Estáticos
    gesture_recognizer = StaticGestureRecognizer()

    # Módulo 5: Detector de Gestos Dinámicos (Swipe)
    swipe_detector = SwipeDetector()

    # Módulo 6: Controlador de Volumen
    volume_controller = VolumeController(min_distance=0.2, max_distance=1.0, smooth_alpha=0.15)

    # Módulo 4: Controlador de Activación (hold_time = 1.5s, require_zone = True)
    activation_controller = ActivationController(
        activation_hold_time=1.5,
        stability_threshold=0.04,
        require_zone=True
    )

    # Módulo 7: Máquina de Estados (timeout = 5.0s, cooldown = 1.5s)
    state_machine = StateMachine(command_timeout=5.0, cooldown_time=1.5)

    # Módulo 8: Controlador Multimedia (Modo simulado por defecto para evitar problemas al usuario)
    # Si se pasa -d / --dry-run o la variable de entorno está activada, se ejecuta en dry_run
    env_dry_run = os.getenv("MEDIA_CONTROLLER_DRY_RUN", "True").lower() == "true"
    final_dry_run = dry_run_mode or env_dry_run
    
    print(f"Iniciando MediaController (dry_run={final_dry_run})...")
    media_controller = MediaController(dry_run=final_dry_run)

    # Módulo 9: Interfaz Gráfica Visual y Feedback
    interface = AirDJInterface(debug=True)

    # Definición de la zona de comandos (caja central en coordenadas normalizadas)
    zone_x_min, zone_x_max = 0.3, 0.7
    zone_y_min, zone_y_max = 0.25, 0.75
    command_zone_coords = (zone_x_min, zone_y_min, zone_x_max, zone_y_max)

    # Propiedades de la cámara
    props = camera.get_properties()
    width = props["width"]
    height = props["height"]
    camera_fps = props["fps"]

    print("\n---------------------------------------")
    print("AirDJ - Propiedades de la Cámara:")
    print(f"  Resolución: {width}x{height}")
    print(f"  FPS (Hardware): {camera_fps}")
    print("---------------------------------------")
    print("Sistema Activo y en Funcionamiento.")
    print("Controles del reproductor:")
    print("  - Muestra PALMA estable en la zona central para activar.")
    print("  - Una vez activo (verde), haz un gesto:")
    print("    - PUÑO -> Play / Pausa")
    print("    - SWIPE DERECHA / IZQUIERDA -> Siguiente / Anterior")
    print("    - PINZA (Pulgar e Índice extendidos) -> Control de volumen continuo")
    print("    - INDICE -> Acción adicional")
    print("  - Presiona 'F' para pantalla completa, 'Q' para salir.")
    print("---------------------------------------\n")

    # Configuración de ventana de OpenCV
    width_str = os.getenv("DEFAULT_WINDOW_WIDTH", "1024")
    height_str = os.getenv("DEFAULT_WINDOW_HEIGHT", "768")
    try:
        win_width = int(width_str)
        win_height = int(height_str)
    except ValueError:
        win_width, win_height = 1024, 768

    window_name = "AirDJ - Sistema Completo Integrado"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, win_width, win_height)

    # Variables para cálculo de FPS
    frame_count = 0
    fps_start_time = time.time()
    processing_fps = 0.0

    try:
        while True:
            current_time = time.monotonic()

            # Capturar frame
            ret, frame = camera.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            # Espejar el frame para comodidad de interacción
            frame = cv2.flip(frame, 1)

            # 1. Ejecutar Detección de Mano (Módulo 2)
            result = detector.detect(frame)

            # Inicializar variables de ciclo
            gesture_name = "NEUTRO"
            hand_center = None
            inside_zone = False
            swipe_gesture = None
            volume_value = None

            if result.detected:
                hand_center = result.center_normalized
                
                # Clasificar gesto estático (Módulo 3)
                gesture_result = gesture_recognizer.classify(result)
                
                # Clasificar gesto dinámico (Módulo 5)
                swipe_gesture = swipe_detector.update(result)

                # Clasificar gestos según mapeo del sistema y evaluar control de volumen (Módulo 6)
                # Evaluamos si es el gesto de pinza de volumen (pulgar e índice extendidos, otros cerrados)
                is_volume_gesture = False
                if gesture_result.extended_fingers:
                    extended = set(gesture_result.extended_fingers)
                    if "thumb" in extended and "index" in extended and len(extended) == 2:
                        is_volume_gesture = True

                if is_volume_gesture:
                    gesture_name = "VOLUMEN"
                    volume_value = volume_controller.update(result.landmarks)
                else:
                    if gesture_result.label == GestureLabel.PALMA:
                        gesture_name = "PALMA"
                    elif gesture_result.label == GestureLabel.PUNO:
                        gesture_name = "PUÑO"
                    elif gesture_result.label == GestureLabel.INDICE:
                        gesture_name = "INDICE"
                    else:
                        gesture_name = "NEUTRO"

                # Verificar si el centro de la mano está en la zona central de comandos
                if hand_center is not None:
                    hx, hy = hand_center
                    if zone_x_min <= hx <= zone_x_max and zone_y_min <= hy <= zone_y_max:
                        inside_zone = True

            # 2. Actualizar controlador de Activación (Módulo 4)
            act_result = activation_controller.update(
                gesture=gesture_name,
                hand_center=hand_center,
                timestamp=current_time,
                inside_zone=inside_zone
            )

            # 3. Determinar el comando actual a enviar a la máquina de estados (Módulo 7)
            # Prioridad: Swipes dinámicos sobre gestos estáticos
            command_to_send = swipe_gesture if swipe_gesture else gesture_name
            val_to_send = volume_value if command_to_send == "VOLUMEN" else None

            # 4. Actualizar Máquina de Estados (Módulo 7)
            state_result = state_machine.update(
                activation_result=act_result,
                command=command_to_send,
                command_value=val_to_send,
                timestamp=current_time
            )

            # Sincronizar el reinicio del activador temporal si la máquina vuelve a bloquearse
            if state_result.state.value == "BLOQUEADO" and activation_controller.activation_emitted:
                activation_controller.reset()

            # 5. Ejecutar la acción si corresponde (Módulo 8)
            # La máquina de estados emite la acción en state_result.action
            if state_result.action:
                if state_result.action == "CONTROL_VOLUMEN":
                    # Ajuste continuo de volumen
                    media_controller.set_volume(state_result.volume_value)
                else:
                    # Comandos multimedia discretos
                    media_controller.execute(state_result.action)

            # Calcular FPS de procesamiento
            frame_count += 1
            elapsed_time = time.time() - fps_start_time
            if elapsed_time >= 0.5:
                processing_fps = frame_count / elapsed_time
                frame_count = 0
                fps_start_time = time.time()

            # 6. Renderizar Interfaz Visual y Feedback en pantalla (Módulo 9)
            # Mapeamos SystemState de StateMachine a SystemState de Interface para coincidir con la firma del render
            ui_state = UISystemState(state_result.state.value)

            frame = interface.render(
                frame=frame,
                state=ui_state,
                activation_progress=state_result.activation_progress,
                time_left=state_result.time_left,
                volume_value=state_result.volume_value,
                detected_gesture=gesture_name if result.detected else "NINGUNO",
                executed_command=state_result.action,
                landmarks=result.landmarks if result.detected else None,
                command_zone=command_zone_coords,
                fps=processing_fps
            )

            # Mostrar frame
            cv2.imshow(window_name, frame)

            # Detección de teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("Cerrando la aplicación por orden del usuario.")
                break
            elif key == ord('f') or key == ord('F'):
                is_fs = cv2.getWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN)
                if is_fs == cv2.WINDOW_FULLSCREEN:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    except KeyboardInterrupt:
        print("\nAplicación interrumpida.")
    finally:
        # Liberación final de recursos
        camera.close()
        detector.close()
        cv2.destroyAllWindows()
        print("Recursos liberados. AirDJ finalizado.")

if __name__ == "__main__":
    main()
