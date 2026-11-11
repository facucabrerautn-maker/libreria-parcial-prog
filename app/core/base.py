"""Clase base SQLModel compartida por todos los módulos.

Provee la metadata compartida que se usa con SQLModel.metadata.create_all
al arrancar la aplicación (sin migraciones en este parcial, D-04).
"""

from typing import Any, Optional

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Clase base para modelos de tabla.

    Todos los modelos de tabla heredan de esta clase para compartir
    la metadata de SQLModel y permitir create_all al arrancar.
    """

    id: Optional[int] = Field(default=None, primary_key=True)


def add_index_for_foreign_key(table_name: str, column_name: str) -> Index:
    """Crea un índice para una clave foránea.

    PostgreSQL no crea índices automáticamente para las claves foráneas
    (sección 4.10 de la consigna). Cada clave foránea debe llevar su
    propio índice.
    """
    return Index(f"ix_{table_name}_{column_name}", column_name)


def eager_load_one_to_one(query: Any, relationship_attr: str) -> Any:
    """Aplica joinedload para una relación a uno (evita N+1).

    Usar en lecturas que incluyan relaciones uno a uno o muchos a uno.
    """
    from sqlalchemy.orm import joinedload

    return query.options(joinedload(relationship_attr))


def eager_load_collection(query: Any, relationship_attr: str) -> Any:
    """Aplica selectinload para una relación de colección (evita N+1).

    Usar en lecturas que incluyan relaciones uno a muchos o muchos a muchos.
    """
    from sqlalchemy.orm import selectinload

    return query.options(selectinload(relationship_attr))
