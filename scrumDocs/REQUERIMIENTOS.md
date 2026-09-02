# Requerimientos -- AirDJ

_Generado automaticamente el 2026-09-02T14:47:46.281Z -- no editar a mano, se sobreescribe en cada publicacion._

## HU-01: HU01 — Activación deliberada del sistema

### RF-01: RF06 — Activación y control de estados (Funcional)

El sistema deberá permanecer bloqueado por defecto. Solo habilitará la recepción de comandos cuando la mano se encuentre en la zona de comandos y se detecte una palma abierta, estable y sostenida durante aproximadamente 1,5 segundos. Una vez activado, dispondrá de una ventana temporal de aproximadamente 5 segundos para recibir un único comando. Si no se reconoce ninguna orden válida o después de ejecutar una acción, el sistema volverá al estado bloqueado.
• BLOQUEADO
• ACTIVANDO
• ACTIVO
• EJECUTANDO
• COOLDOWN

### RF-02: RF07 — Validación y prevención de activaciones accidentales (Funcional)

El sistema deberá aplicar mecanismos temporales y espaciales para diferenciar gestos intencionales de movimientos cotidianos. También deberá evitar que un mismo gesto o el movimiento de retorno de la mano genere comandos repetidos.
• Permanencia mínima del gesto activador.
• Estabilidad de la mano.
• Zona de comandos.
• Umbrales mínimos de desplazamiento para gestos dinámicos.
• Cooldown posterior a una acción.

### RNF-01: RNF04 — Confiabilidad (No funcional)

El sistema deberá minimizar falsos positivos, comandos duplicados y activaciones no intencionales.

## HU-02: HU02 — Confirmación temporal del gesto activador

### RF-01: RF03 — Reconocimiento de gestos estáticos (Funcional)

El sistema deberá reconocer posturas predefinidas de la mano a partir de la configuración de sus landmarks.
• Palma abierta: gesto de activación.
• Puño cerrado: Play/Pausa.
• Índice levantado: función adicional configurable.

### RF-02: RF06 — Activación y control de estados (Funcional)

Proyecto AirDJ — Visión Artificial
El sistema deberá permanecer bloqueado por defecto. Solo habilitará la recepción de comandos cuando la mano se encuentre en la zona de comandos y se detecte una palma abierta, estable y sostenida durante aproximadamente 1,5 segundos. Una vez activado, dispondrá de una ventana temporal de aproximadamente 5 segundos para recibir un único comando. Si no se reconoce ninguna orden válida o después de ejecutar una acción, el sistema volverá al estado bloqueado.
• BLOQUEADO
• ACTIVANDO
• ACTIVO
• EJECUTANDO
• COOLDOWN

### RF-03: RF07 — Validación y prevención de activaciones accidentales (Funcional)

El sistema deberá aplicar mecanismos temporales y espaciales para diferenciar gestos intencionales de movimientos cotidianos. También deberá evitar que un mismo gesto o el movimiento de retorno de la mano genere comandos repetidos.
• Permanencia mínima del gesto activador.
• Estabilidad de la mano.
• Zona de comandos.
• Umbrales mínimos de desplazamiento para gestos dinámicos.
• Cooldown posterior a una acción.

### RNF-01: RNF04 — Confiabilidad (No funcional)

El sistema deberá minimizar falsos positivos, comandos duplicados y activaciones no intencionales.

## HU-03: HU03 — Ventana temporal de comandos

### RF-01: RF06 — Activación y control de estados (Funcional)

El sistema deberá permanecer bloqueado por defecto. Solo habilitará la recepción de comandos cuando la mano se encuentre en la zona de comandos y se detecte una palma abierta, estable y sostenida durante aproximadamente 1,5 segundos. Una vez activado, dispondrá de una ventana temporal de aproximadamente 5 segundos para recibir un único comando. Si no se reconoce ninguna orden válida o después de ejecutar una acción, el sistema volverá al estado bloqueado.
• BLOQUEADO
• ACTIVANDO
• ACTIVO
• EJECUTANDO
• COOLDOWN

### RNF-01: RNF03 — Tiempo de respuesta (No funcional)

La activación, el reconocimiento del gesto y la ejecución de la acción deberán producirse con una latencia suficientemente baja para que la interacción resulte natural.

## HU-04: HU04 — Control de reproducción mediante gestos

### RF-01: RF03 — Reconocimiento de gestos estáticos (Funcional)

El sistema deberá reconocer posturas predefinidas de la mano a partir de la configuración de sus landmarks.
• Palma abierta: gesto de activación.
• Puño cerrado: Play/Pausa.
• Índice levantado: función adicional configurable.

### RF-02: RF08 — Generación y ejecución de comandos multimedia (Funcional)

El sistema deberá asociar cada gesto válido con una acción multimedia y ejecutar el comando correspondiente sobre un reproductor real o una simulación del mismo.
• Puño → Play/Pausa.
• Swipe derecha → Siguiente.
• Swipe izquierda → Anterior.
• Pinza pulgar-índice → Volumen.
• Índice → función adicional configurable.

### RNF-01: RNF02 — Interacción sin contacto (No funcional)

Los comandos principales deberán poder ejecutarse sin teclado, mouse ni contacto físico con el dispositivo.

## HU-05: HU05 — Cambio de canción mediante movimiento de la mano

### RF-01: RF04 — Reconocimiento de gestos dinámicos (Funcional)

El sistema deberá analizar la posición de la mano a lo largo de varios frames para identificar movimientos laterales deliberados.
• Swipe hacia la derecha: siguiente canción.
• Swipe hacia la izquierda: canción anterior.

### RF-02: RF07 — Validación y prevención de activaciones accidentales (Funcional)

El sistema deberá aplicar mecanismos temporales y espaciales para diferenciar gestos intencionales de movimientos cotidianos. También deberá evitar que un mismo gesto o el movimiento de retorno de la mano genere comandos repetidos.
• Permanencia mínima del gesto activador.
• Estabilidad de la mano.
• Zona de comandos.
• Umbrales mínimos de desplazamiento para gestos dinámicos.
• Cooldown posterior a una acción.

### RF-03: RF08 — Generación y ejecución de comandos multimedia (Funcional)

El sistema deberá asociar cada gesto válido con una acción multimedia y ejecutar el comando correspondiente sobre un reproductor real o una simulación del mismo.
• Puño → Play/Pausa.
• Swipe derecha → Siguiente.
• Swipe izquierda → Anterior.
• Pinza pulgar-índice → Volumen.
• Índice → función adicional configurable.

### RNF-01: RNF02 — Interacción sin contacto (No funcional)

Los comandos principales deberán poder ejecutarse sin teclado, mouse ni contacto físico con el dispositivo.

## HU-06: HU06 — Regreso a la canción anterior

### RF-01: RF08 — Generación y ejecución de comandos multimedia (Funcional)

El sistema deberá asociar cada gesto válido con una acción multimedia y ejecutar el comando correspondiente sobre un reproductor real o una simulación del mismo.
• Puño → Play/Pausa.
• Swipe derecha → Siguiente.
• Swipe izquierda → Anterior.
• Pinza pulgar-índice → Volumen.
• Índice → función adicional configurable.

### RF-02: RF07 — Validación y prevención de activaciones accidentales (Funcional)

El sistema deberá aplicar mecanismos temporales y espaciales para diferenciar gestos intencionales de movimientos cotidianos. También deberá evitar que un mismo gesto o el movimiento de retorno de la mano genere comandos repetidos.
• Permanencia mínima del gesto activador.
• Estabilidad de la mano.
• Zona de comandos.
• Umbrales mínimos de desplazamiento para gestos dinámicos.
• Cooldown posterior a una acción.

### RF-03: RF04 — Reconocimiento de gestos dinámicos (Funcional)

El sistema deberá analizar la posición de la mano a lo largo de varios frames para identificar movimientos laterales deliberados.
• Swipe hacia la derecha: siguiente canción.
• Swipe hacia la izquierda: canción anterior.

### RNF-01: RNF02 — Interacción sin contacto (No funcional)

Los comandos principales deberán poder ejecutarse sin teclado, mouse ni contacto físico con el dispositivo.

## HU-07: HU07 — Control gestual del volumen

### RF-01: RF05 — Control gestual continuo del volumen (Funcional)

El sistema deberá calcular la distancia relativa entre pulgar e índice y convertirla en un valor proporcional de volumen dentro de un rango definido.

### RF-02: RF08 — Generación y ejecución de comandos multimedia (Funcional)

El sistema deberá asociar cada gesto válido con una acción multimedia y ejecutar el comando correspondiente sobre un reproductor real o una simulación del mismo.
• Puño → Play/Pausa.
• Swipe derecha → Siguiente.
• Swipe izquierda → Anterior.
• Pinza pulgar-índice → Volumen.
• Índice → función adicional configurable.

### RNF-03: RNF01 — Facilidad de uso (No funcional)

El usuario deberá poder utilizar el sistema sin conocimientos técnicos específicos.

### RNF-04: RNF02 — Interacción sin contacto (No funcional)

Los comandos principales deberán poder ejecutarse sin teclado, mouse ni contacto físico con el dispositivo.

## HU-08: HU08 — Funciones adicionales

### RF-01: RF03 — Reconocimiento de gestos estáticos (Funcional)

El sistema deberá reconocer posturas predefinidas de la mano a partir de la configuración de sus landmarks.
• Palma abierta: gesto de activación.
• Puño cerrado: Play/Pausa.
• Índice levantado: función adicional configurable.

### RF-02: RF08 — Generación y ejecución de comandos multimedia (Funcional)

El sistema deberá asociar cada gesto válido con una acción multimedia y ejecutar el comando correspondiente sobre un reproductor real o una simulación del mismo.
• Puño → Play/Pausa.
• Swipe derecha → Siguiente.
• Swipe izquierda → Anterior.
• Pinza pulgar-índice → Volumen.
• Índice → función adicional configurable.

### RNF-01: RNF08 — Escalabilidad (No funcional)

La arquitectura deberá permitir incorporar nuevos gestos, nuevas acciones y otros reproductores o dispositivos.

## HU-09: HU09 — Reconocimiento confiable

### RF-01: RF07 — Validación y prevención de activaciones accidentales (Funcional)

El sistema deberá aplicar mecanismos temporales y espaciales para diferenciar gestos intencionales de movimientos cotidianos. También deberá evitar que un mismo gesto o el movimiento de retorno de la mano genere comandos repetidos.
• Permanencia mínima del gesto activador.
• Estabilidad de la mano.
• Zona de comandos.
• Umbrales mínimos de desplazamiento para gestos dinámicos.
• Cooldown posterior a una acción.

### RNF-01: RNF04 — Confiabilidad  (No funcional)

El sistema deberá minimizar falsos positivos, comandos duplicados y activaciones no intencionales.

### RNF-02: RNF05 — Robustez (No funcional)

El reconocimiento deberá tolerar variaciones moderadas de iluminación, posición y distancia de la mano respecto de la cámara.

## HU-10: HU10 — Prevención de comandos repetidos

### RF-01: RF06 — Activación y control de estados (Funcional)

El sistema deberá permanecer bloqueado por defecto. Solo habilitará la recepción de comandos cuando la mano se encuentre en la zona de comandos y se detecte una palma abierta, estable y sostenida durante aproximadamente 1,5 segundos. Una vez activado, dispondrá de una ventana temporal de aproximadamente 5 segundos para recibir un único comando. Si no se reconoce ninguna orden válida o después de ejecutar una acción, el sistema volverá al estado bloqueado.
• BLOQUEADO
• ACTIVANDO
• ACTIVO
• EJECUTANDO
• COOLDOWN

### RF-02: RF07 — Validación y prevención de activaciones accidentales (Funcional)

El sistema deberá aplicar mecanismos temporales y espaciales para diferenciar gestos intencionales de movimientos cotidianos. También deberá evitar que un mismo gesto o el movimiento de retorno de la mano genere comandos repetidos.
• Permanencia mínima del gesto activador.
• Estabilidad de la mano.
• Zona de comandos.
• Umbrales mínimos de desplazamiento para gestos dinámicos.
• Cooldown posterior a una acción.

### RNF-01: RNF04 — Confiabilidad (No funcional)

El sistema deberá minimizar falsos positivos, comandos duplicados y activaciones no intencionales.

## HU-11: HU11 — Zona de interacción controlada

### RF-01: RF06 — Activación y control de estados (Funcional)

El sistema deberá permanecer bloqueado por defecto. Solo habilitará la recepción de comandos cuando la mano se encuentre en la zona de comandos y se detecte una palma abierta, estable y sostenida durante aproximadamente 1,5 segundos. Una vez activado, dispondrá de una ventana temporal de aproximadamente 5 segundos para recibir un único comando. Si no se reconoce ninguna orden válida o después de ejecutar una acción, el sistema volverá al estado bloqueado.
• BLOQUEADO
• ACTIVANDO
• ACTIVO
• EJECUTANDO
• COOLDOWN

### RF-02: RF07 — Validación y prevención de activaciones accidentales (Funcional)

El sistema deberá aplicar mecanismos temporales y espaciales para diferenciar gestos intencionales de movimientos cotidianos. También deberá evitar que un mismo gesto o el movimiento de retorno de la mano genere comandos repetidos.
• Permanencia mínima del gesto activador.
• Estabilidad de la mano.
• Zona de comandos.
• Umbrales mínimos de desplazamiento para gestos dinámicos.
• Cooldown posterior a una acción.

### RNF-01: RNF04 — Confiabilidad (No funcional)

El sistema deberá minimizar falsos positivos, comandos duplicados y activaciones no intencionales.

## HU-12: HU12 — Confirmación visual del estado y la acción

### RF-01: RF09 — Retroalimentación visual (Funcional)

El sistema deberá informar visualmente el estado actual, el progreso del gesto de activación, el gesto reconocido y la acción ejecutada, permitiendo al usuario comprender en todo momento qué está interpretando AirDJ.

### RNF-01: RNF01 — Facilidad de uso (No funcional)

El usuario deberá poder utilizar el sistema sin conocimientos técnicos específicos.

### RNF-02: RNF06 — Claridad de interacción (No funcional)

El sistema deberá informar visualmente su estado para que el usuario sepa cuándo está bloqueado, cuándo está activándose y cuándo acepta comandos.

## HU-13: HU13 — Uso sin contacto físico

### RF-01: RF08 — Generación y ejecución de comandos multimedia (Funcional)

El sistema deberá asociar cada gesto válido con una acción multimedia y ejecutar el comando correspondiente sobre un reproductor real o una simulación del mismo.
• Puño → Play/Pausa.
• Swipe derecha → Siguiente.
• Swipe izquierda → Anterior.
• Pinza pulgar-índice → Volumen.
• Índice → función adicional configurable.

### RNF-01: RNF01 — Facilidad de uso (No funcional)

El usuario deberá poder utilizar el sistema sin conocimientos técnicos específicos.

### RNF-02: RNF02 — Interacción sin contacto (No funcional)

Los comandos principales deberán poder ejecutarse sin teclado, mouse ni contacto físico con el dispositivo.

## RO-01: NOMBRE NUEVO DEL OPERACIONAL

### RF-01: RF01 — Adquisición y procesamiento de video (Funcional)

El sistema deberá recibir video desde una cámara, procesar sus frames y mantener un flujo continuo de imágenes para el análisis en tiempo real.

## RO-03: RNF07 — Modularidad

### RF-01: RNF07 — Modularidad (Funcional)

El sistema deberá desarrollarse mediante módulos independientes para facilitar pruebas, mantenimiento y futuras mejoras.

## RO-04: RNF09 — Privacidad

### RF-01: RNF09 — Privacidad (Funcional)

El sistema deberá priorizar el procesamiento local del video y no requerirá almacenamiento permanente de las imágenes capturadas.

## RO-05: Capacitacion del cliente

### RF-01: Capacitacion del cliente (Funcional)

_Sin detalle cargado._
