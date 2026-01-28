"""
Dashboard and reporting API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import logging

try:
    from core.dashboard import DashboardService
except ImportError:
    from ..core.dashboard import DashboardService

router = APIRouter()
logger = logging.getLogger(__name__)

dashboard_service = DashboardService()


@router.get("/stats")
async def get_dashboard_stats(
    repository: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get dashboard statistics"""
    try:
        stats = await dashboard_service.get_stats(
            repository=repository,
            start_date=start_date,
            end_date=end_date
        )
        return stats
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/violations/trends")
async def get_violation_trends(
    repository: Optional[str] = Query(None),
    days: int = Query(30, le=365)
):
    """Get violation trends over time"""
    try:
        trends = await dashboard_service.get_violation_trends(
            repository=repository,
            days=days
        )
        return trends
    except Exception as e:
        logger.error(f"Failed to get violation trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/copilot/insights")
async def get_copilot_insights(
    repository: Optional[str] = Query(None)
):
    """Get Copilot-related insights"""
    try:
        insights = await dashboard_service.get_copilot_insights(repository)
        return insights
    except Exception as e:
        logger.error(f"Failed to get Copilot insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/violations/common")
async def get_most_common_violations(
    repository: Optional[str] = Query(None),
    limit: int = Query(10, le=100)
):
    """Get most common violations"""
    try:
        violations = await dashboard_service.get_most_common_violations(repository, limit)
        return violations
    except Exception as e:
        logger.error(f"Failed to get common violations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/hotspots")
async def get_risk_hotspots(
    repository: Optional[str] = Query(None)
):
    """Get risk hotspots - repositories/files with most violations"""
    try:
        hotspots = await dashboard_service.get_risk_hotspots(repository)
        return hotspots
    except Exception as e:
        logger.error(f"Failed to get risk hotspots: {e}")
        raise HTTPException(status_code=500, detail=str(e))
