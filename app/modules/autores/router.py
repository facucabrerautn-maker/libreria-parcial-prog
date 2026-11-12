from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.autores.schemas import AutorCreate, AutorRead, AutorUpdate
from app.modules.autores.service import (
    create_autor,
    get_autor,
    list_autores,
    list_libros_por_autor,
    update_autor,
)
from app.modules.libros.schemas import LibroDeAutorRead

router = APIRouter(prefix="/autores", tags=["autores"])


@router.post(
    "/",
    response_model=AutorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un autor",
)
async def crear_autor(
    autor_in: AutorCreate,
    session: AsyncSession = Depends(get_session),
) -> AutorRead:
    """Crea un autor nuevo.

    - 201: creado exitosamente
    - 422: datos de entrada inválidos
    """
    return await create_autor(session, autor_in)


@router.get(
    "/",
    response_model=List[AutorRead],
    summary="Listar autores",
)
async def listar_autores(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> List[AutorRead]:
    """Lista autores con paginación.

    - `limit`: cantidad de resultados (1 a 100, default 20)
    - `offset`: posición inicial (default 0)
    """
    return await list_autores(session, limit=limit, offset=offset)


@router.get(
    "/{autor_id}",
    response_model=AutorRead,
    summary="Obtener un autor por id",
)
async def obtener_autor(
    autor_id: int,
    session: AsyncSession = Depends(get_session),
) -> AutorRead:
    """Obtiene un autor por su id.

    - 200: encontrado
    - 404: no existe
    """
    return await get_autor(session, autor_id)


@router.patch(
    "/{autor_id}",
    response_model=AutorRead,
    summary="Actualizar un autor parcialmente",
)
async def actualizar_autor(
    autor_id: int,
    autor_in: AutorUpdate,
    session: AsyncSession = Depends(get_session),
) -> AutorRead:
    """Actualiza un autor aplicando solo los campos enviados (PATCH parcial).

    - 200: actualizado
    - 404: no existe
    - 422: datos inválidos
    """
    return await update_autor(session, autor_id, autor_in)


@router.get(
    "/{autor_id}/libros",
    response_model=List[LibroDeAutorRead],
    summary="Listar libros de un autor con rol y orden",
)
async def listar_libros_autor(
    autor_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> List[LibroDeAutorRead]:
    """Lista los libros de un autor con el rol y el orden de cada autoría.

    - 200: lista de libros (puede ser vacía)
    - 404: el autor no existe
    """
    return await list_libros_por_autor(
        session, autor_id, limit=limit, offset=offset
    )
