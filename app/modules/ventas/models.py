from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Numeric
from sqlmodel import Field, Relationship

from app.core.base import BaseModel


class Venta(BaseModel, table=True):
    __tablename__ = "venta"

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", index=True)
    fecha: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    total: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))

    cliente: Optional["Cliente"] = Relationship(back_populates="ventas")
    renglones: List["RenglonVenta"] = Relationship(back_populates="venta")

    __table_args__ = (
        CheckConstraint("total >= 0", name="chk_venta_total_no_negativo"),
    )


class RenglonVenta(BaseModel, table=True):
    __tablename__ = "renglon_venta"

    id: Optional[int] = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    cantidad: int
    precio_unitario: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False)
    )

    venta: Optional["Venta"] = Relationship(back_populates="renglones")
    libro: Optional["Libro"] = Relationship(back_populates="renglones_venta")

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_renglon_venta_cantidad_positiva"),
        CheckConstraint(
            "precio_unitario > 0", name="chk_renglon_venta_precio_positivo"
        ),
    )

    @property
    def titulo(self) -> str:
        """Título del libro asociado (se usa en la respuesta de la venta)."""
        return self.libro.titulo if self.libro is not None else ""

    @property
    def subtotal(self) -> Decimal:
        """Subtotal del renglón calculado por el servidor."""
        return self.cantidad * self.precio_unitario
