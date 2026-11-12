from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.modules.generos.models import Genero
from app.modules.generos.schemas import GeneroCreate, GeneroUpdate, GeneroRead
from app.modules.libros.models import Libro
from app.modules.libros.schemas import LibroResumenRead


async def create_genero(session: AsyncSession, genero_in: GeneroCreate) -> GeneroRead:
    """Crea un género. Si el nombre ya existe, responde 409 con mensaje propio."""
    genero = Genero.model_validate(genero_in)
    session.add(genero)
    try:
        await session.commit()
        await session.refresh(genero)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe un género con ese nombre",
        ) from exc
    return GeneroRead.model_validate(genero)


async def list_generos(
    session: AsyncSession, limit: int = 20, offset: int = 0
) -> List[GeneroRead]:
    """Lista géneros con paginación (limit entre 1 y 100, offset desde 0)."""
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    result = await session.execute(
        select(Genero).order_by(Genero.id).offset(offset).limit(limit)
    )
    generos = result.scalars().all()
    return [GeneroRead.model_validate(g) for g in generos]


async def get_genero(session: AsyncSession, genero_id: int) -> GeneroRead:
    """Obtiene un género por su id. 404 si no existe."""
    genero = await session.get(Genero, genero_id)
    if genero is None:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    return GeneroRead.model_validate(genero)


async def update_genero(
    session: AsyncSession, genero_id: int, genero_in: GeneroUpdate
) -> GeneroRead:
    """Actualiza un género parcialmente (solo campos enviados). 409 si nombre duplica."""
    genero = await session.get(Genero, genero_id)
    if genero is None:
        raise HTTPException(status_code=404, detail="Género no encontrado")

    update_data = genero_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(genero, field, value)

    session.add(genero)
    try:
        await session.commit()
        await session.refresh(genero)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe un género con ese nombre",
        ) from exc
    return GeneroRead.model_validate(genero)


async def list_libros_por_genero(
    session: AsyncSession, genero_id: int, limit: int = 20, offset: int = 0
) -> List[LibroResumenRead]:
    """Lista los libros de un género. 404 si el género no existe."""
    genero = await session.get(Genero, genero_id)
    if genero is None:
        raise HTTPException(status_code=404, detail="Género no encontrado")

    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    result = await session.execute(
        select(Libro)
        .where(Libro.genero_id == genero_id)
        .order_by(Libro.id)
        .offset(offset)
        .limit(limit)
    )
    libros = result.scalars().all()
    return [LibroResumenRead.model_validate(libro) for libro in libros]
