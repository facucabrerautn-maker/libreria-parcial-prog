from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.modules.editoriales.models import Editorial
from app.modules.editoriales.schemas import EditorialCreate, EditorialUpdate, EditorialRead


async def create_editorial(session: AsyncSession, editorial_in: EditorialCreate) -> EditorialRead:
    """Crea una editorial. Si el nombre ya existe, responde 409 con mensaje propio."""
    editorial = Editorial.model_validate(editorial_in)
    session.add(editorial)
    try:
        await session.commit()
        await session.refresh(editorial)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe una editorial con ese nombre",
        ) from exc
    return EditorialRead.model_validate(editorial)


async def list_editoriales(
    session: AsyncSession, limit: int = 20, offset: int = 0
) -> List[EditorialRead]:
    """Lista editoriales con paginación (limit entre 1 y 100, offset desde 0)."""
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    result = await session.execute(
        select(Editorial).offset(offset).limit(limit)
    )
    editoriales = result.scalars().all()
    return [EditorialRead.model_validate(e) for e in editoriales]


async def get_editorial(session: AsyncSession, editorial_id: int) -> EditorialRead:
    """Obtiene una editorial por su id. 404 si no existe."""
    editorial = await session.get(Editorial, editorial_id)
    if editorial is None:
        raise HTTPException(status_code=404, detail="Editorial no encontrada")
    return EditorialRead.model_validate(editorial)


async def update_editorial(
    session: AsyncSession, editorial_id: int, editorial_in: EditorialUpdate
) -> EditorialRead:
    """Actualiza una editorial parcialmente (solo campos enviados). 409 si nombre duplica."""
    editorial = await session.get(Editorial, editorial_id)
    if editorial is None:
        raise HTTPException(status_code=404, detail="Editorial no encontrada")

    update_data = editorial_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(editorial, field, value)

    session.add(editorial)
    try:
        await session.commit()
        await session.refresh(editorial)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe una editorial con ese nombre",
        ) from exc
    return EditorialRead.model_validate(editorial)
