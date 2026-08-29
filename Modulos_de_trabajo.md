# AirDJ — Plan de desarrollo modular

AIRDJ

Plan de desarrollo modular

Qué vamos a desarrollar, probar y entregar en cada etapa

Proyecto de visión artificial para control gestual de reproducción multimedia

# 1. OBJETIVO DE ESTE DOCUMENTO

Este documento organiza el desarrollo de AirDJ en módulos independientes. La idea es construir y validar cada parte por separado, evitando implementar todo el sistema de una sola vez. Cada módulo tiene una responsabilidad concreta, entradas y salidas definidas, pruebas propias y un criterio claro para considerarlo terminado.

La integración final se realizará únicamente cuando los módulos principales funcionen de forma aislada. Esto permite detectar errores con mayor facilidad, repartir tareas entre integrantes del equipo y mantener una arquitectura escalable.

# 2. FLUJO GENERAL DEL SISTEMA

CÁMARA
  ↓
ADQUISICIÓN DE FRAMES
  ↓
DETECCIÓN DE MANO + LANDMARKS
  ↓
RECONOCIMIENTO DE POSTURAS / MOVIMIENTOS
  ↓
GESTO DE ACTIVACIÓN + MÁQUINA DE ESTADOS
  ↓
VALIDACIÓN DEL COMANDO
  ↓
EJECUCIÓN MULTIMEDIA
  ↓
FEEDBACK VISUAL
  ↓
COOLDOWN Y REGRESO A BLOQUEADO

Lógica de seguridad prevista:

BLOQUEADO
  ↓
PALMA ABIERTA + ESTABLE + 1,5 s
  ↓
ACTIVO DURANTE 5 s
  ↓
GESTO VÁLIDO
  ↓
EJECUTAR UNA ACCIÓN
  ↓
COOLDOWN
  ↓
BLOQUEADO

# 3. ESTRUCTURA PROPUESTA DEL PROYECTO

AirDJ/
│
├── .venv/
├── src/
│   ├── __init__.py
│   ├── camera.py
│   ├── hand_detector.py
│   ├── static_gestures.py
│   ├── activation.py
│   ├── dynamic_gestures.py
│   ├── volume_control.py
│   ├── state_machine.py
│   ├── media_controller.py
│   └── interface.py
│
├── tests/
├── main.py
├── requirements.txt
└── README.md

# MÓDULO 0 — Preparación del entorno y estructura base

Objetivo. Dejar preparado el proyecto para trabajar de forma ordenada y reproducible antes de comenzar con visión artificial.

Requerimientos relacionados. Soporte general del proyecto; especialmente RNF de modularidad, legibilidad y escalabilidad.

Entrada principal. Equipo con Python y Visual Studio Code instalados.

Salida esperada. Proyecto AirDJ creado, entorno virtual activo y dependencias mínimas instaladas.

## Qué vamos a desarrollar

- Crear la carpeta raíz del proyecto.

- Crear el entorno virtual .venv.

- Seleccionar el intérprete del entorno virtual en Visual Studio Code.

- Crear las carpetas src/ y tests/.

- Crear requirements.txt y README.md.

- Instalar inicialmente solo OpenCV; MediaPipe se incorporará cuando llegue el módulo de mano.

- Verificar que python y pip utilizados pertenezcan al entorno virtual.

## Pruebas del módulo

- Abrir una terminal de VS Code y comprobar la ruta del intérprete.

- Ejecutar pip list y verificar que las dependencias estén dentro de .venv.

- Ejecutar un script mínimo de Python desde main.py.

## Resultado para darlo por terminado

El equipo puede clonar o copiar el proyecto, activar .venv y comenzar a trabajar sin mezclar instalaciones globales.

Archivo sugerido. .venv/, requirements.txt, README.md y estructura de carpetas.

# MÓDULO 1 — Cámara y adquisición de video

Objetivo. Abrir la webcam, capturar frames de forma continua y entregar imágenes utilizables por el resto del sistema.

Requerimientos relacionados. RF01 — Adquisición y procesamiento de video.

Entrada principal. Cámara conectada al equipo.

Salida esperada. Un frame válido por iteración, junto con información básica de resolución y FPS.

## Qué vamos a desarrollar

- Crear una clase CameraManager o estructura equivalente.

- Abrir la cámara y comprobar que esté disponible.

- Leer frames en un bucle continuo.

- Obtener ancho, alto y FPS reportados por la cámara.

- Calcular de manera opcional los FPS reales aproximados del procesamiento.

- Mostrar el video en una ventana de OpenCV.

- Permitir salida mediante la tecla Q.

- Liberar la cámara y cerrar correctamente las ventanas al finalizar.

- Manejar el error de cámara no disponible o frame inválido.

## Pruebas del módulo

- Mantener la cámara funcionando al menos 30 segundos sin errores.

- Verificar que la resolución informada coincida con la imagen obtenida.

- Cerrar con Q y confirmar que la cámara quede liberada.

- Probar comportamiento cuando el índice de cámara sea incorrecto.

## Resultado para darlo por terminado

Una ventana muestra el video en tiempo real y el módulo entrega frames estables a main.py sin lógica de gestos.

Archivo sugerido. src/camera.py

## Observaciones importantes

- No instalar ni usar MediaPipe todavía.

- main.py debe coordinar el uso de CameraManager, no contener toda la lógica de captura.

# MÓDULO 2 — Detección de mano y landmarks

Objetivo. Detectar una mano dentro del frame y extraer sus puntos de referencia para que los módulos posteriores puedan analizar postura y movimiento.

Requerimientos relacionados. RF02 — Detección y representación de la mano.

Entrada principal. Frame proveniente del Módulo 1.

Salida esperada. Estado de detección + landmarks normalizados o accesibles por nombre/índice.

## Qué vamos a desarrollar

- Instalar MediaPipe en esta etapa.

- Inicializar el detector de manos.

- Convertir el frame al formato requerido por la librería.

- Detectar la presencia de una mano.

- Obtener los landmarks de muñeca, dedos y puntas.

- Dibujar los 21 landmarks y conexiones sobre el frame para depuración.

- Obtener coordenadas normalizadas y, cuando sea necesario, convertirlas a píxeles.

- Calcular un centro aproximado de la mano para futuros módulos de tracking.

- Devolver None o estructura vacía cuando no haya mano.

## Pruebas del módulo

- Mostrar una mano abierta, cerrada y rotada sin exigir todavía reconocimiento de gesto.

- Mover la mano por distintos sectores de la imagen y comprobar que los landmarks la sigan.

- Retirar la mano y verificar que el sistema informe correctamente ausencia de detección.

- Probar a diferentes distancias razonables de la cámara.

## Resultado para darlo por terminado

AirDJ puede indicar si hay una mano y mostrar correctamente sus landmarks en tiempo real.

Archivo sugerido. src/hand_detector.py

## Observaciones importantes

- Este módulo no decide si la mano es palma, puño o índice; solo entrega datos geométricos.

# MÓDULO 3 — Reconocimiento de gestos estáticos

Objetivo. Interpretar la configuración de los landmarks en un frame y reconocer posturas predefinidas de la mano.

Requerimientos relacionados. RF03 — Reconocimiento de gestos estáticos.

Entrada principal. Landmarks entregados por el Módulo 2.

Salida esperada. Etiqueta de postura: PALMA, PUNO, INDICE o NEUTRO/None.

## Qué vamos a desarrollar

- Definir reglas geométricas para determinar qué dedos están extendidos o flexionados.

- Reconocer palma abierta.

- Reconocer puño cerrado.

- Reconocer índice levantado.

- Definir un estado neutro para configuraciones que no coincidan claramente con ningún gesto.

- Evitar depender de posiciones absolutas en píxeles cuando sea posible.

- Mostrar en pantalla la etiqueta detectada para depuración.

- Ajustar umbrales con varias pruebas y diferentes usuarios.

## Pruebas del módulo

- Repetir cada postura al menos 10 veces y observar la consistencia.

- Cambiar la distancia de la mano a la cámara.

- Probar pequeñas rotaciones y verificar hasta qué punto el gesto sigue siendo estable.

- Realizar movimientos naturales que no sean comandos y comprobar que se clasifiquen como NEUTRO cuando corresponda.

## Resultado para darlo por terminado

El sistema reconoce de forma estable las posturas básicas y las muestra en pantalla, sin ejecutar todavía acciones multimedia.

Archivo sugerido. src/static_gestures.py

## Observaciones importantes

- La palma abierta será reservada para activar AirDJ, por lo que no debe utilizarse como Play/Pausa.

# MÓDULO 4 — Gesto activador y validación temporal

Objetivo. Evitar que cualquier movimiento cotidiano sea interpretado como comando, exigiendo una activación deliberada antes de habilitar el sistema.

Requerimientos relacionados. Parte central de RF06 — Activación y control de estados; soporte de RF07 — Validación y prevención de activaciones accidentales.

Entrada principal. Etiqueta PALMA + posición/centro de la mano + tiempo.

Salida esperada. Evento ACTIVACION_CONFIRMADA o progreso de activación.

## Qué vamos a desarrollar

- Detectar cuándo comienza una palma abierta.

- Iniciar un temporizador de activación.

- Comprobar que la palma continúe visible durante aproximadamente 1,5 segundos.

- Comprobar que la mano permanezca suficientemente estable durante ese período.

- Cancelar y reiniciar el temporizador si cambia el gesto o la mano se mueve demasiado.

- Calcular porcentaje de progreso de activación.

- Generar el evento ACTIVACION_CONFIRMADA únicamente una vez al alcanzar el tiempo requerido.

- Preparar feedback visual: Activando... y barra de progreso.

## Pruebas del módulo

- Mostrar palma durante menos de 1,5 s: no debe activar.

- Mostrar palma durante 1,5 s pero moverla bruscamente: debe cancelar o reiniciar.

- Mantener palma estable durante el tiempo requerido: debe activar una sola vez.

- Repetir la prueba después de volver al estado bloqueado.

## Resultado para darlo por terminado

AirDJ puede diferenciar una palma accidental de una activación intencional y emitir un evento de activación confiable.

Archivo sugerido. src/activation.py

# MÓDULO 5 — Tracking y gestos dinámicos

Objetivo. Analizar la trayectoria de la mano a lo largo de varios frames para reconocer swipes laterales deliberados.

Requerimientos relacionados. RF04 — Reconocimiento de gestos dinámicos.

Entrada principal. Centro o punto de referencia de la mano durante una secuencia temporal.

Salida esperada. SWIPE_DERECHA, SWIPE_IZQUIERDA o None.

## Qué vamos a desarrollar

- Mantener un historial corto de posiciones de la mano.

- Registrar tiempo asociado a cada posición.

- Calcular desplazamiento horizontal total.

- Calcular desplazamiento vertical para descartar movimientos predominantemente verticales.

- Definir distancia mínima para considerar un swipe.

- Definir una ventana temporal máxima para distinguir un movimiento deliberado de un desplazamiento lento.

- Detectar dirección derecha/izquierda.

- Limpiar o reiniciar el historial después de un gesto reconocido.

## Pruebas del módulo

- Mover la mano lentamente: no debería generar swipe.

- Realizar un movimiento corto: no debería generar swipe.

- Realizar swipe amplio hacia derecha: debe detectar SWIPE_DERECHA.

- Realizar swipe amplio hacia izquierda: debe detectar SWIPE_IZQUIERDA.

- Realizar movimientos verticales y diagonales para comprobar falsos positivos.

## Resultado para darlo por terminado

El sistema reconoce los dos desplazamientos laterales solo cuando cumplen los criterios de distancia, tiempo y dirección.

Archivo sugerido. src/dynamic_gestures.py

# MÓDULO 6 — Control gestual de volumen

Objetivo. Transformar la distancia relativa entre pulgar e índice en un valor continuo de volumen.

Requerimientos relacionados. RF05 — Control gestual continuo del volumen.

Entrada principal. Landmarks de punta de pulgar e índice.

Salida esperada. Valor de volumen normalizado, por ejemplo entre 0 y 100%.

## Qué vamos a desarrollar

- Calcular distancia euclidiana entre pulgar e índice.

- Normalizar la medida para reducir el efecto de acercar o alejar la mano de la cámara.

- Definir distancia mínima y máxima útiles.

- Mapear el rango geométrico al rango 0-100%.

- Aplicar suavizado básico para evitar saltos bruscos entre frames.

- Mostrar una barra de volumen visual.

- Emitir valor de volumen solo cuando AirDJ esté en modo activo y el gesto de control sea válido.

## Pruebas del módulo

- Juntar los dedos y comprobar valor bajo.

- Separarlos progresivamente y comprobar crecimiento continuo.

- Mantener una distancia fija y comprobar estabilidad del porcentaje.

- Mover toda la mano hacia adelante/atrás y revisar que la normalización reduzca variaciones no deseadas.

## Resultado para darlo por terminado

La interfaz muestra un volumen estable y proporcional al gesto, aunque todavía puede no modificar el volumen real del sistema.

Archivo sugerido. src/volume_control.py

# MÓDULO 7 — Máquina de estados, timeout y cooldown

Objetivo. Coordinar toda la interacción de AirDJ y decidir cuándo los gestos deben ser ignorados, aceptados o bloqueados.

Requerimientos relacionados. RF06 — Activación y control de estados + RF07 — Validación y prevención de activaciones accidentales.

Entrada principal. Eventos provenientes de activación, gestos estáticos, gestos dinámicos y volumen.

Salida esperada. Estado actual de AirDJ + autorización o rechazo de comandos.

## Qué vamos a desarrollar

- Definir estados: BLOQUEADO, ACTIVANDO, ACTIVO, EJECUTANDO y COOLDOWN.

- Permanecer BLOQUEADO por defecto.

- Aceptar el evento ACTIVACION_CONFIRMADA para pasar a ACTIVO.

- Abrir una ventana de aproximadamente 5 segundos para recibir un comando.

- Aceptar un único comando válido durante la ventana activa.

- Pasar a EJECUTANDO cuando se confirme un comando.

- Pasar a COOLDOWN después de ejecutar para ignorar movimientos residuales.

- Volver a BLOQUEADO después del cooldown.

- Volver a BLOQUEADO por timeout si pasan los 5 segundos sin comando.

- Exponer el estado actual para que la interfaz pueda mostrarlo.

## Pruebas del módulo

- Realizar swipe estando BLOQUEADO: debe ignorarse.

- Activar correctamente y realizar un comando dentro de 5 s: debe aceptarse.

- Activar y no realizar ningún comando: debe bloquearse por timeout.

- Ejecutar un swipe y mover la mano de regreso: el cooldown debe impedir una segunda acción.

- Mantener un gesto después de ejecutar: no debe repetirse.

## Resultado para darlo por terminado

AirDJ se comporta como un sistema controlado por estados y no como un detector que ejecuta cualquier gesto observado.

Archivo sugerido. src/state_machine.py

## Observaciones importantes

- Este módulo es el cerebro lógico del proyecto y conviene probarlo incluso con eventos simulados antes de conectarlo al reproductor.

# MÓDULO 8 — Mapeo de comandos y control multimedia

Objetivo. Convertir los gestos validados en acciones reales sobre el reproductor o el sistema operativo.

Requerimientos relacionados. RF08 — Generación y ejecución de comandos multimedia.

Entrada principal. Comando lógico validado por la máquina de estados.

Salida esperada. Acción multimedia ejecutada.

## Qué vamos a desarrollar

- Definir un mapeo único entre gesto y comando.

- Asignar PUÑO a Play/Pausa.

- Asignar SWIPE_DERECHA a Siguiente.

- Asignar SWIPE_IZQUIERDA a Anterior.

- Asignar el gesto de pinza/distancia al control de volumen.

- Reservar INDICE para una función secundaria como favorito o repetición.

- Comenzar con una simulación: imprimir el comando en consola.

- Luego integrar teclas multimedia o una API/controlador apropiado del sistema.

- Manejar errores si la acción no puede ejecutarse.

## Pruebas del módulo

- Enviar comandos simulados sin cámara y verificar el mapeo.

- Probar Play/Pausa, Siguiente y Anterior de manera independiente.

- Probar que un único evento produzca una única acción.

- Comprobar que el volumen respete límites 0-100%.

## Resultado para darlo por terminado

Los comandos validados modifican efectivamente la reproducción multimedia.

Archivo sugerido. src/media_controller.py

# MÓDULO 9 — Interfaz visual y feedback

Objetivo. Mostrar al usuario qué está entendiendo AirDJ para que la interacción sea clara y demostrable.

Requerimientos relacionados. RF09 — Retroalimentación visual.

Entrada principal. Frame + estado de AirDJ + gesto detectado + comando ejecutado + métricas relevantes.

Salida esperada. Frame anotado con información visual comprensible.

## Qué vamos a desarrollar

- Mostrar estado BLOQUEADO.

- Mostrar progreso de activación.

- Mostrar estado ACTIVO y tiempo restante aproximado.

- Mostrar gesto reconocido.

- Mostrar comando ejecutado.

- Mostrar barra de volumen cuando corresponda.

- Dibujar landmarks opcionalmente en modo depuración.

- Mantener la interfaz simple para no tapar la mano ni dificultar la demo.

## Pruebas del módulo

- Verificar que cada cambio de estado sea visible.

- Ejecutar todos los gestos y comprobar que el mensaje mostrado coincida.

- Comprobar legibilidad con diferentes fondos e iluminación.

- Revisar que el feedback desaparezca o cambie cuando corresponde.

## Resultado para darlo por terminado

La demo permite entender visualmente cuándo AirDJ está bloqueado, activándose, activo, ejecutando y nuevamente bloqueado.

Archivo sugerido. src/interface.py

# 4. INTEGRACIÓN FINAL — main.py

main.py no debe contener los algoritmos de cada módulo. Su responsabilidad es crear los componentes, recibir el frame, pasar los datos de un módulo al siguiente y mantener el bucle principal de ejecución.

1. Abrir cámara
2. Leer frame
3. Detectar mano
4. Obtener landmarks
5. Reconocer postura y/o movimiento
6. Actualizar activación y máquina de estados
7. Si corresponde, obtener comando
8. Ejecutar acción multimedia
9. Dibujar feedback visual
10. Mostrar frame
11. Repetir hasta salir

# 5. ORDEN RECOMENDADO DE IMPLEMENTACIÓN

| Hito | Meta | Resultado | Módulos |
| --- | --- | --- | --- |
| Hito 1 | Base visual | Entorno + cámara + frames | Módulos 0 y 1 |
| Hito 2 | Ver la mano | Detección + landmarks | Módulo 2 |
| Hito 3 | Entender posturas | Palma, puño, índice | Módulo 3 |
| Hito 4 | Despertar AirDJ | Palma estable + temporizador | Módulo 4 |
| Hito 5 | Entender movimientos | Swipes laterales | Módulo 5 |
| Hito 6 | Control continuo | Pinza/distancia + volumen | Módulo 6 |
| Hito 7 | Control seguro | Estados + timeout + cooldown | Módulo 7 |
| Hito 8 | Controlar música | Comandos reales | Módulo 8 |
| Hito 9 | Presentación | Feedback visual + integración | Módulo 9 + main.py |

# 6. TRABAJO EN PARALELO ENTRE INTEGRANTES

Una vez terminado el Módulo 2, varias tareas pueden desarrollarse en paralelo:

LANDMARKS
                   ↓
        ┌──────────┼──────────┐
        ↓          ↓          ↓
  GESTOS        SWIPES      VOLUMEN
 ESTÁTICOS      DINÁMICOS   CONTINUO
        │          │          │
        └──────────┼──────────┘
                   ↓
          MÁQUINA DE ESTADOS
                   ↓
           CONTROL MULTIMEDIA

Esto permite que diferentes integrantes trabajen sobre funciones separadas siempre que se acuerde previamente qué estructura de datos entrega hand_detector.py. Por ejemplo, todos pueden recibir la misma lista o diccionario de landmarks sin conocer la implementación interna del detector.

# 7. REGLA PARA AVANZAR DE MÓDULO

No avanzar al módulo siguiente solo porque el código “corre”. Cada etapa debe cumplir tres condiciones:

- Funciona de manera aislada con una prueba reproducible.

- Tiene una entrada y una salida claramente definidas.

- Puede integrarse al módulo siguiente sin copiar ni reescribir la lógica interna.

Ejemplo: antes de conectar Spotify o teclas multimedia, el sistema completo debería poder mostrar correctamente:

PALMA DETECTADA
ACTIVANDO... 100%
AIRDJ ACTIVO
SWIPE DERECHA
COMANDO: NEXT
COOLDOWN
AIRDJ BLOQUEADO

# 8. RESULTADO FINAL ESPERADO

Al finalizar todos los módulos, AirDJ deberá ser capaz de observar la mano mediante una webcam, permanecer bloqueado durante el uso normal, activarse únicamente ante una palma abierta y estable durante el tiempo requerido, aceptar un comando gestual dentro de una ventana temporal, ejecutar una acción multimedia, aplicar cooldown y volver a bloquearse. Todo el proceso deberá mostrarse visualmente para facilitar el uso y la explicación académica del proyecto.
