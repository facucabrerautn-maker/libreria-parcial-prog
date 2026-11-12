# 02 — Descripción general

## Stack tecnológico

| Componente | Versión | Uso |
|------------|---------|-----|
| Python | 3.12 | Lenguaje |
| FastAPI | 0.111 | Framework web; handlers `async def` |
| SQLModel | 0.0.37 | Modelos de tabla y contratos |
| SQLAlchemy | 2.0 (async) | Motor, sesión y carga anticipada |
| asyncpg | 0.32 | Controlador asíncrono de PostgreSQL |
| PostgreSQL | 16 | Base de datos (ya existente en el VPS) |
| python-dotenv | 1.0 | Lectura del archivo `.env` |
| uvicorn | — | Servidor ASGI |
| Docker | 20.10 | Construir imagen y correr contenedor |

Imagen base: `python:3.12-alpine` (límite de 100 MB para la imagen base).

> SQLModel 0.0.24 no es compatible con Pydantic 2.14 (falla al importar con
> `Field 'id' requires a type annotation`). Se fija `sqlmodel==0.0.37`, que
> mantiene la API usada por el proyecto y funciona con Pydantic 2.x.

## Arquitectura general

Organización por módulo funcional, con la misma estructura en todos los módulos:

```
app/
  main.py                 # Aplicación, lifespan y registro de routers
  core/
    config.py             # Lectura de DATABASE_URL desde el entorno
    database.py           # Motor, fábrica de sesiones, dependencia get_session
  modules/
    <modulo>/
      models.py           # Modelos de tabla, restricciones y relaciones
      schemas.py          # DTO de entrada (Create, Update) y de salida (Read)
      service.py          # Lógica, traducción de errores, lecturas con precarga
      router.py           # Rutas HTTP: reciben, delegan y declaran la respuesta
test/                     # Archivos .http con casos de prueba
Dockerfile
.dockerignore
.env.example
DEPLOY.md
README.md
```

Módulos mínimos: `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`.
- `LibroAutor` vive en `libros`.
- `PerfilCliente` vive en `clientes`.
- `RenglonVenta` vive en `ventas`.

## Integraciones externas

- **PostgreSQL 16** en el VPS: dirección leída de `DATABASE_URL` (variable de entorno, no se versiona).
- **Docker**: imagen construida y corrida en el VPS con `docker run`, `--env-file` para las variables.
- No hay integraciones con pasarelas de pago, email, Redis ni colas de tareas en este parcial.
