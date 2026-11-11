# 08 — Arquitectura propuesta

## Patrones

- **Capas separadas:** routers (HTTP), services (lógica), models (tabla), schemas (DTO).
- **DTO separados de modelos de tabla:** los DTO de alta no llevan `id`; los PATCH aplican solo campos enviados (`exclude_unset`).
- **Lógica en el service:** cada módulo tiene su `service.py` que recibe la sesión como parámetro.
- **Traducción de errores:** `IntegrityError` de la base se traduce a mensajes propios; nunca se expone texto interno de la base ni trazas al cliente.
- **Carga anticipada:** `joinedload` para relaciones a uno, `selectinload` para colecciones; nunca carga perezosa.
- **Asincronía sin bloqueos:** todos los handlers son `async def`; no hay `time.sleep`, `requests` ni acceso síncrono a la base dentro de ellos.
- **BackgroundTasks:** el aviso de comprobante de venta se agenda tras enviar la respuesta.
- **Ciclo de vida con lifespan:** el motor y la fábrica de sesiones se crean en el lifespan, se guardan en `app.state`, y el motor se cierra al apagar.
- **create_all al arrancar:** `SQLModel.metadata.create_all` crea las tablas que faltan (no migraciones en este parcial).

## Estructura de directorios

```
app/
  main.py
  core/
    config.py      # DATABASE_URL desde el entorno
    database.py    # motor, sesiones, get_session
  modules/
    health/
    editoriales/
    generos/
    autores/
    libros/        # incluye LibroAutor
    clientes/      # incluye PerfilCliente
    ventas/        # incluye RenglonVenta
test/              # archivos .http
Dockerfile
.dockerignore
.env.example
DEPLOY.md
README.md
```

## Seguridad

- La aplicación no corre como root en el contenedor (usuario sin privilegios con `USER`).
- Ninguna contraseña en el código, el repositorio ni la imagen.
- El `.env` no se versiona; hay `env.example` con la forma de `DATABASE_URL` sin valores reales.
- El `.dockerignore` excluye `.env`, `.venv`, `.git` y `__pycache__`.
- `DATABASE_URL` entra como variable de entorno al correr el contenedor (`--env-file`), nunca se hornea en la imagen.
- Los errores devueltos al cliente son mensajes propios, nunca texto de la base ni trazas.

## Variables de entorno

| Variable | Descripción | Origen |
|----------|-------------|--------|
| `DATABASE_URL` | Dirección de PostgreSQL con driver `postgresql+asyncpg` (servidor, usuario, contraseña, nombre de base) | `.env` / `--env-file` en `docker run` |
| `SQL_ECHO` | Activa diagnóstico de consultas (echo=True) | `.env` (opcional, false por defecto) |

## Despliegue

- Imagen base: `python:3.12-alpine` (74,7 MB, límite de 100 MB para la base).
- Dependencias instaladas con `pip install --no-cache-dir` antes de copiar el código (capa de caché).
- Se corre con `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file <archivo> libreria`.
- `DATABASE_URL` con `localhost` falla dentro del contenedor; usar `host.docker.internal` (con `--add-host=host.docker.internal:host-gateway` en Linux) o la dirección que entregue la cátedra.
- HEALTHCHECK sobre `GET /health/ready` (usando `wget` en Alpine, sin `curl`; dirección `127.0.0.1` no `localhost`).
