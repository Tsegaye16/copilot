"""
AI-powered code analysis using Google Gemini API
Enhanced for security, performance, and maintainability analysis
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
    """AI-powered code analysis engine using Gemini for comprehensive code review"""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured. AI analysis will be disabled.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use gemini-2.5-flash (works with free tier), fallback to other models
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("Using Gemini 2.5 Flash")
            except Exception as e1:
                logger.warning(f"Failed to load gemini-2.5-flash: {e1}, trying gemini-flash")
                try:
                    self.model = genai.GenerativeModel('gemini-flash')
                    logger.info("Using Gemini Flash")
                except Exception as e2:
                    logger.warning(f"Failed to load gemini-flash: {e2}, trying gemini-1.5-flash")
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    logger.info("Using Gemini 1.5 Flash")
            self.enabled = True
            self.quota_exceeded = False  # Track quota status
            self.quota_exceeded_time = None  # Track when quota was exceeded
            logger.info("Gemini AI analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.enabled = False
            self.quota_exceeded = False
            self.quota_exceeded_time = None
    
    async def analyze_code(
        self,
        file_path: str,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        is_copilot: bool = False
    ) -> List[Violation]:
        """Analyze code using AI for contextual understanding"""
        # Check if quota was exceeded and enough time has passed (1 hour)
        if self.quota_exceeded and self.quota_exceeded_time:
            import time
            if time.time() - self.quota_exceeded_time > 3600:  # 1 hour
                logger.info("Resetting quota_exceeded flag after 1 hour")
                self.quota_exceeded = False
                self.quota_exceeded_time = None
        
        if not self.enabled or self.quota_exceeded:
            if self.quota_exceeded:
                logger.debug("AI analysis skipped due to quota exceeded")
            return []
        
        try:
            prompt = self._build_analysis_prompt(file_path, content, context, is_copilot)
            response = await self._call_gemini(prompt)
            violations = self._parse_ai_response(response, file_path, is_copilot)
            return violations
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower() or "exceeded" in error_str.lower():
                logger.warning(f"AI analysis skipped for {file_path} due to quota limits")
                import time
                self.quota_exceeded = True
                self.quota_exceeded_time = time.time()
            else:
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
        
        prompt = f"""You are an expert enterprise code reviewer analyzing code for production systems. Your analysis must be thorough, covering security, performance, maintainability, and compliance.

{copilot_note}

File: {file_path}
Context: {context or "No additional context"}

Code to analyze:
```python
{content[:8000]}  # Limit to 8000 chars for API limits
```

**COMPREHENSIVE ANALYSIS REQUIRED:**

1. **SECURITY VULNERABILITIES** (OWASP Top 10, CWE):
   - Hardcoded secrets, credentials, API keys
   - SQL/NoSQL injection risks
   - XSS, CSRF vulnerabilities
   - Insecure deserialization
   - Unsafe file/command execution
   - Authentication/authorization flaws
   - Cryptographic weaknesses
   - Insecure dependencies

2. **PERFORMANCE ISSUES**:
   - Inefficient algorithms (O(n²) when O(n) possible)
   - Memory leaks or excessive memory usage
   - Blocking I/O operations
   - N+1 query problems
   - Unnecessary database calls
   - Missing caching opportunities
   - Inefficient data structures

3. **MAINTAINABILITY CONCERNS**:
   - Code duplication
   - Complex functions (high cyclomatic complexity)
   - Poor error handling
   - Missing logging
   - Inconsistent naming conventions
   - Magic numbers/strings
   - Tight coupling
   - Missing documentation

4. **BEST PRACTICES & STANDARDS**:
   - PEP 8 compliance (Python)
   - SOLID principles violations
   - Design pattern misuse
   - Resource management (file handles, connections)
   - Exception handling patterns
   - Type safety issues

5. **COMPLIANCE & IP RISKS**:
   - License compatibility issues
   - Potential IP violations
   - Data privacy concerns (GDPR, etc.)
   - Regulatory compliance gaps

**OUTPUT FORMAT (JSON array):**
[
  {{
    "rule_id": "AI001",
    "rule_name": "Missing Input Validation",
    "category": "security",
    "severity": "high",
    "line_number": 15,
    "message": "User input not validated before processing",
    "explanation": "The function accepts user input without validation, which can lead to injection attacks, data corruption, or system compromise. Input validation is a critical security control.",
    "fix_suggestion": "Add input validation: if not isinstance(value, str) or len(value) > MAX_LENGTH: raise ValueError('Invalid input')",
    "standard_mappings": ["CWE-20", "OWASP-A03:2021"]
  }}
]

**SEVERITY GUIDELINES:**
- critical: Immediate security risk, data breach potential, system compromise
- high: Significant security issue, performance bottleneck, major maintainability problem
- medium: Security concern, performance issue, maintainability problem
- low: Code quality issue, minor optimization opportunity

**CATEGORIES:**
- security: Security vulnerabilities
- compliance: Compliance/regulatory issues
- code_quality: Code quality and maintainability
- license: License/IP issues
- ip_risk: Intellectual property risks
- standard: Coding standards violations

Return ONLY valid JSON array. If no issues found, return [].
"""
        return prompt
    
    async def _call_gemini(self, prompt: str, max_retries: int = 3) -> str:
        """Call Gemini API with retry logic for quota errors"""
        import asyncio
        import time
        
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(prompt)
                )
                # Reset quota_exceeded flag on success
                self.quota_exceeded = False
                return response.text
            except Exception as e:
                error_str = str(e)
                
                # Check for quota exceeded (429 error)
                if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                    self.quota_exceeded = True
                    
                    # Extract retry delay from error if available
                    retry_delay = 60  # Default 60 seconds
                    if "retry in" in error_str.lower() or "retry_delay" in error_str.lower():
                        import re
                        delay_match = re.search(r'retry.*?(\d+(?:\.\d+)?)', error_str, re.IGNORECASE)
                        if delay_match:
                            retry_delay = float(delay_match.group(1))
                            retry_delay = min(retry_delay + 5, 300)  # Cap at 5 minutes
                    
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Gemini API quota exceeded (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {retry_delay:.1f} seconds..."
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.error(
                            f"Gemini API quota exceeded after {max_retries} attempts. "
                            f"AI features will be temporarily disabled. Error: {error_str[:200]}"
                        )
                        # Track when quota was exceeded (will auto-reset after 1 hour)
                        import time
                        self.quota_exceeded_time = time.time()
                        # Don't disable completely, just mark as exceeded
                        # This allows the system to continue with static analysis
                        raise Exception(f"Quota exceeded: {error_str[:200]}")
                else:
                    # Other errors - log and raise
                    logger.error(f"Gemini API call failed: {e}")
                    if attempt < max_retries - 1:
                        # Exponential backoff for other errors
                        wait_time = 2 ** attempt
                        logger.warning(f"Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
        
        raise Exception("Max retries exceeded")
    
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
        # Check if quota was exceeded and enough time has passed (1 hour)
        if self.quota_exceeded and self.quota_exceeded_time:
            import time
            if time.time() - self.quota_exceeded_time > 3600:  # 1 hour
                logger.info("Resetting quota_exceeded flag after 1 hour")
                self.quota_exceeded = False
                self.quota_exceeded_time = None
        
        if not self.enabled or self.quota_exceeded:
            if self.quota_exceeded:
                logger.debug("AI fix suggestion skipped due to quota exceeded")
            return None
        
        try:
            # Build a more detailed prompt for better code suggestions
            prompt = f"""You are a security expert providing code fixes for security vulnerabilities.

**Security Issue:**
Rule ID: {violation.rule_id}
Rule Name: {violation.rule_name}
Severity: {violation.severity.value.upper()}
Category: {violation.category.value}

**Issue Description:**
{violation.message}

**Explanation:**
{violation.explanation}

**Vulnerable Code (Line {violation.line_number}):**
```python
{code_context}
```

**Your Task:**
Provide a CONCISE, ACTIONABLE code fix (maximum 30 lines) that:
1. Shows the exact code change needed
2. Includes a complete, working code example
3. Uses security best practices
4. Is production-ready

**Requirements:**
- Keep it SHORT and FOCUSED (max 30 lines)
- Show ONLY the fixed function/method, not entire file
- Include necessary imports
- Add brief inline comments for clarity
- Skip lengthy explanations - focus on the code fix

**Example Format (concise):**
```python
import os

API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
```

**Important:** Be concise! Developers need quick, actionable fixes, not lengthy tutorials.

Now provide the fix for this specific issue:"""
            
            response = await self._call_gemini(prompt)
            
            # Clean up the response - extract code block if present
            import re
            code_match = re.search(r'```(?:python)?\s*\n(.*?)\n```', response, re.DOTALL)
            if code_match:
                code_snippet = code_match.group(1).strip()
                # Limit to 30 lines max for conciseness
                lines = code_snippet.split('\n')
                if len(lines) > 30:
                    # Take first 30 lines and add a note
                    truncated = '\n'.join(lines[:30])
                    code_snippet = truncated + '\n# ... (truncated for brevity)'
                return code_snippet
            
            # If no code block, return the response but clean it up
            cleaned = response.strip()
            # Remove common prefixes like "Here's the fix:" etc.
            prefixes = ["here's", "here is", "the fix", "solution:", "fixed code:"]
            for prefix in prefixes:
                if cleaned.lower().startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
                    if cleaned.startswith(':'):
                        cleaned = cleaned[1:].strip()
            
            # Limit text responses to 500 characters
            if len(cleaned) > 500:
                cleaned = cleaned[:500] + "..."
            
            return cleaned if len(cleaned) > 20 else None
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower() or "exceeded" in error_str.lower():
                logger.warning(f"AI fix suggestion skipped due to quota limits")
                import time
                self.quota_exceeded = True
                self.quota_exceeded_time = time.time()
            else:
                logger.error(f"Fix suggestion failed: {e}")
            return None
