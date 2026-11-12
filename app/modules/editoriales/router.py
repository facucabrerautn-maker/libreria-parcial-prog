from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.editoriales.schemas import (
    EditorialCreate,
    EditorialRead,
    EditorialUpdate,
)
from app.modules.editoriales.service import (
    create_editorial,
    get_editorial,
    list_editoriales,
    list_libros_por_editorial,
    update_editorial,
)
from app.modules.libros.schemas import LibroResumenRead

router = APIRouter(prefix="/editoriales", tags=["editoriales"])


@router.post(
    "/",
    response_model=EditorialRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una editorial",
)
async def crear_editorial(
    editorial_in: EditorialCreate,
    session: AsyncSession = Depends(get_session),
) -> EditorialRead:
    """Crea una editorial nueva.

    - 201: creada exitosamente
    - 409: ya existe una editorial con ese nombre (UNIQUE en nombre)
    - 422: datos de entrada inválidos
    """
    return await create_editorial(session, editorial_in)


@router.get(
    "/",
    response_model=List[EditorialRead],
    summary="Listar editoriales",
)
async def listar_editoriales(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> List[EditorialRead]:
    """Lista editoriales con paginación.

    - `limit`: cantidad de resultados (1 a 100, default 20)
    - `offset`: posición inicial (default 0)
    """
    return await list_editoriales(session, limit=limit, offset=offset)


@router.get(
    "/{editorial_id}",
    response_model=EditorialRead,
    summary="Obtener una editorial por id",
)
async def obtener_editorial(
    editorial_id: int,
    session: AsyncSession = Depends(get_session),
) -> EditorialRead:
    """Obtiene una editorial por su id.

    - 200: encontrada
    - 404: no existe
    """
    return await get_editorial(session, editorial_id)


@router.patch(
    "/{editorial_id}",
    response_model=EditorialRead,
    summary="Actualizar una editorial parcialmente",
)
async def actualizar_editorial(
    editorial_id: int,
    editorial_in: EditorialUpdate,
    session: AsyncSession = Depends(get_session),
) -> EditorialRead:
    """Actualiza una editorial aplicando solo los campos enviados (PATCH parcial).

    - 200: actualizada
    - 404: no existe
    - 409: nombre duplicado
    - 422: datos inválidos
    """
    return await update_editorial(session, editorial_id, editorial_in)


@router.get(
    "/{editorial_id}/libros",
    response_model=List[LibroResumenRead],
    summary="Listar libros de una editorial",
)
async def listar_libros_editorial(
    editorial_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> List[LibroResumenRead]:
    """Lista los libros de una editorial.

    - 200: lista de libros (puede ser vacía)
    - 404: la editorial no existe
    """
    return await list_libros_por_editorial(
        session, editorial_id, limit=limit, offset=offset
    )
