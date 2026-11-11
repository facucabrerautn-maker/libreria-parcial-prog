from typing import Optional

from pydantic import Field as PydanticField

from app.modules.autores.models import Autor


class AutorCreate(Autor):
    """DTO de entrada para crear un autor. No lleva id."""
    pass


class AutorUpdate(Autor):
    """DTO de entrada para actualizar un autor. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)
    nacionalidad: Optional[str] = PydanticField(default=None)


class AutorRead(Autor):
    """DTO de salida de un autor."""
    id: int

    model_config = {"from_attributes": True}
