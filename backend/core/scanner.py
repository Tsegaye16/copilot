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
    from engines.coding_standards import CodingStandardsEngine
    from engines.duplicate_detector import DuplicateDetector
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
        self.coding_standards = CodingStandardsEngine()
        self.duplicate_detector = DuplicateDetector()
    
    async def scan(self, request: ScanRequest) -> ScanResult:
        """Perform comprehensive code scan"""
        start_time = time.time()
        scan_id = str(uuid.uuid4())
        
        logger.info(f"Starting scan {scan_id} for {request.repository}")
        
        # Enforce data residency and code retention policies
        self._enforce_data_policies(request)
        
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
                    if self.ai_analyzer.enabled:
                        logger.info(f"AI analyzer is enabled, running analysis for {file_path}")
                        ai_violations = await self.ai_analyzer.analyze_code(
                            file_path, content, metadata, is_copilot
                        )
                        all_violations.extend(ai_violations)
                        logger.info(f"AI analyzer found {len(ai_violations)} additional violations")
                    else:
                        logger.warning(f"AI analyzer is disabled (GEMINI_API_KEY not set), skipping AI analysis")
                    
                    # Enhance static violations with AI-generated fix suggestions if AI is enabled
                    if self.ai_analyzer.enabled and static_violations:
                        logger.info(f"Enhancing {len(static_violations)} static violations with AI suggestions for {file_path}")
                        enhanced_count = 0
                        for violation in static_violations:
                            # Check if suggestion is generic (common generic phrases)
                            generic_phrases = [
                                "Use environment variables",
                                "Use safer alternatives",
                                "implement strict input validation",
                                "Use parameterized queries"
                            ]
                            is_generic = not violation.fix_suggestion or any(
                                phrase.lower() in violation.fix_suggestion.lower() 
                                for phrase in generic_phrases
                            )
                            
                            # Always enhance with AI if enabled (AI provides better contextual suggestions)
                            if is_generic or not violation.fix_suggestion:
                                try:
                                    # Get code context around the violation line (more context for better suggestions)
                                    lines = content.split('\n')
                                    start_line = max(0, violation.line_number - 10)
                                    end_line = min(len(lines), violation.line_number + 10)
                                    code_context = '\n'.join(lines[start_line:end_line])
                                    
                                    # Get AI-suggested fix with full context
                                    logger.debug(f"Requesting AI fix suggestion for {violation.rule_id} at line {violation.line_number}")
                                    ai_fix = await self.ai_analyzer.suggest_fix(violation, code_context)
                                    if ai_fix and len(ai_fix.strip()) > 20:  # Ensure AI suggestion is meaningful
                                        old_suggestion = violation.fix_suggestion[:50] + "..." if violation.fix_suggestion and len(violation.fix_suggestion) > 50 else violation.fix_suggestion
                                        violation.fix_suggestion = ai_fix
                                        enhanced_count += 1
                                        logger.info(f"✓ Enhanced violation {violation.rule_id} with AI suggestion (was: '{old_suggestion}')")
                                    else:
                                        logger.debug(f"AI suggestion for {violation.rule_id} was too short or empty ({len(ai_fix) if ai_fix else 0} chars), keeping static suggestion")
                                except Exception as e:
                                    logger.warning(f"Failed to enhance violation {violation.rule_id} with AI: {e}")
                                    logger.debug(f"Error details: {type(e).__name__}: {str(e)}")
                                    # Continue with existing fix suggestion
                            else:
                                logger.debug(f"Skipping AI enhancement for {violation.rule_id} - already has specific suggestion")
                        
                        logger.info(f"Enhanced {enhanced_count}/{len(static_violations)} violations with AI suggestions")
                except Exception as e:
                    logger.warning(f"AI analysis failed for {file_path}: {e}")
                    logger.debug(f"AI error details: {type(e).__name__}: {str(e)}")
                    # Continue without AI analysis if it fails
                
                # License checking
                try:
                    license_violations = self.license_checker.check_file(file_path, content)
                    all_violations.extend(license_violations)
                except Exception as e:
                    logger.warning(f"License checking failed for {file_path}: {e}")
                
                # Enterprise coding standards checking
                try:
                    # Get custom standards from policy if available
                    custom_standards = policy.custom_rules if hasattr(policy, 'custom_rules') else None
                    standards_violations = self.coding_standards.analyze_file(
                        file_path, content, is_copilot, custom_standards
                    )
                    all_violations.extend(standards_violations)
                except Exception as e:
                    logger.warning(f"Coding standards check failed for {file_path}: {e}")
            except Exception as e:
                logger.error(f"Error processing file {file_data.get('path', 'unknown')}: {e}")
                continue
        
        # Apply policy filtering
        filtered_violations = self.policy_engine.filter_violations(
            all_violations, policy
        )
        
        # Apply rule packs if specified
        for pack_name in policy.rule_packs:
            # Apply rule pack to each file
            for file_data in request.files:
                file_path = file_data.get("path", "")
                content = file_data.get("content", "")
                filtered_violations = self.policy_engine.apply_rule_pack(
                    filtered_violations, pack_name, file_path, content
                )
        
        # Detect duplicate code patterns
        try:
            duplicate_violations = self.duplicate_detector.detect_duplicates(
                request.files, request.repository
            )
            filtered_violations.extend(duplicate_violations)
            logger.info(f"Duplicate detection found {len(duplicate_violations)} violations")
        except Exception as e:
            logger.warning(f"Duplicate detection failed: {e}")
        
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
    
    def _enforce_data_policies(self, request: ScanRequest):
        """Enforce data residency and code retention policies"""
        from core.config import settings
        
        # Data residency enforcement
        if settings.DATA_RESIDENCY_REGION:
            logger.info(f"Data residency region: {settings.DATA_RESIDENCY_REGION}")
            # In production, this would route data processing to the specified region
            # For now, we just log it
        
        # Code retention prevention
        if not settings.ENABLE_CODE_RETENTION:
            logger.info("Code retention disabled - code will not be stored after analysis")
            # Ensure code content is not persisted beyond scan completion
            # The code is already processed in-memory and not stored in database