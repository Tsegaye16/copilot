"""
Scan API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging

from ..models.schemas import ScanRequest, ScanResult
from ..core.scanner import CodeScanner
from ..core.audit import AuditLogger

router = APIRouter()
logger = logging.getLogger(__name__)

scanner = CodeScanner()
audit_logger = AuditLogger()


@router.post("/", response_model=ScanResult)
async def scan_code(request: ScanRequest, background_tasks: BackgroundTasks):
    """Scan code for violations"""
    try:
        result = await scanner.scan(request)
        
        # Log audit event in background
        background_tasks.add_task(
            audit_logger.log_scan,
            result,
            request
        )
        
        return result
    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pr/{owner}/{repo}/{pr_number}")
async def scan_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    background_tasks: BackgroundTasks
):
    """Scan a GitHub pull request"""
    # This would integrate with GitHub API to fetch PR files
    # For now, return a placeholder
    raise HTTPException(
        status_code=501,
        detail="PR scanning will be implemented via GitHub App"
    )


@router.post("/commit/{owner}/{repo}/{commit_sha}")
async def scan_commit(
    owner: str,
    repo: str,
    commit_sha: str,
    background_tasks: BackgroundTasks
):
    """Scan a specific commit"""
    # This would integrate with GitHub API to fetch commit files
    raise HTTPException(
        status_code=501,
        detail="Commit scanning will be implemented via GitHub App"
    )
