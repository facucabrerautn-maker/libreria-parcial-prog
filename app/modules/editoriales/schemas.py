from typing import List, Optional

from sqlmodel import SQLModel
from pydantic import Field as PydanticField


class EditorialCreate(SQLModel):
    """DTO de entrada para crear una editorial. No lleva id."""
    nombre: str
    pais: Optional[str] = PydanticField(default=None)


class EditorialUpdate(SQLModel):
    """DTO de entrada para actualizar una editorial. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)
    pais: Optional[str] = PydanticField(default=None)


class EditorialRead(SQLModel):
    """DTO de salida de una editorial."""
    id: int
    nombre: str
    pais: Optional[str] = None

    model_config = {"from_attributes": True}
