# Testing and Configuration Guide

This document provides comprehensive testing scenarios and configuration details. **This file can be removed after setup is complete.**

## 🧪 Testing Scenarios

### Level 1: Basic Tests (5 minutes)

#### 1.1 Health Check Tests

```bash
# Backend health check
curl https://guardrails-backend.onrender.com/health

# GitHub App health check
curl https://guardrails-github-app.onrender.com/health
```

**Expected**: Both should return `{"status": "healthy"}` or similar.

#### 1.2 Basic API Scan Test

```bash
curl -X POST https://guardrails-backend.onrender.com/api/v1/scan/ \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "test/repo",
    "files": [{
      "path": "test.py",
      "content": "api_key = \"sk_test_1234567890\""
    }]
  }'
```

**Expected**: Should detect hardcoded API key violation.

#### 1.3 Test with Multiple Violations

```bash
curl -X POST https://guardrails-backend.onrender.com/api/v1/scan/ \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "test/repo",
    "files": [
      {
        "path": "unsafe.py",
        "content": "import subprocess\nsubprocess.run(\"rm -rf /\", shell=True)"
      },
      {
        "path": "secrets.py",
        "content": "password = \"admin123\"\napi_key = \"sk_live_abc123\""
      }
    ],
    "detect_copilot": true
  }'
```

**Expected**: Should detect multiple violations including unsafe shell execution and hardcoded secrets.

### Level 2: Intermediate Tests (15 minutes)

#### 2.1 GitHub PR Integration Test

1. **Create a test repository** (or use existing)
2. **Create a new branch**:
   ```bash
   git checkout -b test-guardrails
   ```

3. **Add test file with violations** (`test_violations.py`):
   ```python
   # Test file with security issues
   api_key = "sk_live_1234567890abcdef"
   password = "admin123"
   
   def unsafe_query(user_input):
       query = "SELECT * FROM users WHERE id = " + user_input
       return execute(query)
   
   import pickle
   data = pickle.loads(user_input)  # Unsafe deserialization
   ```

4. **Commit and push**:
   ```bash
   git add test_violations.py
   git commit -m "Test guardrails scanning"
   git push origin test-guardrails
   ```

5. **Create Pull Request** on GitHub

6. **Verify**:
   - PR should receive comments from the guardrails bot
   - Inline comments on violation lines
   - Summary comment with violation count
   - Commit status check should show results

#### 2.2 Policy Configuration Test

1. **Create repository-specific policy**:
   ```bash
   mkdir -p config/policies/test/repo
   ```

2. **Create `config/policies/test/repo.yaml`**:
   ```yaml
   enforcement_mode: blocking
   severity_threshold: medium
   allow_blocking_override: true
   rule_packs:
     - default
   ```

3. **Test with blocking mode**:
   - Create PR with critical violation
   - Verify merge is blocked
   - Test override functionality

#### 2.3 Copilot Detection Test

1. **Create file that looks AI-generated**:
   ```python
   # This function processes data
   def process_data(data):
       # Process the data
       result = []
       for item in data:
           # Add item to result
           result.append(item)
       return result
   ```

2. **Scan and verify** Copilot detection flags the code

### Level 3: Advanced Tests (30 minutes)

#### 3.1 Full Workflow Test

1. **Create feature branch with multiple file types**:
   - Python file with security issues
   - JavaScript file with vulnerabilities
   - Configuration file with secrets

2. **Open PR and verify**:
   - All files scanned
   - Appropriate violations detected
   - Comments posted correctly
   - Status checks updated

3. **Fix violations and verify**:
   - Update code to fix issues
   - Push new commit
   - Verify violations cleared

#### 3.2 Audit Logging Test

```bash
# Get audit logs
curl "https://guardrails-backend.onrender.com/api/v1/audit/logs?repository=test/repo&limit=10"

# Export audit logs
curl "https://guardrails-backend.onrender.com/api/v1/audit/export?format=json&repository=test/repo"
```

**Expected**: Should return audit logs in JSON format.

#### 3.3 Dashboard API Test

```bash
# Get dashboard stats
curl "https://guardrails-backend.onrender.com/api/v1/dashboard/stats?repository=test/repo"

# Get violation trends
curl "https://guardrails-backend.onrender.com/api/v1/dashboard/violations/trends?repository=test/repo&days=30"

# Get Copilot insights
curl "https://guardrails-backend.onrender.com/api/v1/dashboard/copilot/insights?repository=test/repo"
```

#### 3.4 Performance Test

1. **Create large PR** (100+ files)
2. **Verify**:
   - Scanning completes within reasonable time
   - No timeouts
   - All violations detected
   - Comments posted correctly

#### 3.5 Rule Pack Test

1. **Test banking rule pack**:
   ```yaml
   # config/policies/test/banking.yaml
   enforcement_mode: blocking
   rule_packs:
     - banking
   ```

2. **Create PR with banking-specific violations**
3. **Verify** banking-specific rules are applied

## ⚙️ Configuration Details

### Environment Variables

#### Backend (.env)

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Gemini AI API
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=generate-a-secure-random-key-here
ALLOWED_ORIGINS=https://guardrails-github-app.onrender.com,http://localhost:3000

# Data Residency
DATA_RESIDENCY_REGION=us-east-1
ENABLE_CODE_RETENTION=False

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/guardrails.log
```

#### GitHub App (.env)

```env
# GitHub App Credentials
GITHUB_APP_ID=your_github_app_id
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...full private key content...
-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Backend API URL
BACKEND_API_URL=https://guardrails-backend.onrender.com

# Server
PORT=3000
```

### Policy Configuration Examples

#### Advisory Mode (Informational Only)

```yaml
enforcement_mode: advisory
severity_threshold: low
allow_blocking_override: false
rule_packs:
  - default
```

#### Warning Mode (Alerts but Allow Merge)

```yaml
enforcement_mode: warning
severity_threshold: medium
allow_blocking_override: false
rule_packs:
  - default
```

#### Blocking Mode (Prevent Merge)

```yaml
enforcement_mode: blocking
severity_threshold: high
allow_blocking_override: true  # Allow override with justification
rule_packs:
  - default
  - banking  # Add industry-specific rules
```

#### Strict Blocking (No Override)

```yaml
enforcement_mode: blocking
severity_threshold: critical
allow_blocking_override: false
rule_packs:
  - default
  - healthcare  # HIPAA compliance
```

### Rule Pack Configuration

#### Banking Rule Pack

```yaml
# config/rule_packs/banking.yaml
name: banking
description: Banking and financial services compliance
rules:
  - rule_id: BANK001
    name: PCI-DSS Compliance
    severity: critical
  - rule_id: BANK002
    name: SOX Compliance
    severity: high
```

#### Healthcare Rule Pack

```yaml
# config/rule_packs/healthcare.yaml
name: healthcare
description: Healthcare and HIPAA compliance
rules:
  - rule_id: HIPAA001
    name: PHI Data Protection
    severity: critical
```

## 🔍 Troubleshooting

### Common Issues

1. **Webhook not receiving events**:
   - Verify webhook URL in GitHub App settings
   - Check webhook secret matches
   - Verify app is installed on repository

2. **Scan not completing**:
   - Check backend API is accessible
   - Verify GEMINI_API_KEY is set
   - Check logs for errors

3. **Comments not posting**:
   - Verify GitHub App has write permissions
   - Check installation is active
   - Verify PR is not closed

4. **False positives**:
   - Adjust severity thresholds
   - Disable specific rules
   - Use custom rules to override

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
DEBUG=True
```

## 📝 Test Checklist

- [ ] Health checks pass
- [ ] Basic scan detects violations
- [ ] PR comments are posted
- [ ] Inline comments appear on correct lines
- [ ] Commit status checks update
- [ ] Copilot detection works
- [ ] Policy enforcement modes work
- [ ] Override functionality works
- [ ] Audit logs are created
- [ ] Dashboard APIs return data
- [ ] Export functionality works
- [ ] Rule packs are applied
- [ ] Large PRs are handled efficiently

---

**Note**: This file can be removed after testing and configuration are complete.
