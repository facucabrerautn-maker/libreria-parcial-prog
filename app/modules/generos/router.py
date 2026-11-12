from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.generos.schemas import GeneroCreate, GeneroRead, GeneroUpdate
from app.modules.generos.service import (
    create_genero,
    get_genero,
    list_generos,
    list_libros_por_genero,
    update_genero,
)
from app.modules.libros.schemas import LibroResumenRead

router = APIRouter(prefix="/generos", tags=["generos"])


@router.post(
    "/",
    response_model=GeneroRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un género",
)
async def crear_genero(
    genero_in: GeneroCreate,
    session: AsyncSession = Depends(get_session),
) -> GeneroRead:
    """Crea un género nuevo.

    - 201: creado exitosamente
    - 409: ya existe un género con ese nombre (UNIQUE en nombre)
    - 422: datos de entrada inválidos
    """
    return await create_genero(session, genero_in)


@router.get(
    "/",
    response_model=List[GeneroRead],
    summary="Listar géneros",
)
async def listar_generos(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> List[GeneroRead]:
    """Lista géneros con paginación.

    - `limit`: cantidad de resultados (1 a 100, default 20)
    - `offset`: posición inicial (default 0)
    """
    return await list_generos(session, limit=limit, offset=offset)


@router.get(
    "/{genero_id}",
    response_model=GeneroRead,
    summary="Obtener un género por id",
)
async def obtener_genero(
    genero_id: int,
    session: AsyncSession = Depends(get_session),
) -> GeneroRead:
    """Obtiene un género por su id.

    - 200: encontrado
    - 404: no existe
    """
    return await get_genero(session, genero_id)


@router.patch(
    "/{genero_id}",
    response_model=GeneroRead,
    summary="Actualizar un género parcialmente",
)
async def actualizar_genero(
    genero_id: int,
    genero_in: GeneroUpdate,
    session: AsyncSession = Depends(get_session),
) -> GeneroRead:
    """Actualiza un género aplicando solo los campos enviados (PATCH parcial).

    - 200: actualizado
    - 404: no existe
    - 409: nombre duplicado
    - 422: datos inválidos
    """
    return await update_genero(session, genero_id, genero_in)


@router.get(
    "/{genero_id}/libros",
    response_model=List[LibroResumenRead],
    summary="Listar libros de un género",
)
async def listar_libros_genero(
    genero_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> List[LibroResumenRead]:
    """Lista los libros de un género.

    - 200: lista de libros (puede ser vacía)
    - 404: el género no existe
    """
    return await list_libros_por_genero(
        session, genero_id, limit=limit, offset=offset
    )
