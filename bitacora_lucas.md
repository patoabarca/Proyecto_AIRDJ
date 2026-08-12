# Bitácora de Actividades - Lucas (Proyecto AirDJ)

Este documento registra el progreso, las tareas completadas, los desafíos encontrados y el estado del desarrollo de **AirDJ** llevado a cabo por Lucas.

---

## 📋 Resumen del Proyecto
**AirDJ** es un sistema de visión por computadora en Python para controlar un reproductor multimedia mediante gestos de la mano.

* **Stack:** Python, OpenCV, MediaPipe (Hands), NumPy.
* **Rama de trabajo:** `airdj_lucas`

---

## 🚀 Hoja de Ruta y Estado de Tareas

A continuación se detallan las etapas planificadas según el documento `Proyecto_AirDJ.pdf` y su estado actual:

### [x] Etapa 1 — Video y Cámara
*Requerimientos: RF01*
- [x] Configurar el entorno de Python local y verificar dependencias (`opencv-python`).
- [x] Desarrollar script básico para abrir la cámara web.
- [x] Obtener y visualizar la resolución y FPS de captura.
- [x] Mostrar ventana de visualización en tiempo real.
- **Notas de progreso:** Módulo 1 heredado de la rama `main` y funcionando correctamente.

### [x] Etapa 2 — Detección de Mano y Landmarks
*Requerimientos: RF02*
- [x] Instalar e integrar `mediapipe`.
- [x] Detectar la mano en el cuadro de video y dibujar los landmarks (puntos de referencia).
- [x] Normalizar coordenadas para facilitar los cálculos matemáticos.
- **Notas de progreso:** Se implementó y aisló el detector en `src/hand_detector.py` utilizando la API moderna de MediaPipe Tasks para garantizar compatibilidad con Python 3.13 en Windows. Se descargó de forma autocurativa el archivo `hand_landmarker.task`.

### [ ] Etapa 3 — Gestos Estáticos
*Requerimientos: RF03*
- [ ] Definir lógica de detección para "Palma abierta".
- [ ] Definir lógica de detección para "Puño cerrado".
- [ ] Definir lógica de detección para "Índice levantado".
- [ ] Probar estabilidad del reconocimiento en distintas distancias.
- **Notas de progreso:**

### [ ] Etapa 4 — Activación y Zona de Comandos
*Requerimientos: RF06, RF07*
- [ ] Definir y dibujar en pantalla la "Zona de comandos" (cuadro delimitador).
- [ ] Validar que la palma abierta se mantenga estable dentro de esa zona durante 1.5 segundos.
- [ ] Mostrar visualmente una barra de carga o progreso de activación.
- **Notas de progreso:**

### [ ] Etapa 5 — Máquina de Estados y Ventana Temporal
*Requerimientos: RF06*
- [ ] Implementar la máquina de estados: `BLOQUEADO`, `ACTIVANDO`, `ACTIVO`, `EJECUTANDO` y `COOLDOWN`.
- [ ] Configurar ventana de comandos de 5 segundos al activarse (espera de gesto).
- [ ] Implementar el bloqueo automático por timeout si no hay gestos en ese tiempo.
- **Notas de progreso:**

### [ ] Etapa 6 — Tracking y Gestos Dinámicos
*Requerimientos: RF04, RF07*
- [ ] Almacenar posiciones históricas de la mano (varios frames de memoria).
- [ ] Implementar la detección de desplazamientos rápidos (Swipes):
  - [ ] Swipe derecha (Siguiente canción).
  - [ ] Swipe izquierda (Canción anterior).
- [ ] Definir umbrales mínimos para evitar falsos positivos por movimientos involuntarios.
- **Notas de progreso:**

### [ ] Etapa 7 — Control de Volumen
*Requerimientos: RF05*
- [ ] Medir distancia relativa entre el pulgar y el dedo índice.
- [ ] Normalizar la distancia a un rango porcentual (0% - 100%).
- [ ] Mostrar visualmente la barra de volumen en pantalla.
- **Notas de progreso:**

### [ ] Etapa 8 — Validación y Cooldown
*Requerimientos: RF07*
- [ ] Bloquear la ejecución repetida de un mismo gesto mientras se mantiene activo.
- [ ] Implementar período de `COOLDOWN` (espera temporal) posterior a una acción multimedia.
- [ ] Asegurar el retorno suave al estado `BLOQUEADO`.
- **Notas de progreso:**

### [ ] Etapa 9 — Integración Multimedia y Feedback
*Requerimientos: RF08, RF09*
- [ ] Vincular los gestos con las acciones del reproductor (utilizando bibliotecas del sistema operativo como `pyautogui` o APIs multimedia).
  - Puño $\rightarrow$ Play/Pausa
  - Swipe Derecha $\rightarrow$ Siguiente
  - Swipe Izquierda $\rightarrow$ Anterior
  - Pinza Pulgar-Índice $\rightarrow$ Control de Volumen
  - Índice Levantado $\rightarrow$ Función configurable (Favorito/Repetición)
- [ ] Mostrar en pantalla el feedback visual del estado del sistema y la acción ejecutada.
- **Notas de progreso:**

### [ ] Etapa 10 — Pruebas y Calibración
*Requerimientos: Todos*
- [ ] Realizar pruebas con diferentes niveles de iluminación.
- [ ] Ajustar tiempos de activación y umbrales de gestos dinámicos.
- [ ] Medir la tasa de falsos positivos y optimizar la latencia del sistema.
- **Notas de progreso:**

---

## 📝 Registro Diario de Actividades

### 12 de Agosto de 2026
- **Fusión de Código:** Se realizó la fusión inicial de `main` en `airdj_lucas` permitiendo historias no relacionadas.
- **Módulo 2 (Detección de Mano):** Se creó la clase `HandDetector` en `src/hand_detector.py` y las estructuras de datos `LandmarkPoint` y `HandDetectionResult` para independizar el código del proyecto de MediaPipe.
- **Compatibilidad Python 3.13:** Ante la falta del módulo `solutions` tradicional en las compilaciones de MediaPipe para Python 3.13 en Windows, se adaptó el código para utilizar la API de `mediapipe.tasks.python.vision.HandLandmarker`. Se agregó lógica de descarga autocurativa para el archivo del modelo `hand_landmarker.task`.
- **Integración con Cámara:** Se integró el detector con `main.py` de modo que dibuja los landmarks de la mano, conexiones esqueléticas y centro de la mano, además de reflejar en tiempo real el estado de detección ("MANO DETECTADA" / "SIN MANO") en el HUD.
- **Pruebas Unitarias:** Se implementaron pruebas automáticas en `tests/test_hand_detector.py` evaluando la conversión matemática de píxeles, cálculo de centro y tratamiento de frames nulos. Todos los tests pasaron exitosamente.
- **Contrato de Datos:** Se documentó detalladamente el formato de entrada y salida del Módulo 2 en el `README.md` del proyecto.
