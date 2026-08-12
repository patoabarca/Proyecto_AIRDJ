import cv2
import time
import sys
import argparse
import os
from dotenv import load_dotenv
from src.camera import CameraManager

def parse_args():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="AirDJ - Módulo 1: Adquisición de Video")
    parser.add_argument(
        "-c", "--camera",
        type=int,
        default=None,
        help="Indice de la camara a utilizar (ej. 0, 1, 2)."
    )
    return parser.parse_args()

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Parse CLI arguments
    args = parse_args()
    camera_index = args.camera

    # If camera index wasn't specified via CLI, check environment variable
    if camera_index is None:
        env_cam_index = os.getenv("DEFAULT_CAMERA_INDEX")
        if env_cam_index is not None and env_cam_index.strip() != "":
            try:
                camera_index = int(env_cam_index)
                print(f"Usando camara por defecto desde .env: {camera_index}")
            except ValueError:
                pass

    # If camera index wasn't specified via CLI, detect available webcams
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
                print(f"\nEntrada cancelada o no valida. Usando camara por defecto: {available[0][1]} (Indice: {default_index})")
                camera_index = default_index
    
    print(f"Iniciando CameraManager con camara indice: {camera_index}...")
    camera = CameraManager(device_index=camera_index)

    # Attempt to open the camera
    if not camera.open():
        print(f"[ERROR] No se pudo abrir la camara con indice {camera_index}. Verifica la conexion.", file=sys.stderr)
        sys.exit(1)

    # Retrieve camera hardware properties
    props = camera.get_properties()
    width = props["width"]
    height = props["height"]
    camera_fps = props["fps"]

    print("--- AirDJ: Propiedades de la Cámara ---")
    print(f"Resolución: {width}x{height}")
    print(f"FPS de la Cámara (Hardware): {camera_fps}")
    print("---------------------------------------")

    # Retrieve default window dimensions from environment variables
    width_str = os.getenv("DEFAULT_WINDOW_WIDTH", "1024")
    height_str = os.getenv("DEFAULT_WINDOW_HEIGHT", "768")
    try:
        win_width = int(width_str)
        win_height = int(height_str)
    except ValueError:
        win_width, win_height = 1024, 768

    # Create named window with WINDOW_NORMAL so it can be resized/maximized
    window_name = "AirDJ - Adquisicion de Video"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, win_width, win_height)

    # Variables for calculation of processing FPS
    frame_count = 0
    fps_start_time = time.time()
    processing_fps = 0.0

    try:
        while True:
            # Mark start of current frame processing cycle
            cycle_start = time.time()

            # Read frame from camera
            ret, frame = camera.read()
            if not ret or frame is None:
                print("[WARNING] Fallo al capturar el frame de la cámara.", file=sys.stderr)
                # Small pause to avoid CPU hogging in case of consecutive failures
                time.sleep(0.01)
                continue

            # Increment frame counter for processing FPS calculation
            frame_count += 1

            # Periodically update processing FPS (every 0.5 seconds to avoid UI flicker)
            elapsed_time = time.time() - fps_start_time
            if elapsed_time >= 0.5:
                processing_fps = frame_count / elapsed_time
                frame_count = 0
                fps_start_time = time.time()

            # --- RENDER OVERLAY HUD (Rich Aesthetics) ---
            # Create a semi-transparent background box for the HUD to guarantee readability
            hud_x1, hud_y1 = 15, 15
            hud_x2, hud_y2 = 360, 190
            
            overlay = frame.copy()
            cv2.rectangle(overlay, (hud_x1, hud_y1), (hud_x2, hud_y2), (0, 0, 0), -1)
            # Apply transparency (65% HUD box, 35% original frame)
            cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

            # Draw the HUD text lines
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.55
            thickness = 1
            color = (255, 255, 255) # White text

            lines = [
                "AirDJ - Modulo 1",
                f"Resolucion: {width} x {height}",
                f"FPS Camara: {camera_fps if camera_fps > 0 else 'N/A'}",
                f"FPS Procesamiento: {processing_fps:.1f}",
                "F = pantalla completa",
                "Q = salir"
            ]

            start_y = 40
            line_spacing = 25
            for i, line in enumerate(lines):
                # Accentuate the first title line with a different color (cyan-ish)
                line_color = (255, 255, 100) if i == 0 else color
                # Accentuate the exit prompt in yellow/orange
                if i == len(lines) - 1:
                    line_color = (100, 100, 255)

                cv2.putText(
                    frame, 
                    line, 
                    (hud_x1 + 15, start_y + (i * line_spacing)), 
                    font, 
                    font_scale, 
                    line_color, 
                    thickness, 
                    cv2.LINE_AA
                )

            # Show the video stream
            cv2.imshow(window_name, frame)

            # Key press detection (1ms wait time)
            # Check for 'Q' to exit, 'F' to toggle fullscreen
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("Solicitud de salida recibida de usuario.")
                break
            elif key == ord('f') or key == ord('F'):
                is_fs = cv2.getWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN)
                if is_fs == cv2.WINDOW_FULLSCREEN:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")

    finally:
        # Resource cleanup
        camera.release()
        cv2.destroyAllWindows()
        print("Recursos liberados. Programa finalizado correctamente.")

if __name__ == "__main__":
    main()
