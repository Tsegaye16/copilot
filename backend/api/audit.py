"""
Audit logging API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.schemas import AuditLog
from ..core.audit import AuditLogger

router = APIRouter()
logger = logging.getLogger(__name__)

audit_logger = AuditLogger()


@router.get("/logs", response_model=List[AuditLog])
async def get_audit_logs(
    repository: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000)
):
    """Get audit logs with filtering"""
    try:
        logs = await audit_logger.get_logs(
            repository=repository,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return logs
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/export")
async def export_audit_logs(
    repository: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    format: str = Query("json", regex="^(json|csv)$")
):
    """Export audit logs"""
    try:
        export_data = await audit_logger.export_logs(
            repository=repository,
            start_date=start_date,
            end_date=end_date,
            format=format
        )
        return export_data
    except Exception as e:
        logger.error(f"Failed to export audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
