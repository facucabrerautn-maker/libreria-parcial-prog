from decimal import Decimal
from typing import List, Optional

from sqlalchemy import CheckConstraint, Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

from app.core.base import BaseModel


class Libro(BaseModel, table=True):
    __tablename__ = "libro"

    id: Optional[int] = Field(default=None, primary_key=True)
    isbn: str = Field(index=True, unique=True)
    titulo: str
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = 0
    editorial_id: Optional[int] = Field(
        default=None, foreign_key="editorial.id", index=True
    )
    genero_id: Optional[int] = Field(
        default=None, foreign_key="genero.id", index=True
    )

    editorial: Optional["Editorial"] = Relationship(back_populates="libros")
    genero: Optional["Genero"] = Relationship(back_populates="libros")
    autorias: List["LibroAutor"] = Relationship(back_populates="libro")
    renglones_venta: List["RenglonVenta"] = Relationship(back_populates="libro")

    __table_args__ = (
        CheckConstraint("precio > 0", name="chk_libro_precio_positivo"),
        CheckConstraint("stock >= 0", name="chk_libro_stock_no_negativo"),
    )


class LibroAutor(SQLModel, table=True):
    """Entidad de asociación Libro-Autor con datos propios (rol y orden).

    No hereda de BaseModel a propósito: la clave primaria es compuesta
    (libro_id, autor_id) y no debe llevar un id propio, tal como exige
    el modelo de datos del parcial.
    """

    __tablename__ = "libro_autor"

    libro_id: int = Field(foreign_key="libro.id", primary_key=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True)
    rol: str
    orden: int

    libro: Optional["Libro"] = Relationship(back_populates="autorias")
    autor: Optional["Autor"] = Relationship(back_populates="autorias")

    __table_args__ = (
        CheckConstraint("orden >= 1", name="chk_libro_autor_orden_positivo"),
        CheckConstraint(
            "rol IN ('autor', 'coautor', 'traductor', 'ilustrador')",
            name="chk_libro_autor_rol_valido",
        ),
    )
