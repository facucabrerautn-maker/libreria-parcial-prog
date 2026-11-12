from typing import Optional

from sqlmodel import SQLModel
from pydantic import Field as PydanticField


class AutorCreate(SQLModel):
    """DTO de entrada para crear un autor. No lleva id."""
    nombre: str
    nacionalidad: Optional[str] = PydanticField(default=None)


class AutorUpdate(SQLModel):
    """DTO de entrada para actualizar un autor. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)
    nacionalidad: Optional[str] = PydanticField(default=None)


class AutorRead(SQLModel):
    """DTO de salida de un autor."""
    id: int
    nombre: str
    nacionalidad: Optional[str] = None

    model_config = {"from_attributes": True}
