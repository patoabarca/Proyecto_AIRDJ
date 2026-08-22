# Observaciones generales — AirDJ

Este archivo reúne reglas y criterios que deben respetarse en todas las funcionalidades del proyecto.

## Lógica general

AirDJ es una aplicación de control musical mediante gestos de la mano detectados por cámara.

El flujo principal debe ser:

```text
Cámara → detección de mano → reconocimiento de gesto → validación → comando → acción
```

## Reglas transversales

* Los comandos musicales no deben ejecutarse directamente ante cualquier gesto.
* Primero debe reconocerse un **gesto de activación**.
* Luego se habilita una ventana breve para recibir el gesto de comando.
* Si no se detecta un comando válido, el sistema vuelve al estado bloqueado.
* Un gesto debe mantenerse durante un tiempo mínimo o varios frames para considerarse válido.
* Después de ejecutar una acción debe existir un pequeño `cooldown` para evitar repeticiones.
* Ante un gesto dudoso o de baja confianza, no debe ejecutarse ninguna acción.
* La detección del gesto debe estar separada de la ejecución del comando musical.
* Los valores como confianza mínima, timeout y cooldown deben estar centralizados en configuración.
* La interfaz siempre debe informar el estado actual: bloqueado, escuchando, gesto detectado o acción ejecutada.

## Arquitectura

Cada módulo debe mantener una responsabilidad clara:

* **Cámara:** captura de video.
* **Visión:** detección de manos y landmarks.
* **Gestos:** reconocimiento y validación.
* **Estados:** activación, escucha y cooldown.
* **Reproductor:** ejecución de comandos musicales.
* **Interfaz:** presentación de información al usuario.

## Criterio general

AirDJ debe priorizar:

1. Evitar comandos accidentales.
2. Interpretar correctamente la intención del usuario.
3. Mantener el código modular y entendible.
4. Proporcionar feedback claro.
5. Permitir agregar nuevos gestos y comandos sin modificar toda la aplicación.

Cualquier nueva funcionalidad deberá respetar estas reglas generales.