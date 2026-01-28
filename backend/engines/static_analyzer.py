"""
Static analysis engine for security and compliance patterns
"""
import re
import logging
from typing import List, Dict, Any, Optional
try:
    from models.schemas import Violation, ViolationCategory, Severity
except ImportError:
    from ..models.schemas import Violation, ViolationCategory, Severity

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """Static code analysis engine"""
    
    def __init__(self):
        self.secret_patterns = self._load_secret_patterns()
        self.sql_injection_patterns = self._load_sql_injection_patterns()
        self.unsafe_patterns = self._load_unsafe_patterns()
    
    def _load_secret_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for detecting hardcoded secrets"""
        return [
            {
                "pattern": r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([^"\']{20,})["\']',
                "rule_id": "SEC001",
                "rule_name": "Hardcoded API Key",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798", "OWASP-A07:2021"]
            },
            {
                "pattern": r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']+)["\']',
                "rule_id": "SEC002",
                "rule_name": "Hardcoded Password",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798", "OWASP-A07:2021"]
            },
            {
                "pattern": r'(?i)(secret|secret[_-]?key)\s*[=:]\s*["\']([^"\']{20,})["\']',
                "rule_id": "SEC003",
                "rule_name": "Hardcoded Secret",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798", "OWASP-A07:2021"]
            },
            {
                "pattern": r'(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*["\']([^"\']+)["\']',
                "rule_id": "SEC004",
                "rule_name": "Hardcoded AWS Credentials",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798", "OWASP-A07:2021"]
            },
            {
                "pattern": r'sk_live_[0-9a-zA-Z]{24,}',
                "rule_id": "SEC005",
                "rule_name": "Stripe Live Secret Key",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798"]
            },
            {
                "pattern": r'(?i)(token|bearer[_-]?token)\s*[=:]\s*["\']([^"\']{20,})["\']',
                "rule_id": "SEC006",
                "rule_name": "Hardcoded Token",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798", "OWASP-A07:2021"]
            },
            {
                "pattern": r'(?i)(private[_-]?key|privatekey)\s*[=:]\s*["\']([^"\']{20,})["\']',
                "rule_id": "SEC007",
                "rule_name": "Hardcoded Private Key",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798", "OWASP-A07:2021"]
            },
            {
                "pattern": r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
                "rule_id": "SEC008",
                "rule_name": "Hardcoded Private Key (PEM Format)",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798", "OWASP-A07:2021"]
            },
            {
                "pattern": r'(?i)(database[_-]?url|db[_-]?password|connection[_-]?string)\s*[=:]\s*["\']([^"\']*://[^"\']+)["\']',
                "rule_id": "SEC009",
                "rule_name": "Hardcoded Database Credentials",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-798", "OWASP-A07:2021"]
            }
        ]
    
    def _load_sql_injection_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for detecting SQL injection risks"""
        return [
            {
                "pattern": r'(?i)(execute|query|exec)\s*\([^)]*\+.*["\']',
                "rule_id": "SEC101",
                "rule_name": "Potential SQL Injection (String Concatenation)",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.HIGH,
                "standard_mappings": ["CWE-89", "OWASP-A03:2021"]
            },
            {
                "pattern": r'(?i)(execute|query|exec)\s*\([^)]*f["\']',
                "rule_id": "SEC102",
                "rule_name": "Potential SQL Injection (F-string)",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.HIGH,
                "standard_mappings": ["CWE-89", "OWASP-A03:2021"]
            },
            {
                "pattern": r'(?i)(execute|query|exec)\s*\([^)]*\.format\(',
                "rule_id": "SEC103",
                "rule_name": "Potential SQL Injection (String Format)",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.HIGH,
                "standard_mappings": ["CWE-89", "OWASP-A03:2021"]
            }
        ]
    
    def _load_unsafe_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for detecting unsafe operations"""
        return [
            {
                "pattern": r'eval\s*\(',
                "rule_id": "SEC201",
                "rule_name": "Use of eval()",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-95", "OWASP-A03:2021"]
            },
            {
                "pattern": r'exec\s*\(',
                "rule_id": "SEC202",
                "rule_name": "Use of exec()",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.CRITICAL,
                "standard_mappings": ["CWE-95", "OWASP-A03:2021"]
            },
            {
                "pattern": r'(?i)subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True',
                "rule_id": "SEC203",
                "rule_name": "Unsafe Shell Execution",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.HIGH,
                "standard_mappings": ["CWE-78", "OWASP-A03:2021"]
            },
            {
                "pattern": r'(?i)pickle\.(loads?|dumps?)\s*\(',
                "rule_id": "SEC204",
                "rule_name": "Unsafe Deserialization",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.HIGH,
                "standard_mappings": ["CWE-502", "OWASP-A08:2021"]
            },
            {
                "pattern": r'(?i)open\s*\([^)]*\.\./',
                "rule_id": "SEC205",
                "rule_name": "Path Traversal Risk",
                "category": ViolationCategory.SECURITY,
                "severity": Severity.HIGH,
                "standard_mappings": ["CWE-22", "OWASP-A01:2021"]
            }
        ]
    
    def analyze_file(self, file_path: str, content: str, is_copilot: bool = False) -> List[Violation]:
        """Analyze a single file for violations"""
        violations = []
        lines = content.split('\n')
        
        # Check for secrets
        violations.extend(self._check_secrets(file_path, lines, is_copilot))
        
        # Check for SQL injection
        violations.extend(self._check_sql_injection(file_path, lines, is_copilot))
        
        # Check for unsafe patterns
        violations.extend(self._check_unsafe_patterns(file_path, lines, is_copilot))
        
        return violations
    
    def _check_secrets(self, file_path: str, lines: List[str], is_copilot: bool) -> List[Violation]:
        """Check for hardcoded secrets"""
        violations = []
        for line_num, line in enumerate(lines, 1):
            for pattern_config in self.secret_patterns:
                matches = re.finditer(pattern_config["pattern"], line)
                for match in matches:
                    violation = Violation(
                        rule_id=pattern_config["rule_id"],
                        rule_name=pattern_config["rule_name"],
                        category=pattern_config["category"],
                        severity=pattern_config["severity"],
                        file_path=file_path,
                        line_number=line_num,
                        column_number=match.start() + 1,
                        message=f"Hardcoded secret detected: {pattern_config['rule_name']}",
                        explanation=f"This code contains a hardcoded secret which is a critical security risk. "
                                   f"Secrets should be stored in environment variables or secret management systems. "
                                   f"{'This appears to be AI-generated code, which may have introduced this vulnerability.' if is_copilot else ''}",
                        fix_suggestion="Use environment variables or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault)",
                        standard_mappings=pattern_config["standard_mappings"],
                        code_snippet=line.strip(),
                        is_copilot_generated=is_copilot
                    )
                    violations.append(violation)
        return violations
    
    def _check_sql_injection(self, file_path: str, lines: List[str], is_copilot: bool) -> List[Violation]:
        """Check for SQL injection patterns"""
        violations = []
        for line_num, line in enumerate(lines, 1):
            for pattern_config in self.sql_injection_patterns:
                if re.search(pattern_config["pattern"], line):
                    violation = Violation(
                        rule_id=pattern_config["rule_id"],
                        rule_name=pattern_config["rule_name"],
                        category=pattern_config["category"],
                        severity=pattern_config["severity"],
                        file_path=file_path,
                        line_number=line_num,
                        message="Potential SQL injection vulnerability detected",
                        explanation=f"SQL queries constructed using string concatenation or formatting are vulnerable to SQL injection attacks. "
                                   f"Use parameterized queries or ORM methods instead. "
                                   f"{'This AI-generated code may not have considered security best practices.' if is_copilot else ''}",
                        fix_suggestion="Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                        standard_mappings=pattern_config["standard_mappings"],
                        code_snippet=line.strip(),
                        is_copilot_generated=is_copilot
                    )
                    violations.append(violation)
        return violations
    
    def _check_unsafe_patterns(self, file_path: str, lines: List[str], is_copilot: bool) -> List[Violation]:
        """Check for unsafe execution patterns"""
        violations = []
        for line_num, line in enumerate(lines, 1):
            for pattern_config in self.unsafe_patterns:
                if re.search(pattern_config["pattern"], line):
                    violation = Violation(
                        rule_id=pattern_config["rule_id"],
                        rule_name=pattern_config["rule_name"],
                        category=pattern_config["category"],
                        severity=pattern_config["severity"],
                        file_path=file_path,
                        line_number=line_num,
                        message=f"Unsafe operation detected: {pattern_config['rule_name']}",
                        explanation=f"The use of {pattern_config['rule_name'].lower()} can lead to code injection vulnerabilities. "
                                   f"Only use when absolutely necessary and with proper input validation. "
                                   f"{'AI-generated code may not have considered the security implications.' if is_copilot else ''}",
                        fix_suggestion="Use safer alternatives or implement strict input validation and sandboxing",
                        standard_mappings=pattern_config["standard_mappings"],
                        code_snippet=line.strip(),
                        is_copilot_generated=is_copilot
                    )
                    violations.append(violation)
        return violations
