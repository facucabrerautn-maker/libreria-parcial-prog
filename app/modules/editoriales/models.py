from typing import Optional

from sqlmodel import Field

from app.core.base import BaseModel


class Editorial(BaseModel, table=True):
    __tablename__ = "editorial"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    pais: Optional[str] = None

    # La relación con Libro se completa en C-07 (libros-con-autores)
