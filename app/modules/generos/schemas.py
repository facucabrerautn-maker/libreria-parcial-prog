from typing import Optional

from pydantic import Field as PydanticField

from app.modules.generos.models import Genero


class GeneroCreate(Genero):
    """DTO de entrada para crear un género. No lleva id."""
    pass


class GeneroUpdate(Genero):
    """DTO de entrada para actualizar un género. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)


class GeneroRead(Genero):
    """DTO de salida de un género."""
    id: int

    model_config = {"from_attributes": True}
