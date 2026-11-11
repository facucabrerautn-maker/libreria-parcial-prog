from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException

from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.clientes.schemas import (
    ClienteCreate,
    ClienteRead,
    ClienteUpdate,
    PerfilCreate,
    PerfilRead,
)


async def create_cliente(session: AsyncSession, cliente_in: ClienteCreate) -> ClienteRead:
    """Crea un cliente. Si el email ya existe, responde 409 con mensaje propio."""
    cliente = Cliente.model_validate(cliente_in)
    session.add(cliente)
    try:
        await session.commit()
        await session.refresh(cliente)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe un cliente con ese email",
        ) from exc
    return ClienteRead.model_validate(cliente)


async def get_cliente(session: AsyncSession, cliente_id: int) -> ClienteRead:
    """Obtiene un cliente por su id con su perfil (carga anticipada)."""
    result = await session.execute(
        select(Cliente)
        .options(joinedload(Cliente.perfil))
        .where(Cliente.id == cliente_id)
    )
    cliente = result.scalar_one_or_none()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return ClienteRead.model_validate(cliente)


async def update_cliente(
    session: AsyncSession, cliente_id: int, cliente_in: ClienteUpdate
) -> ClienteRead:
    """Actualiza un cliente parcialmente (solo campos enviados)."""
    cliente = await session.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = cliente_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)

    session.add(cliente)
    try:
        await session.commit()
        await session.refresh(cliente)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe un cliente con ese email",
        ) from exc

    result = await session.execute(
        select(Cliente)
        .options(joinedload(Cliente.perfil))
        .where(Cliente.id == cliente.id)
    )
    cliente_con_perfil = result.scalar_one()
    return ClienteRead.model_validate(cliente_con_perfil)


async def create_perfil_cliente(
    session: AsyncSession, cliente_id: int, perfil_in: PerfilCreate
) -> PerfilRead:
    """Crea un perfil para un cliente. 404 si el cliente no existe, 409 si ya tiene perfil."""
    cliente = await session.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if cliente.perfil is not None:
        raise HTTPException(
            status_code=409,
            detail="El cliente ya tiene un perfil",
        )

    perfil = PerfilCliente.model_validate(perfil_in)
    perfil.cliente_id = cliente_id
    session.add(perfil)
    try:
        await session.commit()
        await session.refresh(perfil)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="El cliente ya tiene un perfil",
        ) from exc
    return PerfilRead.model_validate(perfil)


async def list_ventas_por_cliente(
    session: AsyncSession, cliente_id: int
) -> List:
    """Obtiene las ventas de un cliente. Se implementa completamente en C-09."""
    # Placeholder: se completa en C-09 con el modelo Venta
    return []
