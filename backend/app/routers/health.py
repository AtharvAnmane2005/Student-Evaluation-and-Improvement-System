"""
Health check endpoint.

Render (and any uptime monitor) pings this to know the service and its
database connection are alive. Kept dependency-free of auth so it's always
reachable.
"""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncIOMotorDatabase = Depends(get_database)) -> dict:
    db_status = "unknown"
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "unreachable"

    return {
        "status": "ok",
        "database": db_status,
    }
