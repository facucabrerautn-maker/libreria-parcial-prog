# 01 — Visión y objetivos

## Propósito

API REST asíncrona para una librería de barrio que gestione su catálogo de libros y sus ventas. El sistema permite a la librería registrar editoriales, géneros, autores y libros; registrar clientes con perfil opcional; y registrar ventas con sus renglones (qué libro, cuántos ejemplares, a qué precio). Desarrollado como parcial de Programación III (Unidades 1 a 4: fundamentos de FastAPI, contratos y CRUD, ejecución asíncrona sin bloqueos, persistencia relacional con SQLModel y PostgreSQL, despliegue en Docker sobre VPS).

## Objetivos por actor

### Cliente (comprador)
- Consultar el catálogo de libros con paginación y búsqueda por título.
- Ver el detalle de un libro (editorial, género, autores con rol y orden).
- Registrarse como cliente y cargar un perfil con teléfono y dirección.
- Ver sus propias ventas realizadas.

### Librero (administrador de la librería)
- ABMC de editoriales, géneros, autores y libros.
- Registrar ventas con renglones anidados (precio copiado del libro, total calculado por el servidor).
- Consultar ventas y su detalle.

## Alcance

- API REST con handlers `async def`, sin llamadas bloqueantes.
- Modelos de tabla separados de contratos de entrada/salida (DTO).
- Códigos HTTP correctos (201 al crear, 404, 409, 422).
- Carga anticipada de relaciones (joinedload / selectinload) para evitar N+1.
- Restricciones de base de datos (UNIQUE, CHECK, FK, índices).
- Imagen Docker basada en `python:3.12-alpine`, usuario no root, sin secretos en la imagen.
- Despliegue con `docker run` contra PostgreSQL ya existente en el VPS.
- `create_all` al arrancar (no migraciones en este parcial).

## Fuera de alcance

- Autenticación y autorización (capítulo 5).
- Repositorios ni Unit of Work (capítulo 6).
- Colas de tareas con Redis (capítulos 7 y 8).
- Docker Compose (despliegue de una sola imagen).
- Migraciones de esquema (el esquema se crea con `create_all` al arrancar).
- Pago real (el comprobante se simula con `BackgroundTasks` + `asyncio.sleep`).
