from typing import List, Optional

from sqlmodel import Field, Relationship

from app.core.base import BaseModel


class Editorial(BaseModel, table=True):
    __tablename__ = "editorial"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    pais: Optional[str] = None
    libros: List["Libro"] = Relationship(back_populates="editorial")
