from typing import List

from fastapi import APIRouter, Depends, Query, status

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
    update_editorial,
)

router = APIRouter(prefix="/editoriales", tags=["editoriales"])


@router.post(
    "/",
    response_model=EditorialRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una editorial",
)
async def crear_editorial(
    editorial_in: EditorialCreate, session=Depends(get_session)
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
    session=Depends(get_session),
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
    editorial_id: int, session=Depends(get_session)
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
    session=Depends(get_session),
) -> EditorialRead:
    """Actualiza una editorial aplicando solo los campos enviados (PATCH parcial).

    - 200: actualizada
    - 404: no existe
    - 409: nombre duplicado
    - 422: datos inválidos
    """
    return await update_editorial(session, editorial_id, editorial_in)


# El endpoint GET /editoriales/{id}/libros se completa en C-07 (libros-con-autores)
# cuando el modelo Libro esté definido y la relación esté completa.
