from typing import Optional

from sqlmodel import Field, Relationship

from app.core.base import BaseModel


class Cliente(BaseModel, table=True):
    __tablename__ = "cliente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(index=True, unique=True)

    perfil: Optional["PerfilCliente"] = Relationship(back_populates="cliente", sa_relationship_kwargs={"uselist": False})


class PerfilCliente(BaseModel, table=True):
    __tablename__ = "perfil_cliente"

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", unique=True)
    telefono: Optional[str] = None
    direccion: Optional[str] = None

    cliente: Optional["Cliente"] = Relationship(back_populates="perfil")
