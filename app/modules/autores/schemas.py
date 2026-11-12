from typing import ClassVar, Optional

from pydantic import Field as PydanticField
from sqlmodel import SQLModel

from app.core.schemas import UpdateModel


class AutorCreate(SQLModel):
    """DTO de entrada para crear un autor. No lleva id."""
    nombre: str
    nacionalidad: Optional[str] = PydanticField(default=None)


class AutorUpdate(UpdateModel):
    """DTO de entrada para actualizar un autor. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)
    nacionalidad: Optional[str] = PydanticField(default=None)

    campos_no_nulos: ClassVar[tuple[str, ...]] = ("nombre",)


class AutorRead(SQLModel):
    """DTO de salida de un autor."""
    id: int
    nombre: str
    nacionalidad: Optional[str] = None

    model_config = {"from_attributes": True}
