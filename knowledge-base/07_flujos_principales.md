# 07 — Flujos principales

Flujos extremo a extremo del sistema, con número fijo de consultas (sin N+1).

## Flujo 1 — Alta de libro (con autores)

1. El librero envía `POST /libros/` con `isbn`, `titulo`, `precio`, `stock`, `editorial_id`, `genero_id` (opcional) y lista `autores` (cada una con `autor_id`, `rol`, `orden`).
2. El router valida el DTO de entrada (sin `id`).
3. El service crea el `Libro` y los objetos `LibroAutor` asociados.
4. Se escribe a la base; si alguna FK es inválida (editorial, género, autor inexistente), la base rechaza y se responde 409 con mensaje propio (sin consulta previa de existencia).
5. Respuesta 201 con `LibroRead` (incluye editorial, género y autores con rol y orden).

**Consultas:** 1 INSERT en `libro`, N INSERT en `libro_autor`. Sin N+1 en lecturas porque es una escritura.

## Flujo 2 — Alta de venta (con renglones)

1. El cliente envía `POST /ventas/` con `cliente_id` y lista `renglones` (cada una con `libro_id`, `cantidad`).
2. El router valida el DTO de entrada (al menos un renglón, libro no repetido).
3. El service lee el precio de cada libro de la base y lo copia al renglón (no viaja en el DTO).
4. Calcula el total como suma de `cantidad × precio_unitario`.
5. Crea la `Venta` con los `RenglonVenta` anidados (composición).
6. Respuesta 201 con `VentaRead` (cliente, renglones con precios y subtotales, total).
7. Se agenda con `BackgroundTasks` el aviso del comprobante al cliente (`await asyncio.sleep(0.5)` + log), que corre después de enviar la respuesta.

**Consultas:** SELECT de precios de libros (1 consulta con `IN` o join), 1 INSERT en `venta`, N INSERT en `renglon_venta`.

## Flujo 3 — Detalle de libro (sin N+1)

1. GET `/libros/{id}`.
2. Consulta con `joinedload` para `editorial` y `genero` (relaciones a uno), y `selectinload` para `autorias` (colección con datos de rol/orden).
3. Respuesta 200 con libro completo en una consulta fija (no crece con la cantidad de autores).

## Flujo 4 — Detalle de venta (sin N+1)

1. GET `/ventas/{id}`.
2. Consulta con `joinedload` para `cliente` y `selectinload` para `renglones` (con su libro).
3. Respuesta 200 con venta completa en una consulta fija (no crece con la cantidad de renglones).

## Flujo 5 — Listado de libros con búsqueda y paginación

1. GET `/libros/` con `limit`, `offset` y `titulo` opcional.
2. Consulta con filtro `ILIKE %titulo%` (parámetro ligado, nunca SQL concatenado), paginación con `limit`/`offset`.
3. Respuesta 200 con lista paginada de libros con editorial y género.

## Flujo 6 — Salud

1. GET `/health/live` → responde inmediatamente `{"estado": "vivo"}` sin tocar la base.
2. GET `/health/ready` → ejecuta `SELECT 1` contra la base; 200 si responde.
