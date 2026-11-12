from typing import AsyncGenerator

from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.core.base import BaseModel
from app.core.config import DATABASE_URL, SQL_ECHO

# Clase base compartida por todos los modelos de tabla.
# Los modelos de cada módulo heredan de BaseModel para compartir la metadata.
Base = BaseModel


async def init_db(
    app: FastAPI,
    database_url: str | None = DATABASE_URL,
    echo: bool = SQL_ECHO,
) -> None:
    """Crea el motor y la fábrica de sesiones en app.state, y crea las tablas
    que falten con SQLModel.metadata.create_all.

    Se invoca en el lifespan de la aplicación (app/main.py). Falla con un
    mensaje claro si falta DATABASE_URL (D-05): el proyecto no trae una
    dirección de base por defecto.
    """
    if not database_url:
        raise RuntimeError(
            "Falta DATABASE_URL. Definí la variable de entorno o el archivo "
            ".env antes de arrancar la aplicación."
        )

    engine = create_async_engine(database_url, echo=echo)
    app.state.engine = engine
    app.state.session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db(app: FastAPI) -> None:
    """Cierra el motor al apagar la aplicación."""
    engine = getattr(app.state, "engine", None)
    if engine is not None:
        await engine.dispose()
        app.state.engine = None


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Dependencia de FastAPI: proporciona una sesión por petición.

    La fábrica de sesiones vive en app.state y se recupera desde el request.
    Se inyecta en los routers y services de cada módulo con Depends(get_session).
    """
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise RuntimeError("Base de datos no inicializada")
    async with session_factory() as session:
        yield session
