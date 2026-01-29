"""
Audit logging system with file-based persistence
"""
import uuid
import logging
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
try:
    from models.schemas import AuditLog, ScanResult, ScanRequest, EnforcementMode
    from core.config import settings
except ImportError:
    from ..models.schemas import AuditLog, ScanResult, ScanRequest, EnforcementMode
    from ..core.config import settings

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logging service with file-based persistence"""
    
    def __init__(self, log_file: Optional[str] = None):
        # Use file-based persistence
        self.log_file = log_file or getattr(settings, 'AUDIT_LOG_FILE', './logs/audit_logs.json')
        self.logs: List[AuditLog] = []
        self._ensure_log_directory()
        self._load_logs()
        logger.info(f"Audit logger initialized with {len(self.logs)} existing logs")
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_logs(self):
        """Load logs from file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    for log_data in data:
                        try:
                            # Convert timestamp string back to datetime
                            if isinstance(log_data.get('timestamp'), str):
                                log_data['timestamp'] = datetime.fromisoformat(log_data['timestamp'])
                            log = AuditLog(**log_data)
                            self.logs.append(log)
                        except Exception as e:
                            logger.warning(f"Failed to load audit log entry: {e}")
                            continue
                logger.info(f"Loaded {len(self.logs)} audit logs from {self.log_file}")
        except Exception as e:
            logger.warning(f"Failed to load audit logs from file: {e}")
            self.logs = []
    
    def _save_logs(self):
        """Save logs to file"""
        try:
            with open(self.log_file, 'w') as f:
                logs_data = []
                for log in self.logs:
                    log_dict = log.dict()
                    # Convert datetime to ISO string for JSON serialization
                    if isinstance(log_dict.get('timestamp'), datetime):
                        log_dict['timestamp'] = log_dict['timestamp'].isoformat()
                    logs_data.append(log_dict)
                json.dump(logs_data, f, indent=2, default=str)
            logger.debug(f"Saved {len(self.logs)} audit logs to {self.log_file}")
        except Exception as e:
            logger.error(f"Failed to save audit logs to file: {e}")
    
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
            
            # Persist to file
            self._save_logs()
            
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
            # Normalize repository format (handle both URL and owner/repo)
            normalized_repo = self._normalize_repository(repository)
            filtered_logs = [
                log for log in filtered_logs 
                if self._normalize_repository(log.repository) == normalized_repo
            ]
        
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
    
    def _normalize_repository(self, repo: str) -> str:
        """Normalize repository format to owner/repo"""
        if not repo:
            return ""
        
        # Remove protocol and domain if present
        repo = repo.replace("https://github.com/", "").replace("http://github.com/", "")
        repo = repo.replace("https://", "").replace("http://", "")
        
        # Remove trailing slash
        repo = repo.rstrip("/")
        
        # Extract owner/repo if it's a full URL
        if "/" in repo:
            parts = repo.split("/")
            if len(parts) >= 2:
                # Take last two parts (owner/repo)
                return f"{parts[-2]}/{parts[-1]}"
        
        return repo