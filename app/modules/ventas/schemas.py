from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from pydantic import field_serializer
from pydantic import Field as PydanticField
from sqlmodel import SQLModel


class RenglonVentaCreate(SQLModel):
    """DTO de entrada para un renglón de venta.

    No lleva id, precio_unitario, subtotal ni fecha: el precio se copia del
    libro y el subtotal/total los calcula el servidor (RN-06 y RN-07).
    """

    libro_id: int
    cantidad: int = PydanticField(gt=0)


class VentaCreate(SQLModel):
    """DTO de entrada para crear una venta. Incluye lista de renglones anidados."""

    cliente_id: int
    renglones: List[RenglonVentaCreate] = PydanticField(default_factory=list)


class ClienteDeVenta(SQLModel):
    """Datos mínimos del cliente que viajan en la respuesta de una venta."""

    id: int
    nombre: str
    email: str

    model_config = {"from_attributes": True}


class RenglonVentaRead(SQLModel):
    """DTO de salida de un renglón de venta."""

    libro_id: int
    titulo: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class VentaRead(SQLModel):
    """DTO de salida de una venta (con cliente y renglones con precios)."""

    id: int
    fecha: datetime
    total: Decimal
    cliente: Optional[ClienteDeVenta] = None
    renglones: List[RenglonVentaRead] = PydanticField(default_factory=list)

    model_config = {"from_attributes": True}

    @field_serializer("fecha")
    def serializar_fecha(self, fecha: datetime) -> str:
        """Serializa la fecha en ISO 8601 con zona horaria Z."""
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        return fecha.isoformat().replace("+00:00", "Z")
