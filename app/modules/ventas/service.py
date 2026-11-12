import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from fastapi import BackgroundTasks, HTTPException

from app.modules.libros.models import Libro
from app.modules.ventas.models import RenglonVenta, Venta
from app.modules.ventas.schemas import VentaCreate, VentaRead

logger = logging.getLogger("uvicorn.error")


async def _enviar_comprobante(
    cliente_id: int, venta_id: int, total: Decimal
) -> None:
    """Tarea en segundo plano: aviso de comprobante al cliente (simulado)."""
    await asyncio.sleep(0.5)
    logger.info(
        "[COMPROBANTE] Venta %s para cliente %s, total %s",
        venta_id,
        cliente_id,
        total,
    )


async def create_venta(
    session: AsyncSession,
    venta_in: VentaCreate,
    background_tasks: BackgroundTasks,
) -> VentaRead:
    """Crea una venta con renglones anidados.

    - Al menos un renglón requerido (422 si no)
    - Libro no repetido en los renglones (422)
    - Precio unitario copiado del libro en la base (no viaja en el DTO, RN-06)
    - Total calculado por el servidor (suma cantidad × precio_unitario, RN-07)
    - FK inválida → 409 con mensaje propio (RN-12)
    - Aviso de comprobante agendado con BackgroundTasks tras enviar respuesta (D-11)
    """
    if not venta_in.renglones:
        raise HTTPException(
            status_code=422,
            detail="Una venta debe tener al menos un renglón",
        )

    # Validar que no haya libros repetidos
    libro_ids = [renglon.libro_id for renglon in venta_in.renglones]
    if len(libro_ids) != len(set(libro_ids)):
        raise HTTPException(
            status_code=422,
            detail="Un mismo libro no puede aparecer en dos renglones",
        )

    # Leer precios de los libros de la base (una consulta con IN).
    # Es necesario para copiar el precio; si falta un libro, se responde 409.
    result_libros = await session.execute(
        select(Libro).where(Libro.id.in_(libro_ids))
    )
    libros = {libro.id: libro for libro in result_libros.scalars().all()}

    for libro_id in libro_ids:
        if libro_id not in libros:
            raise HTTPException(
                status_code=409,
                detail=f"Libro con id {libro_id} no existe",
            )

    # Calcular total y preparar renglones con precio copiado del libro
    renglones_data = []
    total = Decimal("0")
    for renglon_in in venta_in.renglones:
        libro = libros[renglon_in.libro_id]
        precio_unitario = libro.precio
        subtotal = Decimal(renglon_in.cantidad) * precio_unitario
        total += subtotal
        renglones_data.append(
            {
                "libro_id": renglon_in.libro_id,
                "cantidad": renglon_in.cantidad,
                "precio_unitario": precio_unitario,
            }
        )

    venta = Venta(
        cliente_id=venta_in.cliente_id,
        fecha=datetime.now(timezone.utc),
        total=total,
    )
    session.add(venta)

    try:
        await session.flush()  # Obtener el id de la venta
        for renglon_data in renglones_data:
            session.add(RenglonVenta(venta_id=venta.id, **renglon_data))
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Clave foránea inválida (cliente o libro no existe)",
        ) from exc

    # Agendar aviso de comprobante en segundo plano (después de enviar respuesta)
    background_tasks.add_task(
        _enviar_comprobante, venta_in.cliente_id, venta.id, total
    )

    return await _cargar_venta(session, venta.id)


async def _cargar_venta(session: AsyncSession, venta_id: int) -> VentaRead:
    """Recarga una venta con cliente y renglones en un número fijo de consultas."""
    result = await session.execute(
        select(Venta)
        .options(
            joinedload(Venta.cliente),
            selectinload(Venta.renglones).selectinload(RenglonVenta.libro),
        )
        .where(Venta.id == venta_id)
    )
    venta = result.scalar_one()
    return VentaRead.model_validate(venta)


async def list_ventas(
    session: AsyncSession, limit: int = 20, offset: int = 0
) -> List[VentaRead]:
    """Lista ventas con paginación (solo librero, todas las ventas)."""
    if limit < 1:
        limit = 1
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    result = await session.execute(
        select(Venta)
        .options(
            joinedload(Venta.cliente),
            selectinload(Venta.renglones).selectinload(RenglonVenta.libro),
        )
        .offset(offset)
        .limit(limit)
    )
    ventas = result.scalars().all()
    return [VentaRead.model_validate(venta) for venta in ventas]


async def get_venta(session: AsyncSession, venta_id: int) -> VentaRead:
    """Obtiene una venta por su id con carga anticipada de relaciones (sin N+1)."""
    result = await session.execute(
        select(Venta)
        .options(
            joinedload(Venta.cliente),
            selectinload(Venta.renglones).selectinload(RenglonVenta.libro),
        )
        .where(Venta.id == venta_id)
    )
    venta = result.scalar_one_or_none()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return VentaRead.model_validate(venta)
