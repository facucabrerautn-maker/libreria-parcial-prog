from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel
from pydantic import Field as PydanticField


class RenglonVentaCreate(SQLModel):
    """DTO de entrada para un renglón de venta. No lleva id ni precio_unitario (se copia del libro)."""
    libro_id: int
    cantidad: int


class VentaCreate(SQLModel):
    """DTO de entrada para crear una venta. Incluye lista de renglones anidados."""
    cliente_id: int
    renglones: List[RenglonVentaCreate] = []


class RenglonVentaRead(SQLModel):
    """DTO de salida de un renglón de venta."""
    id: int
    venta_id: int
    libro_id: int
    cantidad: int
    precio_unitario: float

    model_config = {"from_attributes": True}


class VentaRead(SQLModel):
    """DTO de salida de una venta (incluye cliente y renglones con precios)."""
    id: int
    cliente_id: int
    fecha: datetime
    total: float
    renglones: List[RenglonVentaRead] = []

    model_config = {"from_attributes": True}
