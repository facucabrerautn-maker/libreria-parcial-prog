from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException

from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroCreate, LibroUpdate, LibroRead


async def _cargar_libro(session: AsyncSession, libro_id: int) -> LibroRead:
    """Recarga un libro con editorial, género y autorías en una consulta fija."""
    result = await session.execute(
        select(Libro)
        .options(
            joinedload(Libro.editorial),
            joinedload(Libro.genero),
            selectinload(Libro.autorias).selectinload(LibroAutor.autor),
        )
        .where(Libro.id == libro_id)
    )
    libro = result.scalar_one()
    return LibroRead.model_validate(libro)


async def create_libro(session: AsyncSession, libro_in: LibroCreate) -> LibroRead:
    """Crea un libro con sus autorías anidadas.

    - No consulta previamente si los ids existen (la base rechaza FK inválida → 409)
    - El precio y stock se validan con CHECK en la base y con el DTO
    """
    libro_data = libro_in.model_dump(exclude={"autores"})
    libro = Libro(**libro_data)
    session.add(libro)

    try:
        await session.flush()  # Para obtener el id del libro antes de crear autorías

        for autoria_in in libro_in.autores:
            session.add(
                LibroAutor(
                    libro_id=libro.id,
                    autor_id=autoria_in.autor_id,
                    rol=autoria_in.rol,
                    orden=autoria_in.orden,
                )
            )

        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Clave foránea inválida o ISBN duplicado",
        ) from exc

    return await _cargar_libro(session, libro.id)


async def list_libros(
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    titulo: Optional[str] = None,
    genero_id: Optional[int] = None,
) -> List[LibroRead]:
    """Lista libros con paginación y filtros opcionales (título y género)."""
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
    if genero_id is not None:
        query = query.where(Libro.genero_id == genero_id)

    query = query.order_by(Libro.id).offset(offset).limit(limit)
    result = await session.execute(query)
    libros = result.scalars().all()
    return [LibroRead.model_validate(libro) for libro in libros]


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

    update_data = libro_in.model_dump(exclude_unset=True, exclude={"autores"})
    for field, value in update_data.items():
        setattr(libro, field, value)

    session.add(libro)
    try:
        # Si el PATCH envía autores, se reemplaza la lista completa de autorías.
        if "autores" in libro_in.model_fields_set and libro_in.autores is not None:
            await session.execute(
                delete(LibroAutor).where(LibroAutor.libro_id == libro_id)
            )
            for autoria_in in libro_in.autores:
                session.add(
                    LibroAutor(
                        libro_id=libro_id,
                        autor_id=autoria_in.autor_id,
                        rol=autoria_in.rol,
                        orden=autoria_in.orden,
                    )
                )

        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="ISBN duplicado o clave foránea inválida",
        ) from exc

    return await _cargar_libro(session, libro_id)
