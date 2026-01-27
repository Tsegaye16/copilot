"""
Dashboard and reporting service
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ..core.audit import AuditLogger

logger = logging.getLogger(__name__)


class DashboardService:
    """Dashboard statistics and reporting service"""
    
    def __init__(self):
        self.audit_logger = AuditLogger()
    
    async def get_stats(
        self,
        repository: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get dashboard statistics"""
        logs = await self.audit_logger.get_logs(
            repository=repository,
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        total_scans = len(logs)
        total_violations = sum(log.violations_count for log in logs)
        
        enforcement_counts = {}
        for log in logs:
            mode = log.enforcement_action.value
            enforcement_counts[mode] = enforcement_counts.get(mode, 0) + 1
        
        return {
            "total_scans": total_scans,
            "total_violations": total_violations,
            "average_violations_per_scan": total_violations / total_scans if total_scans > 0 else 0,
            "enforcement_distribution": enforcement_counts,
            "resolved_count": len([log for log in logs if log.resolved]),
            "unresolved_count": len([log for log in logs if not log.resolved])
        }
    
    async def get_violation_trends(
        self,
        repository: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get violation trends over time"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        logs = await self.audit_logger.get_logs(
            repository=repository,
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Group by date
        daily_stats = {}
        for log in logs:
            date_key = log.timestamp.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "date": date_key,
                    "scans": 0,
                    "violations": 0
                }
            daily_stats[date_key]["scans"] += 1
            daily_stats[date_key]["violations"] += log.violations_count
        
        return {
            "period_days": days,
            "daily_trends": list(daily_stats.values())
        }
    
    async def get_copilot_insights(
        self,
        repository: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Copilot-related insights"""
        logs = await self.audit_logger.get_logs(
            repository=repository,
            limit=10000
        )
        
        copilot_scans = [
            log for log in logs
            if log.details.get("copilot_detected", False)
        ]
        
        copilot_violations = sum(log.violations_count for log in copilot_scans)
        total_violations = sum(log.violations_count for log in logs)
        
        return {
            "copilot_scans_count": len(copilot_scans),
            "total_scans_count": len(logs),
            "copilot_scan_percentage": (len(copilot_scans) / len(logs) * 100) if logs else 0,
            "copilot_violations": copilot_violations,
            "total_violations": total_violations,
            "copilot_violation_rate": (copilot_violations / len(copilot_scans)) if copilot_scans else 0,
            "average_violation_rate": (total_violations / len(logs)) if logs else 0
        }
