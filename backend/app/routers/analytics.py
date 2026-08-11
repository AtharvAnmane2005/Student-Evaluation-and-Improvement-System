from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.deps import CurrentUser, require_role
from app.models.analytics import AdminAnalyticsResponse, TpoAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/tpo", response_model=TpoAnalyticsResponse)
async def get_tpo_analytics(
    current_user: CurrentUser = Depends(require_role("tpo")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = AnalyticsService(db)
    return await service.get_tpo_analytics(current_user.id)


@router.get("/admin", response_model=AdminAnalyticsResponse)
async def get_admin_analytics(
    current_user: CurrentUser = Depends(require_role("admin")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = AnalyticsService(db)
    return await service.get_admin_analytics()
