# Historias de Usuario -- AirDJ

_Generado automaticamente el 2026-09-02T14:48:27.647Z -- no editar a mano, se sobreescribe en cada publicacion._

## HU-01: HU01 — Activación deliberada del sistema

Como usuario, quiero que AirDJ permanezca bloqueado hasta que realice de forma intencional un gesto de activación, para poder mover mis manos con normalidad frente a la cámara sin provocar cambios de canción, pausas o modificaciones de volumen accidentales.

### Criterios de Aceptacion

- AirDJ debe iniciar en estado bloqueado.
- Mientras esté bloqueado, ningún gesto de comando debe ejecutar acciones.
- El sistema solo debe habilitar comandos después de reconocer el gesto activador válido.
- Una vez activado, debe mostrar visualmente el cambio de estado.

## HU-02: HU02 — Confirmación temporal del gesto activador

Como usuario, quiero que el gesto de activación deba mantenerse estable durante un breve período antes de habilitar los comandos, para que una palma abierta detectada de manera momentánea durante una actividad cotidiana no sea interpretada como una intención de controlar el reproductor.

### Criterios de Aceptacion

- El gesto activador debe mantenerse durante un tiempo mínimo configurado.
- Una detección momentánea no debe activar el sistema.
- Si el gesto se interrumpe antes del tiempo mínimo, la validación debe reiniciarse.
- Al completar la confirmación, AirDJ debe pasar al estado activo.

## HU-03: HU03 — Ventana temporal de comandos

Como usuario, quiero que, una vez activado AirDJ, el sistema espere un comando únicamente durante unos segundos y luego vuelva a bloquearse automáticamente, para que el control gestual permanezca habilitado solo durante el tiempo necesario para dar una orden.

### Criterios de Aceptacion

- Luego de activarse, AirDJ debe habilitar una ventana temporal para recibir comandos.
- Durante ese período debe aceptar únicamente gestos válidos.
- Si no se detecta ningún comando dentro del tiempo establecido, debe volver automáticamente al estado bloqueado.
- La interfaz debe indicar cuándo el sistema está esperando un comando.

## HU-04: HU04 — Control de reproducción mediante gestos

Como usuario, quiero poder iniciar o pausar la reproducción mediante un gesto sencillo y claramente diferenciable, para controlar la música sin acercarme al dispositivo ni utilizar teclado, mouse o pantalla táctil.

### Criterios de Aceptacion

- El sistema debe reconocer el gesto definido para reproducción/pausa.
- El gesto solo debe ejecutarse si AirDJ está activo.
- Al reconocerlo, debe cambiar correctamente entre reproducción y pausa.
- La acción debe ejecutarse una sola vez por activación.

## HU-05: HU05 — Cambio de canción mediante movimiento de la mano

Como usuario, quiero poder avanzar a la siguiente canción realizando un movimiento lateral de la mano hacia la derecha, para cambiar de tema de manera rápida y natural mientras realizo otras actividades.


### Criterios de Aceptacion

- El sistema debe detectar un desplazamiento válido de la mano hacia la derecha.
- El movimiento debe superar un umbral mínimo para considerarse intencional.
- Si AirDJ está activo, debe avanzar una sola canción.
- Movimientos pequeños o incompletos no deben generar el comando.

## HU-06: HU06 — Regreso a la canción anterior

Como usuario, quiero poder volver a la canción anterior mediante un movimiento de la mano hacia la izquierda, para navegar entre las canciones sin interactuar físicamente con el reproductor.

### Criterios de Aceptacion

- El sistema debe detectar un desplazamiento válido de la mano hacia la izquierda.
- El movimiento debe superar el umbral mínimo definido.
- Si AirDJ está activo, debe ejecutar el comando de canción anterior una sola vez.
- Movimientos accidentales no deben producir acciones.

## HU-07: HU07 — Control gestual del volumen

Como usuario, quiero poder aumentar o disminuir progresivamente el volumen modificando la distancia entre pulgar e índice, para disponer de un control continuo e intuitivo del nivel de audio.

### Criterios de Aceptacion

- El sistema debe calcular la distancia relativa entre pulgar e índice.
- Aumentar dicha distancia debe incrementar progresivamente el volumen.
- Reducirla debe disminuir progresivamente el volumen.
- El volumen debe mantenerse dentro de los límites mínimo y máximo.
- Pequeñas variaciones involuntarias no deben provocar cambios bruscos.

## HU-08: HU08 — Funciones adicionales

Como usuario, quiero disponer de gestos adicionales que puedan asociarse a funciones secundarias, como marcar una canción como favorita o activar el modo repetición, para ampliar las posibilidades de interacción sin incorporar nuevos controles físicos.

### Criterios de Aceptacion

- El sistema debe permitir asociar nuevos gestos a funciones secundarias.
- Cada nuevo gesto debe tener un comando interno claramente identificado.
- La incorporación de nuevas funciones no debe modificar el funcionamiento de los gestos existentes.
- Las acciones adicionales deben respetar el mismo flujo de activación y validación.

## HU-09: HU09 — Reconocimiento confiable

Como usuario, quiero que el sistema diferencie correctamente los gestos intencionales de los movimientos naturales o accidentales de mi mano, para evitar acciones no solicitadas.

### Criterios de Aceptacion

- Los gestos deben cumplir un umbral mínimo de confianza.
- Gestos ambiguos o incompletos no deben ejecutar acciones.
- Los movimientos naturales de la mano deben ser ignorados cuando no coincidan con un gesto válido.
- Ante una detección dudosa, el sistema debe priorizar no ejecutar ninguna acción.

## HU-10: HU10 — Prevención de comandos repetidos

Como usuario, quiero que cada activación permita ejecutar una sola acción y que exista un breve bloqueo posterior, para evitar que mantener un gesto o regresar la mano a su posición inicial produzca comandos duplicados.

### Criterios de Aceptacion

- Cada activación debe permitir ejecutar como máximo una acción.
- Mantener un gesto durante varios frames no debe repetir el comando.
- Luego de ejecutar una acción, el sistema debe entrar en estado de cooldown.
- Durante el cooldown no deben aceptarse nuevos comandos.
- Finalizado el cooldown, AirDJ debe volver al estado bloqueado.

## HU-11: HU11 — Zona de interacción controlada

Como usuario, quiero que los comandos sean considerados únicamente cuando mi mano se encuentre dentro de una región específica de la imagen, para reducir todavía más las activaciones accidentales causadas por movimientos realizados fuera del área destinada al control.

### Criterios de Aceptacion

- Debe existir una región de interacción claramente definida dentro de la imagen.
- Solo los gestos realizados dentro de esa región deben ser considerados para ejecutar comandos.
- Los movimientos realizados fuera de la zona deben ser ignorados.
- La interfaz debe permitir identificar visualmente la zona de interacción.

## HU-12: HU12 — Confirmación visual del estado y la acción

Como usuario, quiero recibir una indicación visual del estado del sistema —bloqueado, activando, activo, ejecutando o en cooldown— y del comando reconocido, para comprender qué está interpretando AirDJ en cada momento.

### Criterios de Aceptacion

- La interfaz debe indicar el estado actual de AirDJ.
- Deben diferenciarse visualmente al menos los estados bloqueado, activando, activo, ejecutando y cooldown.
- Cuando se reconozca un comando, debe mostrarse cuál fue detectado.
- La indicación visual debe actualizarse inmediatamente ante un cambio de estado.

## HU-13: HU13 — Uso sin contacto físico

Como usuario, quiero poder controlar las principales funciones del reproductor a distancia y sin tocar ningún dispositivo, para utilizar el sistema mientras cocino, entreno, limpio o realizo otras actividades con las manos ocupadas.

### Criterios de Aceptacion

- Las funciones principales del reproductor deben poder ejecutarse exclusivamente mediante gestos.
- Durante el uso normal no debe ser necesario utilizar teclado, mouse ni pantalla táctil.
- El usuario debe poder controlar reproducción, cambio de canción y volumen a distancia.
- La interacción gestual debe poder realizarse dentro del campo visible de la cámara.
