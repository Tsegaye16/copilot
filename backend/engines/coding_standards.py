"""
Enterprise Coding Standards Engine
Enforces organization-defined coding standards including:
- Naming conventions
- Logging requirements
- Error handling patterns
"""
import re
import logging
from typing import List, Dict, Any, Optional
try:
    from models.schemas import Violation, ViolationCategory, Severity
except ImportError:
    from ..models.schemas import Violation, ViolationCategory, Severity

logger = logging.getLogger(__name__)


class CodingStandardsEngine:
    """Enterprise coding standards enforcement engine"""
    
    def __init__(self):
        # Naming convention patterns
        self.naming_patterns = {
            'function': r'^[a-z_][a-z0-9_]*$',  # snake_case for functions
            'class': r'^[A-Z][a-zA-Z0-9]*$',     # PascalCase for classes
            'constant': r'^[A-Z][A-Z0-9_]*$',     # UPPER_SNAKE_CASE for constants
            'variable': r'^[a-z_][a-z0-9_]*$'     # snake_case for variables
        }
        
        # Logging requirement patterns
        self.logging_patterns = [
            {
                'pattern': r'def\s+\w+.*:\s*\n\s*(?!.*(logger|log|logging))',
                'rule_id': 'STD001',
                'rule_name': 'Missing Logging in Function',
                'severity': Severity.MEDIUM,
                'explanation': 'Functions should include logging for debugging and monitoring'
            },
            {
                'pattern': r'(raise|except).*:\s*\n\s*(?!.*(logger|log|logging))',
                'rule_id': 'STD002',
                'rule_name': 'Missing Error Logging',
                'severity': Severity.HIGH,
                'explanation': 'Error handling should include logging for troubleshooting'
            }
        ]
        
        # Error handling patterns
        self.error_handling_patterns = [
            {
                'pattern': r'except\s*:\s*$',
                'rule_id': 'STD003',
                'rule_name': 'Bare Except Clause',
                'severity': Severity.HIGH,
                'explanation': 'Bare except clauses catch all exceptions including system exits'
            },
            {
                'pattern': r'except\s+Exception\s*:\s*\n\s*pass',
                'rule_id': 'STD004',
                'rule_name': 'Silent Exception Handling',
                'severity': Severity.MEDIUM,
                'explanation': 'Silently catching exceptions hides errors and makes debugging difficult'
            }
        ]
    
    def analyze_file(
        self,
        file_path: str,
        content: str,
        is_copilot: bool = False,
        custom_standards: Optional[Dict[str, Any]] = None
    ) -> List[Violation]:
        """Analyze file for coding standards violations"""
        violations = []
        lines = content.split('\n')
        
        # Apply custom standards if provided
        if custom_standards:
            violations.extend(self._check_custom_standards(file_path, lines, custom_standards))
        
        # Check naming conventions
        violations.extend(self._check_naming_conventions(file_path, lines, is_copilot))
        
        # Check logging requirements
        violations.extend(self._check_logging_requirements(file_path, lines, is_copilot))
        
        # Check error handling patterns
        violations.extend(self._check_error_handling(file_path, lines, is_copilot))
        
        return violations
    
    def _check_naming_conventions(
        self,
        file_path: str,
        lines: List[str],
        is_copilot: bool
    ) -> List[Violation]:
        """Check naming convention compliance"""
        violations = []
        
        for line_num, line in enumerate(lines, 1):
            # Check function definitions
            func_match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if func_match:
                func_name = func_match.group(1)
                if not re.match(self.naming_patterns['function'], func_name):
                    violations.append(Violation(
                        rule_id='STD005',
                        rule_name='Function Naming Convention Violation',
                        category=ViolationCategory.STANDARD,
                        severity=Severity.LOW,
                        file_path=file_path,
                        line_number=line_num,
                        message=f"Function '{func_name}' does not follow snake_case convention",
                        explanation=f"Functions should use snake_case naming (e.g., 'get_user_data' not '{func_name}')",
                        fix_suggestion=f"Rename function to follow snake_case: '{self._to_snake_case(func_name)}'",
                        is_copilot_generated=is_copilot,
                        code_snippet=line.strip()
                    ))
            
            # Check class definitions
            class_match = re.search(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if class_match:
                class_name = class_match.group(1)
                if not re.match(self.naming_patterns['class'], class_name):
                    violations.append(Violation(
                        rule_id='STD006',
                        rule_name='Class Naming Convention Violation',
                        category=ViolationCategory.STANDARD,
                        severity=Severity.LOW,
                        file_path=file_path,
                        line_number=line_num,
                        message=f"Class '{class_name}' does not follow PascalCase convention",
                        explanation=f"Classes should use PascalCase naming (e.g., 'UserService' not '{class_name}')",
                        fix_suggestion=f"Rename class to follow PascalCase: '{self._to_pascal_case(class_name)}'",
                        is_copilot_generated=is_copilot,
                        code_snippet=line.strip()
                    ))
            
            # Check constants
            const_match = re.search(r'^([A-Z_][A-Z0-9_]*)\s*=', line)
            if const_match:
                const_name = const_match.group(1)
                if not re.match(self.naming_patterns['constant'], const_name):
                    violations.append(Violation(
                        rule_id='STD007',
                        rule_name='Constant Naming Convention Violation',
                        category=ViolationCategory.STANDARD,
                        severity=Severity.LOW,
                        file_path=file_path,
                        line_number=line_num,
                        message=f"Constant '{const_name}' does not follow UPPER_SNAKE_CASE convention",
                        explanation=f"Constants should use UPPER_SNAKE_CASE naming (e.g., 'MAX_RETRIES' not '{const_name}')",
                        fix_suggestion=f"Rename constant to follow UPPER_SNAKE_CASE: '{const_name.upper()}'",
                        is_copilot_generated=is_copilot,
                        code_snippet=line.strip()
                    ))
        
        return violations
    
    def _check_logging_requirements(
        self,
        file_path: str,
        lines: List[str],
        is_copilot: bool
    ) -> List[Violation]:
        """Check logging requirements"""
        violations = []
        
        for pattern_config in self.logging_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern_config['pattern'], line, re.MULTILINE):
                    # Check if logging exists in nearby lines
                    context_start = max(0, line_num - 3)
                    context_end = min(len(lines), line_num + 3)
                    context = '\n'.join(lines[context_start:context_end])
                    
                    if 'logger' not in context.lower() and 'log' not in context.lower():
                        violations.append(Violation(
                            rule_id=pattern_config['rule_id'],
                            rule_name=pattern_config['rule_name'],
                            category=ViolationCategory.STANDARD,
                            severity=pattern_config['severity'],
                            file_path=file_path,
                            line_number=line_num,
                            message=pattern_config['rule_name'],
                            explanation=pattern_config['explanation'],
                            fix_suggestion="Add appropriate logging: logger.info('Operation started') or logger.error('Operation failed', exc_info=True)",
                            is_copilot_generated=is_copilot,
                            code_snippet=line.strip()
                        ))
        
        return violations
    
    def _check_error_handling(
        self,
        file_path: str,
        lines: List[str],
        is_copilot: bool
    ) -> List[Violation]:
        """Check error handling patterns"""
        violations = []
        
        for pattern_config in self.error_handling_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern_config['pattern'], line):
                    violations.append(Violation(
                        rule_id=pattern_config['rule_id'],
                        rule_name=pattern_config['rule_name'],
                        category=ViolationCategory.CODE_QUALITY,
                        severity=pattern_config['severity'],
                        file_path=file_path,
                        line_number=line_num,
                        message=pattern_config['rule_name'],
                        explanation=pattern_config['explanation'],
                        fix_suggestion="Use specific exception types: except ValueError as e: logger.error('Error occurred', exc_info=True)",
                        is_copilot_generated=is_copilot,
                        code_snippet=line.strip()
                    ))
        
        return violations
    
    def _check_custom_standards(
        self,
        file_path: str,
        lines: List[str],
        custom_standards: Dict[str, Any]
    ) -> List[Violation]:
        """Check custom coding standards"""
        violations = []
        
        # Custom naming conventions
        if 'naming_conventions' in custom_standards:
            # Implementation for custom naming rules
            pass
        
        # Custom logging requirements
        if 'logging_requirements' in custom_standards:
            # Implementation for custom logging rules
            pass
        
        return violations
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case"""
        # Simple conversion - in production, use a proper library
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase"""
        parts = name.split('_')
        return ''.join(word.capitalize() for word in parts)
