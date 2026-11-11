# Librería — API de Catálogo y Ventas

API REST asíncrona para una librería de barrio que gestiona su catálogo de libros y sus ventas. Desarrollado como parcial de Programación III (Unidades 1 a 4).

## Stack

- Python 3.12
- FastAPI 0.111
- SQLModel 0.0.24
- SQLAlchemy 2.0 (async)
- asyncpg 0.30
- PostgreSQL 16
- python-dotenv 1.0
- uvicorn
- Docker (python:3.12-alpine)

## Levantar el proyecto desde cero

1. Clonar el repositorio.
2. Crear el entorno virtual: `python -m venv .venv`
3. Activarlo: `.venv\Scripts\activate` (Windows) o `source .venv/bin/activate` (Linux/Mac)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Copiar `.env.example` a `.env` y completar `DATABASE_URL`.
6. Arrancar el servidor: `uvicorn app.main:app --reload`

El servidor crea las tablas al arrancar (`create_all`).

## Estructura del proyecto

```
app/
  main.py                 # Aplicación, lifespan, registro de routers
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
