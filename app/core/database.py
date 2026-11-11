from typing import AsyncGenerator

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

_engine = None
_session_factory = None


async def init_db(database_url: str = DATABASE_URL, echo: bool = SQL_ECHO) -> None:
    """Crea el motor async y la fábrica de sesiones, y crea las tablas
    que falten con SQLModel.metadata.create_all.

    Se invoca en el lifespan de la aplicación (app/main.py).
    """
    global _engine, _session_factory

    _engine = create_async_engine(database_url, echo=echo)
    _session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )

    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Cierra el motor al apagar la aplicación."""
    global _engine
    if _engine is not None:
        await _engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia de FastAPI: proporciona una sesión por petición.

    Se inyecta en los routers y services de cada módulo con Depends(get_session).
    """
    if _session_factory is None:
        raise RuntimeError("Base de datos no inicializada")
    async with _session_factory() as session:
        yield session
