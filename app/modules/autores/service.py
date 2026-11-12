from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException

from app.modules.autores.models import Autor
from app.modules.autores.schemas import AutorCreate, AutorUpdate, AutorRead
from app.modules.libros.models import LibroAutor
from app.modules.libros.schemas import LibroDeAutorRead


async def create_autor(session: AsyncSession, autor_in: AutorCreate) -> AutorRead:
    """Crea un autor."""
    autor = Autor.model_validate(autor_in)
    session.add(autor)
    await session.commit()
    await session.refresh(autor)
    return AutorRead.model_validate(autor)


async def list_autores(
    session: AsyncSession, limit: int = 20, offset: int = 0
) -> List[AutorRead]:
    """Lista autores con paginación (limit entre 1 y 100, offset desde 0)."""
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    result = await session.execute(
        select(Autor).order_by(Autor.id).offset(offset).limit(limit)
    )
    autores = result.scalars().all()
    return [AutorRead.model_validate(a) for a in autores]


async def get_autor(session: AsyncSession, autor_id: int) -> AutorRead:
    """Obtiene un autor por su id. 404 si no existe."""
    autor = await session.get(Autor, autor_id)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return AutorRead.model_validate(autor)


async def update_autor(
    session: AsyncSession, autor_id: int, autor_in: AutorUpdate
) -> AutorRead:
    """Actualiza un autor parcialmente (solo campos enviados)."""
    autor = await session.get(Autor, autor_id)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    update_data = autor_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(autor, field, value)

    session.add(autor)
    await session.commit()
    await session.refresh(autor)
    return AutorRead.model_validate(autor)


async def list_libros_por_autor(
    session: AsyncSession, autor_id: int, limit: int = 20, offset: int = 0
) -> List[LibroDeAutorRead]:
    """Lista los libros de un autor con el rol y el orden de cada autoría.

    404 si el autor no existe. La lectura del libro se precarga con joinedload
    para no depender de la carga perezosa.
    """
    autor = await session.get(Autor, autor_id)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    result = await session.execute(
        select(LibroAutor)
        .options(joinedload(LibroAutor.libro))
        .where(LibroAutor.autor_id == autor_id)
        .order_by(LibroAutor.orden, LibroAutor.libro_id)
        .offset(offset)
        .limit(limit)
    )
    autorias = result.scalars().all()

    return [
        LibroDeAutorRead(
            id=autoria.libro.id,
            isbn=autoria.libro.isbn,
            titulo=autoria.libro.titulo,
            precio=autoria.libro.precio,
            stock=autoria.libro.stock,
            rol=autoria.rol,
            orden=autoria.orden,
        )
        for autoria in autorias
        if autoria.libro is not None
    ]
