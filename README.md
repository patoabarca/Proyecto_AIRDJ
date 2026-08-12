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
