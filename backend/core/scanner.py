"""
Main scanning orchestrator combining all analysis engines
"""
import time
import logging
import uuid
from typing import List, Dict, Any, Optional
try:
    from models.schemas import (
        ScanRequest, ScanResult, Violation, EnforcementMode, PolicyConfig
    )
    from engines.static_analyzer import StaticAnalyzer
    from engines.ai_analyzer import AIAnalyzer
    from engines.copilot_detector import CopilotDetector
    from engines.license_checker import LicenseChecker
    from engines.policy_engine import PolicyEngine
except ImportError:
    from ..models.schemas import (
        ScanRequest, ScanResult, Violation, EnforcementMode, PolicyConfig
    )
    from ..engines.static_analyzer import StaticAnalyzer
    from ..engines.ai_analyzer import AIAnalyzer
    from ..engines.copilot_detector import CopilotDetector
    from ..engines.license_checker import LicenseChecker
    from ..engines.policy_engine import PolicyEngine

logger = logging.getLogger(__name__)


class CodeScanner:
    """Main code scanning orchestrator"""
    
    def __init__(self):
        self.static_analyzer = StaticAnalyzer()
        self.ai_analyzer = AIAnalyzer()
        self.copilot_detector = CopilotDetector()
        self.license_checker = LicenseChecker()
        self.policy_engine = PolicyEngine()
    
    async def scan(self, request: ScanRequest) -> ScanResult:
        """Perform comprehensive code scan"""
        start_time = time.time()
        scan_id = str(uuid.uuid4())
        
        logger.info(f"Starting scan {scan_id} for {request.repository}")
        
        all_violations: List[Violation] = []
        copilot_detected = False
        
        # Get policy configuration
        policy = self.policy_engine.get_policy(
            request.repository,
            request.policy_config
        )
        
        # Process each file
        for file_data in request.files:
            try:
                file_path = file_data.get("path", "")
                content = file_data.get("content", "")
                metadata = file_data.get("metadata", {})
                
                if not file_path:
                    logger.warning("Skipping file with no path")
                    continue
                
                # Detect Copilot code
                is_copilot = False
                if request.detect_copilot:
                    try:
                        is_copilot = self.copilot_detector.detect(content, metadata)
                        if is_copilot:
                            copilot_detected = True
                            logger.info(f"Copilot code detected in {file_path}")
                    except Exception as e:
                        logger.warning(f"Copilot detection failed for {file_path}: {e}")
                
                # Static analysis
                static_violations = []
                try:
                    static_violations = self.static_analyzer.analyze_file(
                        file_path, content, is_copilot
                    )
                    all_violations.extend(static_violations)
                except Exception as e:
                    logger.error(f"Static analysis failed for {file_path}: {e}")
                
                # AI analysis (async) - both for finding new violations and enhancing existing ones
                try:
                    ai_violations = await self.ai_analyzer.analyze_code(
                        file_path, content, metadata, is_copilot
                    )
                    all_violations.extend(ai_violations)
                    
                    # Enhance static violations with AI-generated fix suggestions if AI is enabled
                    if self.ai_analyzer.enabled and static_violations:
                        logger.info(f"Enhancing {len(static_violations)} static violations with AI suggestions for {file_path}")
                        for violation in static_violations:
                            # Only enhance if violation doesn't have a good fix suggestion or it's generic
                            if not violation.fix_suggestion or len(violation.fix_suggestion) < 50:
                                try:
                                    # Get code context around the violation line
                                    lines = content.split('\n')
                                    start_line = max(0, violation.line_number - 5)
                                    end_line = min(len(lines), violation.line_number + 5)
                                    code_context = '\n'.join(lines[start_line:end_line])
                                    
                                    # Get AI-suggested fix
                                    ai_fix = await self.ai_analyzer.suggest_fix(violation, code_context)
                                    if ai_fix:
                                        violation.fix_suggestion = ai_fix
                                        logger.debug(f"Enhanced violation {violation.rule_id} with AI suggestion")
                                except Exception as e:
                                    logger.warning(f"Failed to enhance violation {violation.rule_id} with AI: {e}")
                                    # Continue with existing fix suggestion
                except Exception as e:
                    logger.warning(f"AI analysis failed for {file_path}: {e}")
                    # Continue without AI analysis if it fails
                
                # License checking
                try:
                    license_violations = self.license_checker.check_file(file_path, content)
                    all_violations.extend(license_violations)
                except Exception as e:
                    logger.warning(f"License checking failed for {file_path}: {e}")
            except Exception as e:
                logger.error(f"Error processing file {file_data.get('path', 'unknown')}: {e}")
                continue
        
        # Apply policy filtering
        filtered_violations = self.policy_engine.filter_violations(
            all_violations, policy
        )
        
        # Apply rule packs if specified
        for pack_name in policy.rule_packs:
            filtered_violations = self.policy_engine.apply_rule_pack(
                filtered_violations, pack_name
            )
        
        # Determine enforcement action (with override support)
        override_requested = getattr(request, 'override_blocking', False)
        enforcement_action, can_merge = self.policy_engine.determine_enforcement(
            filtered_violations, policy, override_requested=override_requested
        )
        
        # Build summary
        summary = self._build_summary(filtered_violations)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        result = ScanResult(
            scan_id=scan_id,
            repository=request.repository,
            violations=filtered_violations,
            summary=summary,
            enforcement_action=enforcement_action,
            can_merge=can_merge,
            copilot_detected=copilot_detected,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Scan {scan_id} completed: {len(filtered_violations)} violations, "
                   f"enforcement={enforcement_action}, can_merge={can_merge}")
        
        return result
    
    def _build_summary(self, violations: List[Violation]) -> Dict[str, Any]:
        """Build summary statistics"""
        summary = {
            "total_violations": len(violations),
            "by_severity": {
                "critical": len([v for v in violations if v.severity.value == "critical"]),
                "high": len([v for v in violations if v.severity.value == "high"]),
                "medium": len([v for v in violations if v.severity.value == "medium"]),
                "low": len([v for v in violations if v.severity.value == "low"]),
            },
            "by_category": {},
            "copilot_violations": len([v for v in violations if v.is_copilot_generated]),
            "files_affected": len(set(v.file_path for v in violations))
        }
        
        # Count by category
        for violation in violations:
            category = violation.category.value
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        return summary
