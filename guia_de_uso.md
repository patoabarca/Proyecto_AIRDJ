# Guía de Uso de AirDJ: Gestos, Funciones y Pruebas

**AirDJ** es un sistema de visión artificial en Python que permite controlar funciones de reproducción multimedia (Spotify, reproductores multimedia locales, volumen del sistema operativo) mediante gestos de una sola mano capturados por la cámara web.

Este documento detalla los gestos disponibles, cómo interactuar con el sistema paso a paso y cómo ejecutar las distintas herramientas de prueba.

---

## 1. Configuración Rápida

Antes de comenzar, asegúrate de activar el entorno virtual e instalar las dependencias:

```powershell
# 1. Activar el entorno virtual (PowerShell)
.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar la aplicación
python main.py
```

*Nota: Si tienes más de una cámara conectada (por ejemplo, una integrada y una USB), la terminal te presentará un menú interactivo para seleccionar el índice del dispositivo. También puedes forzar un índice específico usando `python main.py -c 1`.*

---

## 2. Flujo de Estados del Sistema

AirDJ utiliza una **máquina de estados** de seguridad para evitar que movimientos accidentales de la mano ejecuten comandos no deseados en tu reproductor.

1. **BLOQUEADO (Color Rojo)**: El sistema está apagado/en reposo. No responde a ningún comando discreto ni de volumen.
2. **ACTIVANDO (Color Amarillo)**: Se inicia cuando el usuario realiza el gesto activador. Muestra un porcentaje de progreso (0% a 100%).
3. **ACTIVO (Color Verde)**: El sistema se desbloquea. Se inicia un temporizador de **5 segundos** (timeout). Tienes esta ventana de tiempo para realizar un gesto de comando.
4. **EJECUTANDO (Color Cian)**: Se activa brevemente al detectar un gesto de comando válido y ejecutar la acción multimedia.
5. **COOLDOWN (Color Naranja)**: Un período de espera de **1.5 segundos** post-comando. Durante este tiempo no se detectan nuevos gestos para evitar ejecuciones repetidas. Al finalizar, el sistema regresa al estado **BLOQUEADO**.

---

## 3. Catálogo de Gestos y Acciones

| Gesto Visual | Nombre Técnico | Estado Requerido | Acción Ejecutada | Descripción del Movimiento |
| :--- | :--- | :--- | :--- | :--- |
| **Palma Abierta** | `PALMA` | `BLOQUEADO` | **Desbloquear Sistema** | Coloca la palma de la mano abierta **estática** dentro del recuadro verde central (**Zona de Comandos**) durante **1.5 segundos**. |
| **Puño Cerrado** | `PUÑO` | `ACTIVO` | **Play / Pausa** | Cierra todos los dedos formando un puño dentro de la pantalla. Alterna la reproducción de música. |
| **Desplazamiento Rápido Derecha** | `SWIPE_DERECHA` | `ACTIVO` | **Siguiente Canción** | Mueve la mano rápidamente de izquierda a derecha. Pasa a la siguiente pista de música. |
| **Desplazamiento Rápido Izquierda** | `SWIPE_IZQUIERDA` | `ACTIVO` | **Canción Anterior** | Mueve la mano rápidamente de derecha a izquierda. Regresa a la pista de música anterior. |
| **Dedo Índice Levantado** | `INDICE` | `ACTIVO` | **Acción Adicional** | Levanta únicamente el dedo índice manteniendo los demás cerrados. |
| **Pinza (Pulgar e Índice)** | `VOLUMEN` | `ACTIVO` | **Control de Volumen Continuo** | Extiende el pulgar y el índice (los otros tres dedos cerrados) y varía la distancia entre sus puntas. |

---

## 4. Funcionamiento Detallado de los Gestos Clave

### A. Cómo Activar el Sistema (Gesto de Palma)
* Coloca tu mano frente a la cámara mostrando la palma abierta con los 5 dedos extendidos.
* Asegúrate de que el centro geométrico de la mano (indicado con un punto azul en pantalla si estás en modo debug) esté dentro del **recuadro central verde** denominado **ZONA DE COMANDOS**.
* Mantén la mano quieta. Si te mueves muy rápido o te sales de la zona, el progreso de activación se reiniciará a 0% inmediatamente.
* Al completarse el 100% de la barra amarilla, la interfaz se volverá verde y escucharás/verás que el sistema está **ACTIVO**.

### B. Cómo Ajustar el Volumen (Gesto de Pinza)
* Una vez que el sistema esté **ACTIVO** (pantalla en verde), realiza la forma de pinza: extiende únicamente el dedo pulgar y el índice, y cierra los dedos medio, anular y meñique.
* **Ajuste continuo:** Junta las puntas de los dedos para bajar el volumen (llegando a 0%) o sepáralos ampliamente para subirlo (llegando a 100%).
* **Sin límite de tiempo:** Mientras mantengas el gesto de pinza de volumen, el temporizador de apagado de 5 segundos se detiene/congela, permitiéndote calibrar el volumen todo el tiempo que desees.
* **Salida:** Al cerrar el gesto de volumen o retirar la mano, el sistema aplica la última posición, entra en cooldown (1.5s) y se bloquea automáticamente por seguridad.

---

## 5. Control Real vs Simulado (Dry-Run)

Para evitar alterar accidentalmente el volumen de tu computadora o cambiar de canción mientras estás programando o calibrando el sensor:

* **Modo Simulado (Dry-Run - Por Defecto)**: Registra los eventos en la consola e interfaz, pero no interactúa con el sistema operativo de tu computadora.
* **Modo Real**: Envía las pulsaciones multimedia y de volumen directo al sistema operativo.
  * Para activarlo, puedes modificar la variable `MEDIA_CONTROLLER_DRY_RUN` en tu archivo `.env` a `False` o ejecutar la aplicación con la bandera de comandos:
    ```powershell
    python main.py -d
    ```

---

## 6. Scripts de Prueba Disponibles

Puedes probar cada parte del sistema de forma aislada ejecutando sus correspondientes scripts de prueba:

* **Para probar la cámara web y el volumen en tiempo real (Módulo 6)**:
  Muestra una barra lateral de volumen y una línea conectando tu pulgar e índice con métricas en tiempo real.
  ```powershell
  python demo_volume.py
  ```
* **Para probar la Máquina de Estados por teclado (Módulo 7)**:
  Permite usar las flechas del teclado y combinaciones de teclas para simular eventos de gestos y ver cómo transiciona el sistema.
  ```powershell
  python tests/demo_state_machine.py
  ```
* **Para probar la Interfaz Gráfica (Módulo 9)**:
  Ejecuta una simulación automática animada paso a paso que recrea todo el recorrido visual del HUD.
  ```powershell
  python tests/demo_interface.py
  ```
* **Para correr todas las pruebas unitarias automatizadas**:
  Corre los 135 tests matemáticos y lógicos del sistema completo:
  ```powershell
  python -m unittest discover -s tests
  ```
