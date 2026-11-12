from typing import ClassVar, Optional

from pydantic import Field as PydanticField
from sqlmodel import SQLModel

from app.core.schemas import UpdateModel


class GeneroCreate(SQLModel):
    """DTO de entrada para crear un género. No lleva id."""
    nombre: str


class GeneroUpdate(UpdateModel):
    """DTO de entrada para actualizar un género. Campos opcionales (PATCH parcial)."""
    nombre: Optional[str] = PydanticField(default=None)

    campos_no_nulos: ClassVar[tuple[str, ...]] = ("nombre",)


class GeneroRead(SQLModel):
    """DTO de salida de un género."""
    id: int
    nombre: str

    model_config = {"from_attributes": True}
