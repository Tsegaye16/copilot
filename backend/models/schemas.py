"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class EnforcementMode(str, Enum):
    """Policy enforcement modes"""
    ADVISORY = "advisory"
    WARNING = "warning"
    BLOCKING = "blocking"


class Severity(str, Enum):
    """Issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationCategory(str, Enum):
    """Violation categories"""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    CODE_QUALITY = "code_quality"
    LICENSE = "license"
    IP_RISK = "ip_risk"
    STANDARD = "standard"


class CodeSource(str, Enum):
    """Code source type"""
    HUMAN = "human"
    COPILOT = "copilot"
    UNKNOWN = "unknown"


class ScanRequest(BaseModel):
    """Request model for code scanning"""
    repository: str = Field(..., description="Repository full name (owner/repo)")
    pull_request_number: Optional[int] = Field(None, description="PR number if scanning PR")
    commit_sha: Optional[str] = Field(None, description="Commit SHA if scanning commit")
    files: List[Dict[str, Any]] = Field(..., description="Files to scan with content")
    base_sha: Optional[str] = Field(None, description="Base commit SHA for diff")
    policy_config: Optional[Dict[str, Any]] = Field(None, description="Policy configuration override")
    detect_copilot: bool = Field(True, description="Whether to detect Copilot-generated code")


class Violation(BaseModel):
    """Individual violation/issue"""
    rule_id: str = Field(..., description="Rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    category: ViolationCategory = Field(..., description="Violation category")
    severity: Severity = Field(..., description="Severity level")
    file_path: str = Field(..., description="File path")
    line_number: int = Field(..., description="Line number")
    column_number: Optional[int] = Field(None, description="Column number")
    message: str = Field(..., description="Violation message")
    explanation: str = Field(..., description="Detailed explanation")
    fix_suggestion: Optional[str] = Field(None, description="Suggested fix")
    standard_mappings: List[str] = Field(default_factory=list, description="OWASP/CWE mappings")
    code_snippet: Optional[str] = Field(None, description="Code snippet")
    is_copilot_generated: bool = Field(False, description="Whether code is Copilot-generated")
    ai_confidence: Optional[float] = Field(None, description="AI confidence score (0-1)")


class ScanResult(BaseModel):
    """Scan result model"""
    scan_id: str = Field(..., description="Unique scan identifier")
    repository: str = Field(..., description="Repository name")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    violations: List[Violation] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    enforcement_action: EnforcementMode = Field(..., description="Recommended enforcement action")
    can_merge: bool = Field(..., description="Whether PR can be merged")
    copilot_detected: bool = Field(False, description="Whether Copilot code was detected")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class PolicyConfig(BaseModel):
    """Policy configuration model"""
    enforcement_mode: EnforcementMode = Field(EnforcementMode.WARNING)
    enabled_rules: List[str] = Field(default_factory=list, description="Enabled rule IDs")
    disabled_rules: List[str] = Field(default_factory=list, description="Disabled rule IDs")
    severity_threshold: Severity = Field(Severity.MEDIUM, description="Minimum severity to report")
    custom_rules: List[Dict[str, Any]] = Field(default_factory=list)
    rule_packs: List[str] = Field(default_factory=list, description="Rule pack names")
    allow_blocking_override: bool = Field(True, description="Allow override of blocking mode")


class AuditLog(BaseModel):
    """Audit log entry"""
    log_id: str
    timestamp: datetime
    repository: str
    action: str
    user: Optional[str]
    details: Dict[str, Any]
    violations_count: int
    enforcement_action: EnforcementMode
    resolved: bool = False
