from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from app.core.database import get_session
from app.modules.ventas.schemas import VentaCreate, VentaRead
from app.modules.ventas.service import create_venta, get_venta, list_ventas

router = APIRouter(prefix="/ventas", tags=["ventas"])


@router.post(
    "/",
    response_model=VentaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una venta con renglones",
)
async def crear_venta(
    venta_in: VentaCreate,
    background_tasks: BackgroundTasks,
    session=Depends(get_session),
) -> VentaRead:
    """Crea una venta con renglones anidados.

    - 201: creada exitosamente (con precios copiados y total calculado)
    - 409: cliente o libro inexistente (FK inválida)
    - 422: venta sin renglones, libro repetido, o datos inválidos
    """
    return await create_venta(session, venta_in, background_tasks)


@router.get(
    "/",
    response_model=List[VentaRead],
    summary="Listar ventas",
)
async def listar_ventas(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session=Depends(get_session),
) -> List[VentaRead]:
    """Lista ventas con paginación.

    - `limit`: cantidad de resultados (1 a 100, default 20)
    - `offset`: posición inicial (default 0)
    """
    return await list_ventas(session, limit=limit, offset=offset)


@router.get(
    "/{venta_id}",
    response_model=VentaRead,
    summary="Obtener una venta por id",
)
async def obtener_venta(
    venta_id: int, session=Depends(get_session)
) -> VentaRead:
    """Obtiene una venta por su id con carga anticipada de relaciones.

    - 200: encontrada (con cliente y renglones)
    - 404: no existe
    """
    return await get_venta(session, venta_id)


# No existe PATCH /ventas/{id} (RN-08: las ventas no se modifican, registran un hecho)
