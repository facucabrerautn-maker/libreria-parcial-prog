from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_session
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def health_live():
    """Endpoint de vida: responde inmediatamente sin tocar la base de datos."""
    return {"estado": "vivo"}


@router.get("/ready")
async def health_ready(session=Depends(get_session)):
    """Endpoint de disponibilidad: ejecuta SELECT 1 contra la base de datos.

    Devuelve 200 si la base responde, 503 si no.
    """
    try:
        await session.execute(text("SELECT 1"))
        return {"estado": "listo"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from exc
