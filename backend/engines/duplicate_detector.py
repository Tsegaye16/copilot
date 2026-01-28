"""
Near-duplicate code detection engine
Detects copied or near-duplicate code patterns
"""
import hashlib
import logging
from typing import List, Dict, Any, Tuple, Set
try:
    from models.schemas import Violation, ViolationCategory, Severity
except ImportError:
    from ..models.schemas import Violation, ViolationCategory, Severity

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Detect near-duplicate code patterns"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.code_fingerprints: Dict[str, List[Tuple[str, str]]] = {}  # hash -> [(file_path, line_range)]
    
    def detect_duplicates(
        self,
        files: List[Dict[str, Any]],
        repository: str
    ) -> List[Violation]:
        """Detect duplicate code patterns across files"""
        violations = []
        
        # Generate fingerprints for each function/method
        fingerprints = []
        for file_data in files:
            file_path = file_data.get('path', '')
            content = file_data.get('content', '')
            
            if not content:
                continue
            
            # Extract functions/methods
            functions = self._extract_functions(file_path, content)
            for func_name, func_code, start_line, end_line in functions:
                fingerprint = self._generate_fingerprint(func_code)
                fingerprints.append({
                    'file': file_path,
                    'function': func_name,
                    'code': func_code,
                    'fingerprint': fingerprint,
                    'start_line': start_line,
                    'end_line': end_line
                })
        
        # Compare fingerprints
        for i, func1 in enumerate(fingerprints):
            for func2 in fingerprints[i+1:]:
                if func1['file'] == func2['file']:
                    continue  # Skip same file
                
                similarity = self._calculate_similarity(
                    func1['fingerprint'],
                    func2['fingerprint']
                )
                
                if similarity >= self.similarity_threshold:
                    violations.append(Violation(
                        rule_id='IP001',
                        rule_name='Near-Duplicate Code Detected',
                        category=ViolationCategory.IP_RISK,
                        severity=Severity.MEDIUM,
                        file_path=func1['file'],
                        line_number=func1['start_line'],
                        message=f"Code in '{func1['function']}' is similar to '{func2['function']}' in {func2['file']}",
                        explanation=f"Near-duplicate code detected ({similarity:.0%} similarity). This may indicate code copying, potential IP risks, or need for refactoring into shared utilities.",
                        fix_suggestion=f"Consider refactoring common code into a shared utility function or module to reduce duplication and potential IP risks.",
                        standard_mappings=['CWE-1049', 'CWE-1050'],
                        code_snippet=func1['code'][:200] + '...' if len(func1['code']) > 200 else func1['code'],
                        is_copilot_generated=False
                    ))
        
        return violations
    
    def _extract_functions(self, file_path: str, content: str) -> List[Tuple[str, str, int, int]]:
        """Extract function definitions from code"""
        import ast
        import re
        
        functions = []
        lines = content.split('\n')
        
        # Try AST parsing for Python files
        if file_path.endswith('.py'):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        start_line = node.lineno
                        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
                        func_code = '\n'.join(lines[start_line-1:end_line])
                        functions.append((node.name, func_code, start_line, end_line))
            except:
                # Fallback to regex if AST fails
                pass
        
        # Regex fallback for other languages or if AST fails
        if not functions:
            # Match function definitions
            pattern = r'(?:def|function|const|let|var)\s+(\w+)\s*[\(\[].*?\{'
            for match in re.finditer(pattern, content, re.MULTILINE):
                func_name = match.group(1)
                start_pos = match.start()
                start_line = content[:start_pos].count('\n') + 1
                # Try to find function end (simplified)
                end_line = min(start_line + 20, len(lines))
                func_code = '\n'.join(lines[start_line-1:end_line])
                functions.append((func_name, func_code, start_line, end_line))
        
        return functions
    
    def _generate_fingerprint(self, code: str) -> str:
        """Generate fingerprint for code block"""
        # Normalize code (remove whitespace, comments)
        normalized = self._normalize_code(code)
        # Generate hash
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison"""
        import re
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        # Remove variable names (keep structure)
        code = re.sub(r'\b[a-z_][a-z0-9_]*\b', 'VAR', code)
        return code.strip()
    
    def _calculate_similarity(self, fingerprint1: str, fingerprint2: str) -> float:
        """Calculate similarity between two fingerprints"""
        # Simple hash comparison - in production, use more sophisticated algorithms
        # like Levenshtein distance or token-based comparison
        if fingerprint1 == fingerprint2:
            return 1.0
        
        # Compare character-level similarity
        matches = sum(c1 == c2 for c1, c2 in zip(fingerprint1, fingerprint2))
        return matches / max(len(fingerprint1), len(fingerprint2))
