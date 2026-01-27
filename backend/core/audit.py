"""
Audit logging system
"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..models.schemas import AuditLog, ScanResult, ScanRequest, EnforcementMode
from ..core.config import settings

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logging service"""
    
    def __init__(self):
        # In production, this would use a database
        # For now, we'll use in-memory storage
        self.logs: List[AuditLog] = []
        logger.info("Audit logger initialized")
    
    async def log_scan(self, result: ScanResult, request: ScanRequest):
        """Log a scan event"""
        try:
            log_entry = AuditLog(
                log_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                repository=result.repository,
                action="scan",
                user=None,  # Would be populated from GitHub context
                details={
                    "scan_id": result.scan_id,
                    "pull_request": request.pull_request_number,
                    "commit_sha": request.commit_sha,
                    "files_scanned": len(request.files),
                    "copilot_detected": result.copilot_detected
                },
                violations_count=len(result.violations),
                enforcement_action=result.enforcement_action,
                resolved=False
            )
            
            self.logs.append(log_entry)
            
            # In production, persist to database
            logger.info(f"Audit log created: {log_entry.log_id}")
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
    
    async def get_logs(
        self,
        repository: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Retrieve audit logs with filtering"""
        filtered_logs = self.logs
        
        if repository:
            filtered_logs = [log for log in filtered_logs if log.repository == repository]
        
        if start_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_date]
        
        if end_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_date]
        
        # Sort by timestamp descending
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_logs[:limit]
    
    async def export_logs(
        self,
        repository: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export audit logs in specified format"""
        logs = await self.get_logs(repository, start_date, end_date, limit=10000)
        
        if format == "json":
            return {
                "format": "json",
                "count": len(logs),
                "logs": [log.dict() for log in logs]
            }
        elif format == "csv":
            # Generate CSV
            csv_lines = ["log_id,timestamp,repository,action,violations_count,enforcement_action,resolved"]
            for log in logs:
                csv_lines.append(
                    f"{log.log_id},{log.timestamp.isoformat()},{log.repository},"
                    f"{log.action},{log.violations_count},{log.enforcement_action.value},{log.resolved}"
                )
            return {
                "format": "csv",
                "count": len(logs),
                "content": "\n".join(csv_lines)
            }
        
        raise ValueError(f"Unsupported format: {format}")
