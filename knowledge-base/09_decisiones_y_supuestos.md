# 09 — Decisiones y supuestos

## Decisiones de diseño

| # | Decisión | Justificación |
|---|----------|---------------|
| D-01 | Stack exactamente como lo fija la consigna: Python 3.12, FastAPI 0.111, SQLModel 0.0.24, SQLAlchemy 2.0 async, asyncpg, PostgreSQL 16. | La consigna especifica versiones mínimas y los casos de prueba las asumen. |
| D-02 | Imagen base `python:3.12-alpine` en lugar de `python:3.12-slim`. | Alpine ocupa 74,7 MB (bajo el límite de 100 MB); slim ocupa 180 MB y no cumple. Las dependencias (asyncpg, pydantic-core) se instalan sin compilador. |
| D-03 | No usar Docker Compose. | La consigna dice explícitamente que el despliegue es de una sola imagen y la base ya está en el servidor. |
| D-04 | No usar migraciones; `create_all` al arrancar. | La consigna indica que las migraciones no se evalúan y el esquema se crea con `create_all`. |
| D-05 | `libro_autor` modelado como entidad de asociación con clase propia. | Tiene datos propios (rol, orden) que no son del libro ni del autor; un `link_model` los ocultaría. |
| D-06 | Precio del renglón copiado del libro en el service, no viaja en el DTO. | RN-06: el precio se lee de la base al registrar la venta. |
| D-07 | Total de venta calculado por el servidor, no viaja en el DTO. | RN-07. |
| D-08 | `cliente.perfil` devuelve un objeto, no una lista. | Relación uno a uno (RN-09). |
| D-09 | No hay PATCH de ventas. | RN-08: las ventas no se modifican, registran un hecho. |
| D-10 | Filtro por título con parámetro ligado, `ILIKE`, sin SQL concatenado. | RN-11 y requisito no funcional de SQL nunca armado por concatenación. |
| D-11 | `BackgroundTasks` para el aviso de comprobante (`asyncio.sleep(0.5)`). | Ejercicio 6: asincronía sin bloqueos, aviso después de enviar la respuesta. |
| D-12 | `exclude_unset` en PATCH para aplicar solo campos enviados. | Ejercicio 3: PATCH parcial. |

## Supuestos inferidos

| # | Supósito | Incertidumbre |
|---|----------|---------------|
| S-01 | No se requiere autenticación ni autorización en el parcial. | Confirmado por la consigna (QUÉ QUEDA AFUERA). |
| S-02 | El esquema se crea con `create_all` al arrancar; no hay versionado de migraciones. | Confirmado por la consigna. |
| S-03 | Los datos semilla se cargan dentro del contenedor tras el despliegue (`docker exec`). | Mencionado en el ejercicio 8, pero no hay script específico definido. |
| S-04 | PostgreSQL ya existe en el VPS; la aplicación solo se conecta a ella. | Confirmado por la consigna ("la base es la que ya tiene el servidor"). |
| S-05 | La URL de la base se pasa via `--env-file` en `docker run`, no se hornea en la imagen. | Confirmado por la consigna (ningún secreto en la imagen). |
| S-06 | Los casos de prueba son archivos `.http` en `test/`. | Confirmado por la consigna (estructura obligatoria del proyecto). |
| S-07 | El grupo parte de su propio TP entregado como base del parcial. | Mencionado en los objetivos, pero no se sabe qué contenido tiene ese TP. |
