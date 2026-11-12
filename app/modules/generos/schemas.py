from typing import Optional

from sqlmodel import SQLModel
from pydantic import Field as PydanticField


class GeneroCreate(SQLModel):
    """DTO de entrada para crear un género. No lleva id."""
    nombre: str


class GeneroUpdate(SQLModel):
    """DTO de entrada para actualizar un género. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)


class GeneroRead(SQLModel):
    """DTO de salida de un género."""
    id: int
    nombre: str

    model_config = {"from_attributes": True}
