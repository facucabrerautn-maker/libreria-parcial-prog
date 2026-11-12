from datetime import datetime
from typing import List, Optional

from sqlalchemy import CheckConstraint, ForeignKey
from sqlmodel import Field, Relationship

from app.core.base import BaseModel


class Venta(BaseModel, table=True):
    __tablename__ = "venta"

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id")
    fecha: datetime
    total: float

    cliente: Optional["Cliente"] = Relationship(back_populates="ventas")
    renglones: List["RenglonVenta"] = Relationship(back_populates="venta")

    __table_args__ = (
        CheckConstraint("total >= 0", name="chk_venta_total_no_negativo"),
    )


class RenglonVenta(BaseModel, table=True):
    __tablename__ = "renglon_venta"

    id: Optional[int] = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id")
    libro_id: int = Field(foreign_key="libro.id")
    cantidad: int
    precio_unitario: float

    venta: Optional["Venta"] = Relationship(back_populates="renglones")
    libro: Optional["Libro"] = Relationship(back_populates="renglones_venta")

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_renglon_venta_cantidad_positiva"),
        CheckConstraint(
            "precio_unitario > 0", name="chk_renglon_venta_precio_positivo"
        ),
    )
