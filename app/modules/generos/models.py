from typing import List, Optional

from sqlmodel import Field, Relationship

from app.core.base import BaseModel


class Genero(BaseModel, table=True):
    __tablename__ = "genero"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    libros: List["Libro"] = Relationship(back_populates="genero")
