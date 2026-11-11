from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException

from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroCreate, LibroUpdate, LibroRead, AutorIARead


async def create_libro(session: AsyncSession, libro_in: LibroCreate) -> LibroRead:
    """Crea un libro con sus autorías anidadas.

    - No consulta previamente si los ids existen (la base rechaza FK inválida → 409)
    - El precio y stock se validan con CHECK en la base
    """
    libro_data = libro_in.model_dump(exclude={"autorias"})
    libro = Libro(**libro_data)
    session.add(libro)
    await session.flush()  # Para obtener el id del libro antes de crear autorías

    for autoria_in in libro_in.autorias:
        autoria = LibroAutor(
            libro_id=libro.id,
            autor_id=autoria_in.autor_id,
            rol=autoria_in.rol,
            orden=autoria_in.orden,
        )
        session.add(autoria)

    try:
        await session.commit()
        await session.refresh(libro)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Clave foránea inválida o ISBN duplicado",
        ) from exc

    # Recargar con relaciones cargadas
    result = await session.execute(
        select(Libro)
        .options(
            joinedload(Libro.editorial),
            joinedload(Libro.genero),
            selectinload(Libro.autorias).selectinload(LibroAutor.autor),
        )
        .where(Libro.id == libro.id)
    )
    libro_con_relaciones = result.scalar_one()
    return LibroRead.model_validate(libro_con_relaciones)


async def list_libros(
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    titulo: Optional[str] = None,
) -> List[LibroRead]:
    """Lista libros con paginación y filtro opcional por título (ILIKE, parámetro ligado)."""
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    query = select(Libro).options(
        joinedload(Libro.editorial),
        joinedload(Libro.genero),
        selectinload(Libro.autorias).selectinload(LibroAutor.autor),
    )

    if titulo:
        query = query.where(Libro.titulo.ilike(f"%{titulo}%"))

    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    libros = result.scalars().all()
    return [LibroRead.model_validate(l) for l in libros]


async def get_libro(session: AsyncSession, libro_id: int) -> LibroRead:
    """Obtiene un libro por su id con carga anticipada de relaciones (sin N+1)."""
    result = await session.execute(
        select(Libro)
        .options(
            joinedload(Libro.editorial),
            joinedload(Libro.genero),
            selectinload(Libro.autorias).selectinload(LibroAutor.autor),
        )
        .where(Libro.id == libro_id)
    )
    libro = result.scalar_one_or_none()
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return LibroRead.model_validate(libro)


async def update_libro(
    session: AsyncSession, libro_id: int, libro_in: LibroUpdate
) -> LibroRead:
    """Actualiza un libro parcialmente (solo campos enviados)."""
    libro = await session.get(Libro, libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    update_data = libro_in.model_dump(exclude_unset=True, exclude={"autorias"})
    for field, value in update_data.items():
        setattr(libro, field, value)

    try:
        await session.commit()
        await session.refresh(libro)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="ISBN duplicado o clave foránea inválida",
        ) from exc

    result = await session.execute(
        select(Libro)
        .options(
            joinedload(Libro.editorial),
            joinedload(Libro.genero),
            selectinload(Libro.autorias).selectinload(LibroAutor.autor),
        )
        .where(Libro.id == libro.id)
    )
    libro_con_relaciones = result.scalar_one()
    return LibroRead.model_validate(libro_con_relaciones)
