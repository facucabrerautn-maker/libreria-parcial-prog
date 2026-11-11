from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.database import get_session
from app.modules.libros.schemas import LibroCreate, LibroRead, LibroUpdate
from app.modules.libros.service import (
    create_libro,
    get_libro,
    list_libros,
    update_libro,
)

router = APIRouter(prefix="/libros", tags=["libros"])


@router.post(
    "/",
    response_model=LibroRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un libro con autorías",
)
async def crear_libro(
    libro_in: LibroCreate, session=Depends(get_session)
) -> LibroRead:
    """Crea un libro con editorial, género opcional y lista de autorías.

    - 201: creado exitosamente
    - 409: ISBN duplicado o FK inválida (editorial, género, autor inexistente)
    - 422: datos de entrada inválidos
    """
    return await create_libro(session, libro_in)


@router.get(
    "/",
    response_model=List[LibroRead],
    summary="Listar libros",
)
async def listar_libros(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    titulo: Optional[str] = Query(default=None),
    session=Depends(get_session),
) -> List[LibroRead]:
    """Lista libros con paginación y filtro opcional por título.

    - `limit`: cantidad de resultados (1 a 100, default 20)
    - `offset`: posición inicial (default 0)
    - `titulo`: filtro por parte del título (sin distinguir mayúsculas, parámetro ligado)
    """
    return await list_libros(session, limit=limit, offset=offset, titulo=titulo)


@router.get(
    "/{libro_id}",
    response_model=LibroRead,
    summary="Obtener un libro por id",
)
async def obtener_libro(
    libro_id: int, session=Depends(get_session)
) -> LibroRead:
    """Obtiene un libro por su id con carga anticipada de relaciones.

    - 200: encontrado (con editorial, género y autorías)
    - 404: no existe
    """
    return await get_libro(session, libro_id)


@router.patch(
    "/{libro_id}",
    response_model=LibroRead,
    summary="Actualizar un libro parcialmente",
)
async def actualizar_libro(
    libro_id: int,
    libro_in: LibroUpdate,
    session=Depends(get_session),
) -> LibroRead:
    """Actualiza un libro aplicando solo los campos enviados (PATCH parcial).

    - 200: actualizado
    - 404: no existe
    - 409: ISBN duplicado o FK inválida
    - 422: datos inválidos
    """
    return await update_libro(session, libro_id, libro_in)
