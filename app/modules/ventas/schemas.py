from datetime import datetime
from typing import List, Optional

from pydantic import Field as PydanticField

from app.modules.ventas.models import Venta, RenglonVenta


class RenglonVentaCreate(RenglonVenta):
    """DTO de entrada para un renglón de venta. No lleva id ni precio_unitario (se copia del libro)."""
    id: Optional[int] = PydanticField(default=None)
    precio_unitario: Optional[float] = PydanticField(default=None)

    model_config = {"from_attributes": True}


class VentaCreate(Venta):
    """DTO de entrada para crear una venta. Incluye lista de renglones anidados."""
    cliente_id: int
    renglones: List[RenglonVentaCreate] = []
    fecha: Optional[datetime] = PydanticField(default=None)
    total: Optional[float] = PydanticField(default=None)

    model_config = {"from_attributes": True}


class VentaUpdate(Venta):
    """DTO de entrada para actualizar una venta. No se permite (ventas inmutables, RN-08)."""
    pass


class RenglonVentaRead(RenglonVenta):
    """DTO de salida de un renglón de venta."""
    id: int

    model_config = {"from_attributes": True}


class VentaRead(Venta):
    """DTO de salida de una venta (incluye cliente y renglones con precios)."""
    id: int
    fecha: datetime
    total: float
    cliente: Optional["ClienteRead"] = None
    renglones: List[RenglonVentaRead] = []

    model_config = {"from_attributes": True}


# Referencia adelante para VentaRead.cliente
from app.modules.clientes.schemas import ClienteRead  # noqa: E402

VentaRead.model_rebuild()
