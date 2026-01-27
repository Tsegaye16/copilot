"""
License and IP compliance checker
"""
import re
import logging
from typing import List, Dict, Any, Optional
from ..models.schemas import Violation, ViolationCategory, Severity

logger = logging.getLogger(__name__)


class LicenseChecker:
    """Check for license and IP compliance issues"""
    
    def __init__(self):
        self.restricted_licenses = [
            "GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0"
        ]
        self.license_patterns = {
            "MIT": r'MIT\s+License|The\s+MIT\s+License',
            "Apache": r'Apache\s+License|Apache-2\.0',
            "GPL": r'GPL|GNU\s+General\s+Public\s+License',
            "BSD": r'BSD\s+License|BSD-\d',
            "Proprietary": r'Proprietary|All\s+Rights\s+Reserved|Copyright',
        }
    
    def check_file(self, file_path: str, content: str) -> List[Violation]:
        """Check a file for license issues"""
        violations = []
        
        # Check for license headers
        license_header = self._extract_license_header(content)
        if license_header:
            violations.extend(self._check_license_compatibility(file_path, license_header))
        
        # Check for third-party imports without attribution
        violations.extend(self._check_imports(file_path, content))
        
        return violations
    
    def _extract_license_header(self, content: str) -> Optional[str]:
        """Extract license header from file"""
        # Check first 50 lines for license info
        lines = content.split('\n')[:50]
        header = '\n'.join(lines)
        
        for license_type, pattern in self.license_patterns.items():
            if re.search(pattern, header, re.IGNORECASE):
                return license_type
        
        return None
    
    def _check_license_compatibility(self, file_path: str, license_type: str) -> List[Violation]:
        """Check if license is compatible with enterprise policies"""
        violations = []
        
        if license_type in self.restricted_licenses:
            violation = Violation(
                rule_id="LIC001",
                rule_name="Restricted License Detected",
                category=ViolationCategory.LICENSE,
                severity=Severity.HIGH,
                file_path=file_path,
                line_number=1,
                message=f"File contains {license_type} license which may be incompatible with enterprise policies",
                explanation=f"The {license_type} license has copyleft requirements that may conflict with proprietary software policies. "
                           f"Review with legal team before including in production code.",
                fix_suggestion="Consider using MIT, Apache-2.0, or BSD licenses, or obtain legal approval",
                standard_mappings=[]
            )
            violations.append(violation)
        
        return violations
    
    def _check_imports(self, file_path: str, content: str) -> List[Violation]:
        """Check for third-party imports that may need attribution"""
        violations = []
        
        # Common third-party libraries that require attribution
        third_party_libs = [
            "requests", "numpy", "pandas", "django", "flask", "tensorflow", "pytorch"
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for lib in third_party_libs:
                if re.search(rf'^import\s+{lib}|^from\s+{lib}', line):
                    # Check if there's attribution in the file
                    if not self._has_attribution(content, lib):
                        violation = Violation(
                            rule_id="LIC002",
                            rule_name="Missing Third-Party Attribution",
                            category=ViolationCategory.LICENSE,
                            severity=Severity.MEDIUM,
                            file_path=file_path,
                            line_number=line_num,
                            message=f"Third-party library '{lib}' used without attribution",
                            explanation=f"The library '{lib}' is used but not properly attributed. "
                                       f"Some licenses require attribution in documentation or source code.",
                            fix_suggestion=f"Add attribution for {lib} in LICENSE or README file",
                            standard_mappings=[]
                        )
                        violations.append(violation)
        
        return violations
    
    def _has_attribution(self, content: str, library: str) -> bool:
        """Check if library has attribution in content"""
        content_lower = content.lower()
        library_lower = library.lower()
        
        # Check for common attribution patterns
        attribution_patterns = [
            rf'{library_lower}',
            rf'attribution.*{library_lower}',
            rf'uses.*{library_lower}',
        ]
        
        for pattern in attribution_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    def check_duplicate_code(self, file_path: str, content: str, codebase_fingerprints: Dict[str, str]) -> List[Violation]:
        """Check for duplicate or near-duplicate code (IP risk)"""
        violations = []
        
        # Simple hash-based duplicate detection
        # In production, use more sophisticated algorithms like AST comparison
        content_hash = hash(content.strip())
        
        for other_file, other_hash in codebase_fingerprints.items():
            if other_file != file_path and content_hash == other_hash:
                violation = Violation(
                    rule_id="IP001",
                    rule_name="Duplicate Code Detected",
                    category=ViolationCategory.IP_RISK,
                    severity=Severity.LOW,
                    file_path=file_path,
                    line_number=1,
                    message=f"Code appears to be duplicate of {other_file}",
                    explanation="Duplicate code may indicate copied code from external sources. "
                               "Review to ensure proper licensing and attribution.",
                    fix_suggestion="Refactor to shared utility if appropriate, or ensure proper attribution",
                    standard_mappings=[]
                )
                violations.append(violation)
                break
        
        return violations
