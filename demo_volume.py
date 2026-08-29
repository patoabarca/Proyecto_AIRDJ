import cv2
import time
import sys
import os
from dotenv import load_dotenv

from src.camera import CameraManager
from src.hand_detector import HandDetector, HandLandmark
from src.volume_control import VolumeController

def main():
    # Cargar variables de entorno si existen
    load_dotenv()
    
    # 1. Buscar cámaras disponibles o usar la por defecto
    print("Buscando cámaras disponibles...")
    available = CameraManager.find_available_cameras(max_to_check=5)
    camera_index = 0
    if available:
        camera_index = available[0][0]
        print(f"Cámara seleccionada automáticamente: {available[0][1]} (Índice: {camera_index})")
    else:
        print("[ADVERTENCIA] No se detectaron cámaras activas. Intentando índice 0 por defecto.")

    # 2. Inicializar componentes
    camera = CameraManager(device_index=camera_index)
    if not camera.open():
        print(f"[ERROR] No se pudo abrir la cámara en el índice {camera_index}.", file=sys.stderr)
        sys.exit(1)

    # Detector de manos (Módulo 2)
    detector = HandDetector(static_image_mode=False, max_num_hands=1)
    
    # Controlador de volumen (Módulo 6)
    # Valores por defecto calibrados: min=0.2, max=1.0, alpha=0.15
    volume_controller = VolumeController(min_distance=0.2, max_distance=1.0, smooth_alpha=0.15)

    print("\n=======================================================")
    print("   AirDJ - Demo Interactiva del Módulo 6: Volumen")
    print("=======================================================")
    print("Controles:")
    print("  - Presiona 'q' para salir de la demo.")
    print("  - Junta el pulgar y el índice -> Volumen decrece a 0%.")
    print("  - Separa el pulgar y el índice -> Volumen crece a 100%.")
    print("  - Acerca o aleja la mano -> El volumen se mantiene estable.")
    print("=======================================================\n")

    # Para cálculo de FPS del procesamiento
    prev_time = time.time()
    
    # Dimensiones por defecto para visualización
    window_width = int(os.getenv("DEFAULT_WINDOW_WIDTH", "1024"))
    window_height = int(os.getenv("DEFAULT_WINDOW_HEIGHT", "768"))
    
    window_name = "AirDJ - Control de Volumen (Modulo 6)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, window_width, window_height)

    try:
        while True:
            # Capturar frame de la cámara
            frame = camera.read()
            if frame is None:
                print("[ERROR] Frame no disponible o inválido.", file=sys.stderr)
                break

            # Espejar el frame para que se sienta natural (efecto espejo)
            frame = cv2.flip(frame, 1)

            # Detección de la mano
            result = detector.detect(frame)
            
            # Actualizar volumen y obtener el valor suavizado
            # Si no se detecta mano, pasamos una lista vacía para verificar el comportamiento seguro
            if result.detected:
                volume = volume_controller.update(result.landmarks)
            else:
                volume = volume_controller.update([])

            # Dibujar marcas de depuración de landmarks de la mano si se detectó
            if result.detected and result.landmarks:
                frame = detector.draw_landmarks(frame, result, draw_center=False)
                
                # Obtener landmarks específicos de forma segura
                wrist = None
                thumb_tip = None
                index_mcp = None
                index_tip = None
                
                for lm in result.landmarks:
                    if lm.index == HandLandmark.WRIST:
                        wrist = lm
                    elif lm.index == HandLandmark.THUMB_TIP:
                        thumb_tip = lm
                    elif lm.index == HandLandmark.INDEX_FINGER_MCP:
                        index_mcp = lm
                    elif lm.index == HandLandmark.INDEX_FINGER_TIP:
                        index_tip = lm

                if thumb_tip and index_tip and wrist and index_mcp:
                    # Dibujar línea entre la punta del pulgar y el índice
                    cv2.line(
                        frame,
                        (thumb_tip.pixel_x, thumb_tip.pixel_y),
                        (index_tip.pixel_x, index_tip.pixel_y),
                        (255, 255, 0),  # Color cian/celeste
                        2,
                        cv2.LINE_AA
                    )
                    # Dibujar un pequeño círculo amarillo en el punto medio de la línea
                    mid_x = int((thumb_tip.pixel_x + index_tip.pixel_x) / 2)
                    mid_y = int((thumb_tip.pixel_y + index_tip.pixel_y) / 2)
                    cv2.circle(frame, (mid_x, mid_y), 4, (0, 255, 255), -1, cv2.LINE_AA)

                    # Calcular métricas para el overlay informativo
                    d_control = volume_controller.calculate_distance(thumb_tip, index_tip)
                    d_ref = volume_controller.calculate_distance(wrist, index_mcp)
                    d_norm = volume_controller.normalize_distance(d_control, d_ref)
                    
                    # Dibujar información detallada de la calibración
                    cv2.putText(frame, f"Dist. Pulgar-Indice: {d_control:.1f} px", (30, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, f"Dist. Referencia: {d_ref:.1f} px", (30, 110), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, f"Dist. Normalizada: {d_norm:.3f}", (30, 140), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

            # Dibujar la barra de volumen y el indicador
            # Fondo del indicador de volumen (barra vertical)
            # Dibujaremos la barra a la derecha de la pantalla
            h, w, _ = frame.shape
            bar_x = w - 60
            bar_y_start = 150
            bar_y_end = h - 150
            bar_height = bar_y_end - bar_y_start

            # Dibujar fondo de la barra (Gris oscuro)
            cv2.rectangle(frame, (bar_x, bar_y_start), (bar_x + 30, bar_y_end), (50, 50, 50), -1, cv2.LINE_AA)
            cv2.rectangle(frame, (bar_x, bar_y_start), (bar_x + 30, bar_y_end), (200, 200, 200), 2, cv2.LINE_AA)

            if volume is not None:
                # El volumen está entre 0.0 y 100.0
                fill_height = int((volume / 100.0) * bar_height)
                # Dibujar barra llena (de abajo hacia arriba, color verde dinámico según nivel)
                color = (0, 255, 0)  # Verde por defecto
                if volume > 80.0:
                    color = (0, 0, 255)  # Rojo si es muy alto
                elif volume < 20.0:
                    color = (255, 0, 0)  # Azul si es muy bajo

                cv2.rectangle(frame, (bar_x, bar_y_end - fill_height), (bar_x + 30, bar_y_end), color, -1, cv2.LINE_AA)
                
                # Texto con el porcentaje de volumen
                cv2.putText(frame, f"{int(volume)}%", (bar_x - 10, bar_y_start - 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                # Si no hay volumen calculado
                cv2.putText(frame, "---", (bar_x - 10, bar_y_start - 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2, cv2.LINE_AA)
                cv2.putText(frame, "Mano no detectada", (30, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv2.LINE_AA)

            # Calcular FPS reales
            current_time = time.time()
            fps = 1.0 / (current_time - prev_time)
            prev_time = current_time
            
            # Dibujar etiqueta de estado del Módulo y FPS
            cv2.putText(frame, f"AirDJ Modulo 6: CONTROL DE VOLUMEN (Rama airdj_pato)", (30, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, f"FPS: {fps:.1f}", (30, h - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

            # Mostrar frame
            cv2.imshow(window_name, frame)

            # Tecla de salida
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nDemo interrumpida por el usuario.")
    finally:
        # Liberar recursos
        camera.close()
        detector.close()
        cv2.destroyAllWindows()
        print("Demo finalizada correctamente.")

if __name__ == "__main__":
    main()
