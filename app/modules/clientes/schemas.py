from typing import List, Optional

from pydantic import Field as PydanticField

from app.modules.clientes.models import Cliente, PerfilCliente


class ClienteCreate(Cliente):
    """DTO de entrada para crear un cliente. No lleva id."""
    pass


class ClienteUpdate(Cliente):
    """DTO de entrada para actualizar un cliente. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)
    email: Optional[str] = PydanticField(default=None)


class ClienteRead(Cliente):
    """DTO de salida de un cliente (incluye perfil si existe)."""
    id: int
    perfil: Optional["PerfilClienteRead"] = None

    model_config = {"from_attributes": True}


class PerfilCreate(PerfilCliente):
    """DTO de entrada para crear un perfil. No lleva id."""
    pass


class PerfilRead(PerfilCliente):
    """DTO de salida de un perfil."""
    id: int

    model_config = {"from_attributes": True}


# Referencia adelante para ClienteRead.perfil
ClienteRead.model_rebuild()
