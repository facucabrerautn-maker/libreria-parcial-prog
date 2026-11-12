from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.database import get_session
from app.modules.clientes.models import Cliente
from app.modules.clientes.schemas import (
    ClienteCreate,
    ClienteRead,
    ClienteUpdate,
    PerfilCreate,
    PerfilRead,
)
from app.modules.clientes.service import (
    create_cliente,
    create_perfil_cliente,
    get_cliente,
    list_ventas_por_cliente,
    update_cliente,
)
from app.modules.ventas.schemas import VentaRead

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post(
    "/",
    response_model=ClienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un cliente",
)
async def crear_cliente(
    cliente_in: ClienteCreate, session=Depends(get_session)
) -> ClienteRead:
    """Crea un cliente nuevo.

    - 201: creado exitosamente
    - 409: ya existe un cliente con ese email (UNIQUE en email)
    - 422: datos de entrada inválidos
    """
    return await create_cliente(session, cliente_in)


@router.get(
    "/{cliente_id}",
    response_model=ClienteRead,
    summary="Obtener un cliente por id con su perfil",
)
async def obtener_cliente(
    cliente_id: int, session=Depends(get_session)
) -> ClienteRead:
    """Obtiene un cliente por su id con su perfil (carga anticipada).

    - 200: encontrado (con perfil si existe)
    - 404: no existe
    """
    return await get_cliente(session, cliente_id)


@router.patch(
    "/{cliente_id}",
    response_model=ClienteRead,
    summary="Actualizar un cliente parcialmente",
)
async def actualizar_cliente(
    cliente_id: int,
    cliente_in: ClienteUpdate,
    session=Depends(get_session),
) -> ClienteRead:
    """Actualiza un cliente aplicando solo los campos enviados (PATCH parcial).

    - 200: actualizado
    - 404: no existe
    - 409: email duplicado
    - 422: datos inválidos
    """
    return await update_cliente(session, cliente_id, cliente_in)


@router.post(
    "/{cliente_id}/perfil",
    response_model=PerfilRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear perfil de cliente",
)
async def crear_perfil(
    cliente_id: int,
    perfil_in: PerfilCreate,
    session=Depends(get_session),
) -> PerfilRead:
    """Crea un perfil para un cliente (relación uno a uno).

    - 201: creado exitosamente
    - 404: cliente no encontrado
    - 409: el cliente ya tiene un perfil
    """
    return await create_perfil_cliente(session, cliente_id, perfil_in)


@router.get(
    "/{cliente_id}/ventas",
    response_model=List[VentaRead],
    summary="Obtener ventas de un cliente",
)
async def obtener_ventas_cliente(
    cliente_id: int, session=Depends(get_session)
) -> List[VentaRead]:
    """Obtiene las ventas de un cliente.

    - 200: lista de ventas
    - 404: cliente no encontrado
    """
    cliente = await session.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return await list_ventas_por_cliente(session, cliente_id)
