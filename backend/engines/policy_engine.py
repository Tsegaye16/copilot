"""
Policy engine for rule management and enforcement
Supports override capability for blocking mode
"""
import yaml
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
try:
    from models.schemas import PolicyConfig, EnforcementMode, Violation, Severity
except ImportError:
    from ..models.schemas import PolicyConfig, EnforcementMode, Violation, Severity

logger = logging.getLogger(__name__)


class PolicyEngine:
    """Policy management and enforcement engine"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.policies: Dict[str, PolicyConfig] = {}
        self.rule_packs: Dict[str, Dict[str, Any]] = {}
        self.config_path = config_path or "config/policies"
        self._load_rule_packs()
    
    def _load_rule_packs(self):
        """Load enterprise rule packs"""
        rule_pack_dir = Path("config/rule_packs")
        if not rule_pack_dir.exists():
            logger.warning(f"Rule packs directory not found: {rule_pack_dir}")
            return
        
        for pack_file in rule_pack_dir.glob("*.yaml"):
            try:
                with open(pack_file, 'r') as f:
                    pack_data = yaml.safe_load(f)
                    pack_name = pack_file.stem
                    self.rule_packs[pack_name] = pack_data
                    logger.info(f"Loaded rule pack: {pack_name}")
            except Exception as e:
                logger.error(f"Failed to load rule pack {pack_file}: {e}")
    
    def get_policy(self, repository: str, override: Optional[Dict[str, Any]] = None) -> PolicyConfig:
        """Get policy configuration for a repository"""
        # Extract organization from repository (format: org/repo)
        org_name = None
        if '/' in repository:
            org_name = repository.split('/')[0]
        
        # Check for organization-level policy first
        if org_name:
            org_policy_path = Path(f"{self.config_path}/organizations/{org_name}.yaml")
            if org_policy_path.exists():
                try:
                    with open(org_policy_path, 'r') as f:
                        org_policy_data = yaml.safe_load(f)
                        policy = PolicyConfig(**org_policy_data)
                        logger.info(f"Loaded organization policy for {org_name}")
                        # Apply override if provided
                        if override:
                            for key, value in override.items():
                                if hasattr(policy, key):
                                    setattr(policy, key, value)
                        return policy
                except Exception as e:
                    logger.warning(f"Failed to load organization policy: {e}")
        
        # Check for repository-specific policy
        repo_policy_path = Path(f"{self.config_path}/{repository}.yaml")
        
        if repo_policy_path.exists():
            try:
                with open(repo_policy_path, 'r') as f:
                    policy_data = yaml.safe_load(f)
                    return PolicyConfig(**policy_data)
            except Exception as e:
                logger.error(f"Failed to load policy for {repository}: {e}")
        
        # Use default policy
        default_policy = PolicyConfig()
        
        # Apply override if provided
        if override:
            for key, value in override.items():
                if hasattr(default_policy, key):
                    setattr(default_policy, key, value)
        
        return default_policy
    
    def filter_violations(
        self,
        violations: List[Violation],
        policy: PolicyConfig
    ) -> List[Violation]:
        """Filter violations based on policy configuration"""
        filtered = []
        
        for violation in violations:
            # Check if rule is enabled
            if policy.enabled_rules and violation.rule_id not in policy.enabled_rules:
                continue
            
            # Check if rule is disabled
            if violation.rule_id in policy.disabled_rules:
                continue
            
            # Check severity threshold
            severity_order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
            if severity_order.index(violation.severity) < severity_order.index(policy.severity_threshold):
                continue
            
            filtered.append(violation)
        
        return filtered
    
    def determine_enforcement(
        self,
        violations: List[Violation],
        policy: PolicyConfig,
        override_requested: bool = False
    ) -> Tuple[EnforcementMode, bool]:
        """Determine enforcement action and merge eligibility
        
        Args:
            violations: List of detected violations
            policy: Policy configuration
            override_requested: Whether user requested to override blocking
            
        Returns:
            Tuple of (enforcement_mode, can_merge)
        """
        if not violations:
            return EnforcementMode.ADVISORY, True
        
        # Check for critical violations
        critical_violations = [v for v in violations if v.severity == Severity.CRITICAL]
        high_violations = [v for v in violations if v.severity == Severity.HIGH]
        
        # Apply stricter rules for Copilot-generated code
        copilot_violations = [v for v in violations if v.is_copilot_generated]
        copilot_critical = [v for v in copilot_violations if v.severity == Severity.CRITICAL]
        
        if policy.enforcement_mode == EnforcementMode.BLOCKING:
            # Check if override is allowed and requested
            if override_requested and policy.allow_blocking_override:
                # Allow override but still show warnings
                if critical_violations or copilot_critical or high_violations:
                    return EnforcementMode.WARNING, True
                else:
                    return EnforcementMode.ADVISORY, True
            
            # Stricter blocking for Copilot-generated critical violations
            if copilot_critical:
                return EnforcementMode.BLOCKING, False
            
            # Block on ANY critical violations OR ANY high violations (standard convention)
            if critical_violations or high_violations:
                return EnforcementMode.BLOCKING, False
            else:
                return EnforcementMode.ADVISORY, True
        elif policy.enforcement_mode == EnforcementMode.WARNING:
            if critical_violations or copilot_critical:
                return EnforcementMode.WARNING, True
            else:
                return EnforcementMode.ADVISORY, True
        else:  # ADVISORY
            return EnforcementMode.ADVISORY, True
    
    def apply_rule_pack(
        self,
        violations: List[Violation],
        pack_name: str,
        file_path: str = "",
        content: str = ""
    ) -> List[Violation]:
        """Apply additional rules from a rule pack"""
        if pack_name not in self.rule_packs:
            logger.warning(f"Rule pack not found: {pack_name}")
            return violations
        
        pack = self.rule_packs[pack_name]
        additional_violations = []
        
        # Apply custom rules from pack
        custom_rules = pack.get("rules", [])
        if not custom_rules:
            return violations
        
        lines = content.split('\n') if content else []
        
        for rule in custom_rules:
            try:
                rule_id = rule.get("id", "")
                rule_name = rule.get("name", "")
                pattern_str = rule.get("pattern", "")
                category_str = rule.get("category", "compliance")
                severity_str = rule.get("severity", "medium")
                explanation = rule.get("explanation", "")
                standard_mappings = rule.get("standard_mappings", [])
                
                if not pattern_str:
                    continue
                
                # Compile pattern
                import re
                pattern = re.compile(pattern_str, re.MULTILINE | re.IGNORECASE)
                
                # Search for matches
                for line_num, line in enumerate(lines, 1):
                    if pattern.search(line):
                        # Check if violation already exists (avoid duplicates)
                        existing = any(
                            v.rule_id == rule_id and v.line_number == line_num
                            for v in violations + additional_violations
                        )
                        if existing:
                            continue
                        
                        from models.schemas import ViolationCategory, Severity
                        try:
                            category = ViolationCategory(category_str)
                        except:
                            category = ViolationCategory.COMPLIANCE
                        
                        try:
                            severity = Severity(severity_str)
                        except:
                            severity = Severity.MEDIUM
                        
                        additional_violations.append(Violation(
                            rule_id=rule_id,
                            rule_name=rule_name,
                            category=category,
                            severity=severity,
                            file_path=file_path,
                            line_number=line_num,
                            message=f"{rule_name} detected",
                            explanation=explanation or f"Violation of {rule_name} rule from {pack_name} rule pack",
                            fix_suggestion=f"Review and fix {rule_name} violation according to {pack_name} compliance requirements",
                            standard_mappings=standard_mappings,
                            code_snippet=line.strip(),
                            is_copilot_generated=False
                        ))
            except Exception as e:
                logger.warning(f"Failed to apply rule {rule.get('id', 'unknown')} from pack {pack_name}: {e}")
                continue
        
        logger.info(f"Applied rule pack {pack_name}: found {len(additional_violations)} additional violations")
        return violations + additional_violations
