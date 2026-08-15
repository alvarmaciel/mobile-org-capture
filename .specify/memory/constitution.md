<!--
Informe de impacto de sincronización
- Cambio de versión: 1.0.0 -> 1.0.1
- Principios modificados:
  - II. Publicar archivos atómicamente: el temporal DEBE crearse en el mismo
    directorio que la ruta final.
  - III. Destino Org solo por append: alcance acotado a operaciones del sistema;
    la edición manual desde el editor queda fuera.
  - VI. Ingesta sin red: alcance acotado al camino post-recepción; la recepción
    de capturas desde el exterior queda fuera.
- Secciones añadidas: ninguna
- Secciones eliminadas: ninguna
- TODO de seguimiento: ninguno
-->
# Constitución de Captura Móvil

## Principios fundamentales

### I. Preservar capturas confirmadas
Ninguna captura confirmada por la persona usuaria puede perderse. Ante la disyuntiva entre crear
un duplicado y perder una captura confirmada, el sistema DEBE crear el duplicado.

Justificación: Un duplicado puede identificarse y tratarse después; una captura perdida no puede
recuperarse.

Lo violaría: Descartar, sobrescribir o dar por procesada una captura confirmada antes de retenerla
de forma duradera.

### II. Publicar archivos atómicamente
Ningún proceso puede leer un archivo a medio escribir. Toda publicación de un archivo DEBE
escribir primero en un temporal, ejecutar `fsync` y renombrarlo atómicamente a su ruta final. 
El temporal DEBE crearse en el mismo directorio que la ruta final.

Justificación: La publicación atómica hace que cada archivo visible esté completo o no exista.

Lo violaría: Escribir directamente en la ruta final o exponer un archivo antes de sincronizar el
temporal y renombrarlo atómicamente.

### III. Destino Org solo por append
El sistema DEBE hacer crecer el archivo Org de destino solo mediante append. Ninguna operación del sistema 
puede ordenar, reescribir ni borrar contenido preexistente. La edición manual del archivo por parte de la 
persona usuaria desde su editor queda fuera de este alcance.


Justificación: Las escrituras solo por append preservan todo el registro previo de capturas ante
fallos.

Lo violaría: Reordenar, reemplazar, truncar o eliminar cualquier contenido existente del archivo
Org de destino.

### IV. Ingesta idempotente ante interrupciones
La ingesta DEBE tolerar interrupciones. Reejecutar una ingesta interrumpida puede duplicar
contenido, pero no DEBE perder una captura.

Justificación: El servicio corre en una Raspberry Pi, donde una interrupción de energía o del
proceso no puede convertir una captura confirmada en pérdida de datos.

Lo violaría: Marcar la ingesta como completa antes de su append duradero, u omitir una captura
reintentada de un modo que pueda excluirla del archivo de destino.

### V. Autorizar antes de procesar
Solo el identificador de la persona usuaria autorizada puede escribir. La verificación de
autorización DEBE ocurrir antes de cualquier procesamiento.

Justificación: La verificación temprana impide que entradas no autorizadas afecten archivos o el
estado de la ingesta.

Lo violaría: Analizar, preparar, crear archivos o realizar cualquier otro procesamiento antes de
verificar el identificador autorizado, o permitir escribir a otro identificador.

### VI. Ingesta sin red
El camino de ingesta —desde que una captura fue recibida hasta que quedó agregada al archivo Org 
de destino— DEBE carecer de dependencias de red. La recepción de capturas desde el exterior queda 
fuera de este alcance.

Justificación: La durabilidad local de las capturas no puede depender de la disponibilidad de red, 
especialmente con la conexión intermitente del sitio donde corre el servicio.

Lo violaría: Requerir una solicitud de red, un servicio remoto o un recurso montado por red para 
preparar, publicar o agregar una captura ya recibida. Por ejemplo, resolver el título de una URL 
antes de escribir el heading.

## Contexto operativo

Este es un servicio personal de captura para una sola persona que opera en una Raspberry Pi.

## Gobierno

Esta constitución prevalece sobre cualquier práctica del proyecto que entre en conflicto. Las
enmiendas DEBEN documentar el cambio propuesto, su efecto sobre los seis principios y el incremento
de versión semántica resultante. Eliminar un principio o redefinirlo de forma incompatible exige
un incremento MAYOR; añadir o ampliar materialmente el gobierno exige un incremento MENOR; las
aclaraciones exigen un incremento de PARCHE. Todo cambio en el comportamiento de ingesta DEBE
revisarse frente a los seis principios antes de aceptarse.

**Version**: 1.0.1 | **Ratified**: 2026-08-15 | **Last Amended**: 2026-08-15
