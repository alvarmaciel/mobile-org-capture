# Feature Specification: Captura móvil al inbox Org

**Feature Branch**: `001-captura-movil`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "Desde mi teléfono envío una nota, texto, enlace o adjunto y la recibo
como una tarea TODO en el inbox de mi árbol Org, con confirmaciones separadas de recepción y de
incorporación."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capturar una nota desde el teléfono (Priority: P1)

La única persona autorizada envía texto o un enlace desde su teléfono y recibe una confirmación de
que la nota fue recibida y retenida. Sin abrir su editor ni ejecutar un comando en su computadora,
la nota termina como una tarea TODO en el archivo inbox de su árbol Org, por lo que queda
disponible en sus computadoras replicadas y en su vista de agenda.

**Why this priority**: Es el flujo que entrega la finalidad central del servicio: convertir una
captura móvil en una tarea visible en el árbol personal de la persona usuaria.

**Independent Test**: Se puede probar enviando una nota de texto de varias líneas desde el teléfono
y comprobando ambas confirmaciones y la tarea resultante en el archivo inbox.

**Acceptance Scenarios**:

1. **Given** que la persona autorizada envía un mensaje cuya primera línea es "Llamar al dentista"
   y cuya segunda línea es "Pedir turno para septiembre", **When** el servicio lo incorpora,
   **Then** el inbox contiene una nueva tarea TODO titulada "Llamar al dentista" con "Pedir turno
   para septiembre" en el cuerpo.
2. **Given** que la persona autorizada envía un enlace, **When** la nota se incorpora, **Then** el
   enlace aparece exactamente como fue enviado y el servicio no sustituye el enlace por un título
   obtenido externamente.
3. **Given** que una nota fue recibida y retenida, **When** su incorporación al inbox falla,
   **Then** la persona recibe la confirmación de recepción pero no la de incorporación y puede
   consultar la nota como pendiente.

---

### User Story 2 - Capturar un adjunto (Priority: P2)

La persona autorizada envía una nota con una foto, un PDF u otro archivo adjunto. El adjunto queda
guardado dentro de la carpeta de artefactos de su árbol Org y la tarea TODO del inbox contiene un
enlace al archivo guardado.

**Why this priority**: Las capturas visuales y documentales deben acompañar a la tarea sin requerir
una transferencia manual posterior desde el teléfono.

**Independent Test**: Se puede probar enviando una nota titulada con un PDF adjunto y verificando
que el archivo está en la carpeta de artefactos y que la tarea creada enlaza a ese archivo.

**Acceptance Scenarios**:

1. **Given** que la persona autorizada envía una nota con una foto adjunta, **When** recibe la
   confirmación de incorporación, **Then** existe una tarea TODO con un enlace a la copia guardada
   de la foto dentro del árbol Org.
2. **Given** que el adjunto no puede incorporarse al árbol Org, **When** se procesa la nota,
   **Then** la persona no recibe confirmación de incorporación y la captura continúa consultable
   como pendiente.

---

### User Story 3 - Consultar capturas pendientes (Priority: P3)

La persona puede consultar en cualquier momento cuántas notas fueron recibidas y retenidas, pero
aún no fueron incorporadas al inbox.

**Why this priority**: Distinguir recepción de incorporación permite detectar y actuar ante fallos
sin confundir una captura pendiente con una pérdida de datos.

**Independent Test**: Se puede retener una nota e impedir temporalmente su incorporación; la
consulta debe mostrar un pendiente. Tras incorporarla, la misma consulta debe mostrar cero
pendientes para esa nota.

**Acceptance Scenarios**:

1. **Given** que hay tres capturas recibidas y retenidas sin incorporar, **When** la persona
   consulta los pendientes, **Then** obtiene el total de tres.
2. **Given** que una captura pendiente queda incorporada al inbox, **When** la persona vuelve a
   consultar los pendientes, **Then** el total disminuye en una unidad.

### Edge Cases

- Una interrupción durante la incorporación no puede hacer que una captura confirmada como recibida
  desaparezca; al reintentar, puede aparecer duplicada pero no faltar.
- Si el mensaje tiene una sola línea, esa línea es el título y la tarea se crea sin cuerpo adicional.
- Si la primera línea está vacía, se conserva el resto del mensaje y se usa "Sin título" como
  título de la tarea.
- Si una persona no autorizada intenta enviar una nota, no se retiene, procesa ni incorpora nada.
- Si ya existe contenido en el inbox, la incorporación de una nota no altera ni elimina dicho
  contenido.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir que únicamente la persona autorizada envíe capturas al
  servicio y DEBE verificar su identidad antes de retener o procesar su contenido.
- **FR-002**: El sistema DEBE aceptar notas de texto, enlaces y archivos adjuntos enviados desde el
  teléfono de la persona autorizada.
- **FR-003**: El sistema DEBE emitir una confirmación distinguible cuando una captura fue recibida
  y retenida de forma duradera.
- **FR-004**: El sistema DEBE emitir una segunda confirmación distinguible solo cuando la captura
  quedó incorporada al archivo inbox.
- **FR-005**: El sistema DEBE crear para cada captura incorporada una nueva tarea marcada TODO en
  el archivo inbox del árbol Org.
- **FR-006**: El sistema DEBE usar la primera línea del mensaje como título de la tarea y debe
  conservar las líneas posteriores como cuerpo, en su orden original.
- **FR-007**: El sistema DEBE conservar los enlaces exactamente como fueron enviados y no debe
  resolver ni sustituir su título.
- **FR-008**: El sistema DEBE guardar cada adjunto incorporado en la carpeta de artefactos del árbol
  Org y debe incluir en la tarea un enlace al archivo guardado.
- **FR-009**: El sistema DEBE conservar toda captura que ya recibió y retuvo aunque falle su
  incorporación; un reintento puede crear un duplicado, pero no puede perder la captura.
- **FR-010**: El sistema DEBE agregar las tareas al inbox sin ordenar, reescribir ni eliminar el
  contenido preexistente.
- **FR-011**: El sistema DEBE permitir consultar el número actual de capturas recibidas y retenidas
  que aún no fueron incorporadas al inbox.
- **FR-012**: Una vez recibida y retenida una captura, el sistema DEBE poder incorporarla al inbox
  sin depender de conectividad de red.
- **FR-013**: El sistema DEBE permitir completar el envío y la incorporación desde el teléfono sin
  que la persona tenga que abrir su editor ni ejecutar un comando en una computadora.
- **FR-014**: El sistema DEBE asignar a cada artefacto guardado un nombre único
  dentro de la carpeta de artefactos, y guardar un artefacto nunca DEBE
  reemplazar ni sobrescribir un artefacto existente.
- **FR-015**: El sistema DEBE rechazar los adjuntos que superen un tamaño máximo
  configurable e informar el rechazo a la persona que los envió, sin retenerlos
  ni incorporarlos.
- **FR-016**: La consulta de pendientes muestra un total actual y cuales son los títulos de los pendientes.
- **FR-016**: El sistema DEBE registrar en la tarea el momento en que la captura
  fue recibida, no el momento en que fue incorporada al inbox.

### Key Entities *(include if feature involves data)*

- **Captura**: Nota enviada por la persona autorizada; incluye texto, enlaces, adjuntos y su estado
  de recepción e incorporación.
- **Tarea de inbox**: Entrada TODO creada en el archivo inbox a partir de una captura; contiene el
  título, el cuerpo y los enlaces correspondientes.
- **Artefacto**: Copia de un archivo adjunto guardada dentro del árbol Org y enlazada desde una
  tarea de inbox.
- **Pendiente de incorporación**: Captura recibida y retenida para la que aún no existe una
  incorporación confirmada al inbox.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En una prueba de 100 capturas autorizadas, el 100% recibe una confirmación de
  recepción antes de que se informe cualquier resultado de incorporación.
- **SC-002**: En una prueba de 100 notas de varias líneas incorporadas, el 100% crea una tarea TODO
  cuyo título coincide con la primera línea y cuyo cuerpo conserva las líneas restantes en orden.
- **SC-003**: En una prueba de 50 capturas con adjuntos, el 100% de las tareas incorporadas contiene
  un enlace utilizable al archivo correspondiente dentro del árbol Org.
- **SC-004**: Ante una falla simulada de incorporación posterior a la recepción, el 100% de las
  capturas recibidas permanece contabilizado como pendiente hasta su incorporación confirmada.
- **SC-005**: La persona puede determinar cuántas capturas siguen pendientes en una única consulta,
  sin abrir el editor ni ejecutar un comando en una computadora.

## Assumptions

- Solo una persona usa el servicio y dispone de un identificador autorizado previamente configurado.
- El árbol Org, su archivo inbox y la carpeta de artefactos ya existen y se replican fuera del
  alcance de esta funcionalidad.
- La recepción inicial desde el teléfono puede requerir conectividad; después de retener la captura,
  su incorporación al árbol Org no depende de red.
- Una primera línea vacía se representa con el título "Sin título" para conservar el resto de la
  captura sin descartarla.
