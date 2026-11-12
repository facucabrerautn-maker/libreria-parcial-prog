from typing import ClassVar, Optional

from pydantic import Field as PydanticField
from sqlmodel import SQLModel

from app.core.schemas import UpdateModel


class EditorialCreate(SQLModel):
    """DTO de entrada para crear una editorial. No lleva id."""
    nombre: str
    pais: Optional[str] = PydanticField(default=None)


class EditorialUpdate(UpdateModel):
    """DTO de entrada para actualizar una editorial. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)
    pais: Optional[str] = PydanticField(default=None)

    campos_no_nulos: ClassVar[tuple[str, ...]] = ("nombre",)


class EditorialRead(SQLModel):
    """DTO de salida de una editorial."""
    id: int
    nombre: str
    pais: Optional[str] = None

    model_config = {"from_attributes": True}
