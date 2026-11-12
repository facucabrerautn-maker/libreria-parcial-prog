from typing import Optional

from sqlmodel import SQLModel
from pydantic import Field as PydanticField


class ClienteCreate(SQLModel):
    """DTO de entrada para crear un cliente. No lleva id."""
    nombre: str
    email: str


class ClienteUpdate(SQLModel):
    """DTO de entrada para actualizar un cliente. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)
    email: Optional[str] = PydanticField(default=None)


class ClienteRead(SQLModel):
    """DTO de salida de un cliente (incluye perfil si existe)."""
    id: int
    nombre: str
    email: str
    perfil: Optional["PerfilRead"] = None

    model_config = {"from_attributes": True}


class PerfilCreate(SQLModel):
    """DTO de entrada para crear un perfil.

    No lleva id ni cliente_id: el cliente llega por la ruta
    POST /clientes/{cliente_id}/perfil.
    """

    telefono: Optional[str] = PydanticField(default=None)
    direccion: Optional[str] = PydanticField(default=None)


class PerfilRead(SQLModel):
    """DTO de salida de un perfil."""
    id: int
    cliente_id: int
    telefono: Optional[str] = None
    direccion: Optional[str] = None

    model_config = {"from_attributes": True}


# Referencia adelante para ClienteRead.perfil
ClienteRead.model_rebuild()
