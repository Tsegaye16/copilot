"""
AI-powered code analysis using Google Gemini API
"""
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional
try:
    from models.schemas import Violation, ViolationCategory, Severity
    from core.config import settings
except ImportError:
    from ..models.schemas import Violation, ViolationCategory, Severity
    from ..core.config import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered code analysis engine using Gemini"""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured. AI analysis will be disabled.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
            logger.info("Gemini AI analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.enabled = False
    
    async def analyze_code(
        self,
        file_path: str,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        is_copilot: bool = False
    ) -> List[Violation]:
        """Analyze code using AI for contextual understanding"""
        if not self.enabled:
            return []
        
        try:
            prompt = self._build_analysis_prompt(file_path, content, context, is_copilot)
            response = await self._call_gemini(prompt)
            violations = self._parse_ai_response(response, file_path, is_copilot)
            return violations
        except Exception as e:
            logger.error(f"AI analysis failed for {file_path}: {e}")
            return []
    
    def _build_analysis_prompt(
        self,
        file_path: str,
        content: str,
        context: Optional[Dict[str, Any]],
        is_copilot: bool
    ) -> str:
        """Build the prompt for AI analysis"""
        copilot_note = "NOTE: This code is suspected to be AI-generated (GitHub Copilot). Apply stricter security standards." if is_copilot else ""
        
        prompt = f"""You are an expert security code reviewer analyzing code for enterprise production systems.

{copilot_note}

File: {file_path}

Code to analyze:
```python
{content}
```

Analyze this code for:
1. Security vulnerabilities (OWASP Top 10, CWE)
2. Performance issues
3. Maintainability concerns
4. Best practice violations
5. Potential bugs or logic errors

For each issue found, provide:
- rule_id: A unique identifier (e.g., "AI001")
- rule_name: Short descriptive name
- category: security, compliance, code_quality, or standard
- severity: low, medium, high, or critical
- line_number: Line number (1-indexed)
- message: Brief issue description
- explanation: Detailed explanation of why this is a problem
- fix_suggestion: Specific code fix or improvement suggestion
- standard_mappings: OWASP/CWE mappings if applicable (comma-separated)

Format your response as JSON array of violations:
[
  {{
    "rule_id": "AI001",
    "rule_name": "Missing Input Validation",
    "category": "security",
    "severity": "high",
    "line_number": 15,
    "message": "User input not validated",
    "explanation": "The function accepts user input without validation...",
    "fix_suggestion": "Add input validation: if not isinstance(value, str): raise ValueError(...)",
    "standard_mappings": ["CWE-20", "OWASP-A03:2021"]
  }}
]

If no issues found, return empty array [].
"""
        return prompt
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""
        try:
            # Note: Gemini SDK may not be fully async, but we wrap it for consistency
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _parse_ai_response(
        self,
        response: str,
        file_path: str,
        is_copilot: bool
    ) -> List[Violation]:
        """Parse AI response into Violation objects"""
        import json
        import re
        
        violations = []
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                ai_violations = json.loads(json_str)
                
                for v in ai_violations:
                    try:
                        violation = Violation(
                            rule_id=v.get("rule_id", "AI000"),
                            rule_name=v.get("rule_name", "AI Detected Issue"),
                            category=ViolationCategory(v.get("category", "code_quality")),
                            severity=Severity(v.get("severity", "medium")),
                            file_path=file_path,
                            line_number=int(v.get("line_number", 1)),
                            message=v.get("message", ""),
                            explanation=v.get("explanation", ""),
                            fix_suggestion=v.get("fix_suggestion"),
                            standard_mappings=v.get("standard_mappings", []),
                            is_copilot_generated=is_copilot,
                            ai_confidence=0.85  # Default confidence for AI-detected issues
                        )
                        violations.append(violation)
                    except Exception as e:
                        logger.warning(f"Failed to parse AI violation: {e}")
                        continue
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
        
        return violations
    
    async def detect_copilot_code(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Detect if code was generated by Copilot"""
        if not self.enabled:
            return False
        
        try:
            prompt = f"""Analyze this code and determine if it was likely generated by GitHub Copilot or similar AI coding assistant.

Consider:
- Code style patterns typical of AI generation
- Comment style
- Variable naming patterns
- Code structure

Code:
```python
{content[:2000]}  # Limit to first 2000 chars
```

Respond with only "true" or "false"."""
            
            response = await self._call_gemini(prompt)
            return "true" in response.lower()
        except Exception as e:
            logger.error(f"Copilot detection failed: {e}")
            return False
    
    async def suggest_fix(self, violation: Violation, code_context: str) -> Optional[str]:
        """Get AI-suggested fix for a violation"""
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Provide a specific code fix for this security issue:

Issue: {violation.message}
Explanation: {violation.explanation}
File: {violation.file_path}
Line: {violation.line_number}

Code context:
```python
{code_context}
```

Provide only the fixed code snippet, not explanations."""
            
            response = await self._call_gemini(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Fix suggestion failed: {e}")
            return None
