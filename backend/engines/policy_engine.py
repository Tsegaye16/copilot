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
                if critical_violations or copilot_critical:
                    return EnforcementMode.WARNING, True
                else:
                    return EnforcementMode.ADVISORY, True
            
            # Stricter blocking for Copilot-generated critical violations
            if copilot_critical:
                return EnforcementMode.BLOCKING, False
            
            # Block on critical violations or multiple high violations
            if critical_violations or (high_violations and len(high_violations) > 3):
                return EnforcementMode.BLOCKING, False
            elif high_violations:
                return EnforcementMode.WARNING, True
            else:
                return EnforcementMode.ADVISORY, True
        elif policy.enforcement_mode == EnforcementMode.WARNING:
            if critical_violations or copilot_critical:
                return EnforcementMode.WARNING, True
            else:
                return EnforcementMode.ADVISORY, True
        else:  # ADVISORY
            return EnforcementMode.ADVISORY, True
    
    def apply_rule_pack(self, violations: List[Violation], pack_name: str) -> List[Violation]:
        """Apply additional rules from a rule pack"""
        if pack_name not in self.rule_packs:
            logger.warning(f"Rule pack not found: {pack_name}")
            return violations
        
        pack = self.rule_packs[pack_name]
        additional_violations = []
        
        # Apply custom rules from pack
        custom_rules = pack.get("rules", [])
        for rule in custom_rules:
            # Rule application logic would go here
            # This is a placeholder for rule pack rule execution
            pass
        
        return violations + additional_violations
