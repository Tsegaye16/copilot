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


def normalize_repository(repo: Optional[str]) -> Optional[str]:
    """Normalize repository format to owner/repo"""
    if not repo:
        return None
    
    # Remove protocol and domain if present
    normalized = repo.replace("https://github.com/", "").replace("http://github.com/", "")
    normalized = normalized.replace("https://", "").replace("http://", "").rstrip("/")
    
    # Extract owner/repo if it's a full URL
    if "/" in normalized:
        parts = normalized.split("/")
        if len(parts) >= 2:
            # Take last two parts (owner/repo)
            return f"{parts[-2]}/{parts[-1]}"
    
    return normalized if normalized else None


@router.get("/stats")
async def get_dashboard_stats(
    repository: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get dashboard statistics"""
    try:
        normalized_repo = normalize_repository(repository)
        stats = await dashboard_service.get_stats(
            repository=normalized_repo,
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
        normalized_repo = normalize_repository(repository)
        trends = await dashboard_service.get_violation_trends(
            repository=normalized_repo,
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
        normalized_repo = normalize_repository(repository)
        insights = await dashboard_service.get_copilot_insights(normalized_repo)
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
        normalized_repo = normalize_repository(repository)
        violations = await dashboard_service.get_most_common_violations(normalized_repo, limit)
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
        normalized_repo = normalize_repository(repository)
        hotspots = await dashboard_service.get_risk_hotspots(normalized_repo)
        return hotspots
    except Exception as e:
        logger.error(f"Failed to get risk hotspots: {e}")
        raise HTTPException(status_code=500, detail=str(e))
