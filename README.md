# AirDJ — Módulo 1: Adquisición de Video y Cámara

Este es el Módulo 1 del proyecto **AirDJ**, un sistema de visión artificial para controlar un reproductor multimedia mediante gestos de la mano.

El objetivo de este módulo es establecer la adquisición de video desde una cámara web utilizando OpenCV, comprobar el estado del dispositivo, calcular FPS de procesamiento en tiempo real y mostrar la información en una interfaz superpuesta sobre el video.

## Requisitos previos

- Python 3.13.x (o una versión compatible)
- Cámara web integrada o externa conectada

## Estructura del Proyecto (Módulo 1)

```text
AirDJ/
├── .venv/               # Entorno virtual (excluido en git)
├── src/
│   ├── __init__.py      # Inicializador del paquete
│   └── camera.py        # Clase CameraManager
├── tests/               # Carpeta para pruebas futuras
├── main.py              # Script coordinador de ejecución
├── requirements.txt     # Dependencias de Python
├── .gitignore           # Archivos omitidos en el repositorio
└── README.md            # Este archivo
```

## Configuración del Entorno

1. Abre una terminal en el directorio raíz de `AirDJ`.
2. Crea el entorno virtual Python:
   ```bash
   python -m venv .venv
   ```
3. Activa el entorno virtual:
   - **Windows (PowerShell):**
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **Linux / macOS:**
     ```bash
     source .venv/bin/activate
     ```
4. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución del Proyecto

Para correr la aplicación de visualización en tiempo real y probar la cámara:

```bash
python main.py
```

### Selección de Cámara (Múltiples Cámaras)

El sistema incluye detección automática de cámaras conectadas:
1. **Una sola cámara**: El sistema la detecta y abre la transmisión inmediatamente.
2. **Múltiples cámaras**: Se muestra un menú interactivo en la consola listando los índices disponibles (ej. integrada y webcam externa) y solicita que ingreses el número del dispositivo a utilizar. Si presionas Enter sin ingresar texto, usará la primera cámara detectada.
3. **Bypass por línea de comandos**: Puedes saltarte la búsqueda y forzar el uso de una cámara en particular pasando el argumento `-c` o `--camera`:
   ```bash
   python main.py -c 1
   ```

### Controles de la Ventana

- Presiona la tecla **`Q`** o **`q`** en el teclado con la ventana del reproductor activa para salir de forma controlada.

## Información en Pantalla

Durante la ejecución, la pantalla mostrará una superposición informativa con:
- Título: **AirDJ — Módulo 1**
- Resolución del frame capturado
- FPS configurados en la cámara
- FPS reales de procesamiento en la máquina local
- Tecla para salir

---

# AirDJ — Módulo 2: Detección de Mano y Landmarks

Este es el Módulo 2 del proyecto **AirDJ**. Su objetivo principal es detectar la mano en el frame capturado por la cámara web, extraer sus 21 puntos de referencia (landmarks) y proporcionar estos datos a través de una interfaz limpia y desacoplada de la biblioteca subyacente.

> [!IMPORTANT]
> El Módulo 2 únicamente detecta la mano y obtiene sus landmarks. El reconocimiento de gestos (tanto estáticos como dinámicos), la máquina de estados y las acciones multimedia pertenecen a módulos posteriores del proyecto.

## Estructura del Proyecto Actualizada

```text
AirDJ/
├── .venv/               # Entorno virtual
├── src/
│   ├── __init__.py
│   ├── camera.py        # Módulo 1 (Adquisición de video)
│   └── hand_detector.py # Módulo 2 (Detector de manos y landmarks) [NUEVO]
├── tests/
│   └── test_hand_detector.py # Pruebas unitarias para el detector [NUEVO]
├── main.py              # Script coordinador de ejecución (Integrado con Módulos 1 y 2)
├── requirements.txt     # Dependencias (incluye mediapipe)
├── hand_landmarker.task # Archivo de modelo para MediaPipe Tasks (Autodescargable) [NUEVO]
└── README.md
```

## Dependencias
* **MediaPipe**: Usada para la detección robusta del esqueleto de la mano. Se utiliza la API moderna `mediapipe.tasks` para asegurar compatibilidad total con Python 3.13 en entornos Windows.
* **OpenCV**: Usada para dibujo de depuración, superposiciones HUD y manejo de frames.

---

## Contrato de Salida de `HandDetector`

Para evitar acoplar los módulos futuros a objetos internos de MediaPipe, `HandDetector` actúa como una capa de abstracción. Su firma es:

### Entrada
* `frame`: Un array de NumPy (`np.ndarray`) en formato **BGR** (el predeterminado de OpenCV).

### Salida
Devuelve un objeto de tipo `HandDetectionResult` con las siguientes propiedades:

* **`detected`** (`bool`): Indica si hay una mano visible y detectada en el frame actual.
* **`landmarks`** (`List[LandmarkPoint]`): Lista de 21 puntos correspondientes al esqueleto de la mano. Si `detected` es `False`, la lista estará vacía.
* **`center_normalized`** (`Tuple[float, float]`): Coordenadas $(x, y)$ normalizadas (entre $0.0$ y $1.0$) del centro de gravedad geométrico de la mano.
* **`center_pixel`** (`Tuple[int, int]`): Coordenadas $(x, y)$ en píxeles de la imagen del centro de gravedad.

### Estructura de `LandmarkPoint`
Cada landmark en la lista contiene:
* `index` (`int`): Índice de punto del 0 al 20 (según el estándar de MediaPipe).
* `x`, `y`, `z` (`float`): Coordenadas espaciales normalizadas.
* `pixel_x`, `pixel_y` (`int`): Coordenadas mapeadas al tamaño real del frame (con prevención de desbordamiento de límites).

### Enumeración `HandLandmark`
Se proporciona la enumeración `HandLandmark` para acceder a los puntos sin necesidad de recordar los números de índice:
```python
from src.hand_detector import HandLandmark

# Acceso directo al índice de la punta del dedo índice
punto_indice = result.landmarks[HandLandmark.INDEX_FINGER_TIP]
print(f"Píxeles: ({punto_indice.pixel_x}, {punto_indice.pixel_y})")
```

---

## Ejecución de Pruebas

### 1. Ejecutar Pruebas Unitarias (Automáticas)
Para correr las pruebas unitarias que validan la matemática de conversión de píxeles, el cálculo del baricentro de la mano y la gestión de frames vacíos o nulos sin necesidad de usar la cámara:

```bash
python -m unittest discover -s tests
```

### 2. Prueba Manual con Webcam
Para ejecutar la aplicación de prueba con cámara web integrada:

```bash
python main.py
```

#### Interpretación de Resultados Manuales:
* Al colocar tu mano frente a la cámara dentro de la ventana de video:
  * El estado en el HUD cambiará a **`Estado: MANO DETECTADA`** (en color verde).
  * Se dibujará un esqueleto de líneas verdes uniendo los puntos de tus dedos.
  * Se dibujarán círculos rojos en cada articulación/punto.
  * Se dibujará un círculo azul con borde blanco en el **centro geométrico** de tu mano.
* Al retirar la mano de la cámara:
  * El estado cambiará a **`Estado: SIN MANO`** (en color rojo).
  * Se eliminarán todos los dibujos de landmarks de manera inmediata para evitar persistencias del frame anterior.

<!-- scrum-master-ai:start -->
## Trabajar con Scrum Master AI

Este repo reporta avance a una instancia de Scrum Master AI. Para empezar, decile a
tu asistente de IA (Claude Code u otro) algo como:

> Leé la documentación de este proyecto.

Va a encontrar las instrucciones en `scrumDocs/EMPEZA-ACA-SEGUN-TU-ROL.md` y lo primero que te va
a pedir es tu **API key** de Scrum Master AI, para identificarte según tu rol (te la
genera tu Project Manager desde "Usuarios Activos"). Con eso ya puede empezar a
trabajar de forma interactiva contra la app -- no hace falta memorizar ningún
comando.
<!-- scrum-master-ai:end -->
