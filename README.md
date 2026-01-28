# Enterprise GitHub Copilot Guardrails Solution

An enterprise-grade guardrails solution that integrates with GitHub and provides AI-assisted code review, security scanning, compliance checking, and policy enforcement for both AI-generated and human-written code. Built for production use with comprehensive security, compliance, and developer experience features.

## 🎯 Challenge Requirements Met

### ✅ Functional Requirements

1. **Secure Coding Guardrails**
   - ✅ Hardcoded secrets detection (API keys, credentials, AWS keys, Stripe keys, tokens, private keys)
   - ✅ SQL injection pattern detection
   - ✅ Insecure deserialization detection
   - ✅ Unsafe file/command execution detection
   - ✅ Explicit Copilot-generated code flagging
   - ✅ OWASP Top 10 and CWE mapping

2. **Enterprise Coding Standards Enforcement**
   - ✅ Naming conventions checking
   - ✅ Logging requirements validation
   - ✅ Error handling pattern enforcement
   - ✅ YAML/JSON rule definition support
   - ✅ Repository-level configuration overrides

3. **AI-Assisted Code Review (Beyond Native Copilot)**
   - ✅ Security vulnerability analysis
   - ✅ Performance issue detection
   - ✅ Maintainability assessment
   - ✅ Detailed explanations with reasoning
   - ✅ Compliant code fix suggestions

4. **License & IP Compliance**
   - ✅ Restricted license detection (GPL, AGPL, etc.)
   - ✅ IP risk flagging in generated code
   - ✅ Code duplication detection
   - ✅ Third-party attribution checking

5. **Policy-Based Enforcement Modes**
   - ✅ Advisory mode (informational comments)
   - ✅ Warning mode (PR annotations and alerts)
   - ✅ Blocking mode (prevent merge)
   - ✅ User override capability for blocking
   - ✅ Per-repository/organization configuration

6. **PR & Commit Integration**
   - ✅ Automatic pull request scanning
   - ✅ Individual commit scanning
   - ✅ Copilot-generated diff identification
   - ✅ Direct PR comment posting
   - ✅ Structured, reviewer-friendly summaries

7. **Traceability & Audit Logs**
   - ✅ Violation detection logging
   - ✅ Action tracking (advisory, warning, blocking)
   - ✅ Resolution state tracking
   - ✅ Exportable logs (JSON, CSV)
   - ✅ Compliance-ready audit trails

### ✅ Non-Functional Requirements

8. **Enterprise-Grade Security**
   - ✅ No source code retention beyond analysis
   - ✅ Configurable data residency
   - ✅ Secure token and secret handling

9. **Performance & Scalability**
   - ✅ Efficient large PR handling
   - ✅ Asynchronous scanning architecture
   - ✅ Minimal developer workflow disruption

10. **Extensibility**
    - ✅ Pluggable rule engine architecture
    - ✅ Easy addition of new security rules
    - ✅ Support for new compliance frameworks
    - ✅ Multi-language support (Python, JavaScript, TypeScript, etc.)

### ✅ Key Differentiating Features

- ⭐ **AI + Static Analysis Hybrid Engine**: Combines pattern-based static analysis with Gemini AI contextual reasoning
- ⭐ **Copilot Awareness**: Detects AI-generated code and applies differentiated, stricter guardrails
- ⭐ **Custom Enterprise Rule Packs**: Pre-built packs for Banking, Healthcare, Telecom, Government
- ⭐ **Developer-Friendly Feedback**: Inline PR comments with clear explanations and fix suggestions
- ⭐ **Dashboard & Reporting**: Organization-level insights, violation trends, Copilot risk hotspots

## 🏗️ Architecture

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │ Webhooks (PR, Push)
         ▼
┌─────────────────┐
│   GitHub App    │  ← TypeScript/Express
│  (Webhook Handler)│
└────────┬────────┘
         │ API Calls
         ▼
┌─────────────────┐
│  Backend API    │  ← Python/FastAPI
│  ┌───────────┐  │
│  │  Scanner  │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │   Static  │  │  Pattern-based analysis
│  │  Analyzer │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │    AI     │  │  Gemini API
│  │  Analyzer │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │  Copilot  │  │  AI code detection
│  │ Detector  │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │  License  │  │  IP compliance
│  │  Checker  │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │  Policy   │  │  Rule enforcement
│  │  Engine   │  │
│  └───────────┘  │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (optional, recommended)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- GitHub App credentials (see [GitHub App Setup](#github-app-setup))

### Option 1: Docker (Recommended)

```bash
# 1. Clone repository
git clone <repository-url>
cd GithubCopilot

# 2. Configure environment
cp backend/.env.example backend/.env
cp github-app/.env.example github-app/.env

# 3. Edit .env files with your credentials:
#    - GEMINI_API_KEY in backend/.env
#    - GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY, GITHUB_WEBHOOK_SECRET in github-app/.env
#    - BACKEND_API_URL in github-app/.env (e.g., http://localhost:8000)

# 4. Start all services
docker-compose up -d

# 5. Access API documentation
open http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure .env file
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# Start server
uvicorn main:app --reload
```

#### GitHub App Setup

```bash
cd github-app
npm install

# Configure .env file
cp .env.example .env
# Edit .env with:
#   - GITHUB_APP_ID
#   - GITHUB_APP_PRIVATE_KEY (full key content)
#   - GITHUB_WEBHOOK_SECRET
#   - BACKEND_API_URL (e.g., http://localhost:8000)

# Build
npm run build

# Start
npm start
```

## 🔧 GitHub App Setup

1. **Create GitHub App**:
   - Go to GitHub → Settings → Developer settings → GitHub Apps
   - Click "New GitHub App"
   - Set name, description, homepage URL: `https://guardrails-backend.onrender.com`
   - Set webhook URL: `https://guardrails-github-app.onrender.com/webhook`
   - Set webhook secret (save for .env)
   - Set permissions:
     - Repository permissions:
       - Contents: Read
       - Pull requests: Read and write
       - Issues: Write
       - Commit statuses: Write
     - Subscribe to events:
       - Pull request
       - Push
   - Generate private key (download .pem file)
   - Note the App ID

2. **Install App on Repository**:
   - Go to your repository → Settings → Integrations → GitHub Apps
   - Find your app and click "Configure"
   - Select repositories to install on
   - Authorize installation

3. **Configure Environment Variables**:
   ```env
   GITHUB_APP_ID=your_app_id
   GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   BACKEND_API_URL=https://guardrails-backend.onrender.com
   ```

## 📁 Project Structure

```
├── backend/              # Python FastAPI backend
│   ├── api/             # API endpoints (scan, policies, audit, dashboard)
│   ├── core/            # Core services
│   │   ├── scanner.py   # Main scanning orchestrator
│   │   ├── audit.py     # Audit logging
│   │   ├── dashboard.py # Dashboard service
│   │   └── config.py    # Configuration management
│   ├── engines/         # Analysis engines
│   │   ├── static_analyzer.py    # Pattern-based security scanning
│   │   ├── ai_analyzer.py        # Gemini AI analysis
│   │   ├── copilot_detector.py   # AI code detection
│   │   ├── license_checker.py    # License/IP compliance
│   │   └── policy_engine.py      # Policy enforcement
│   ├── models/          # Pydantic data models
│   ├── main.py          # FastAPI application entry
│   └── requirements.txt # Python dependencies
├── github-app/          # GitHub App (TypeScript)
│   ├── src/
│   │   ├── index.ts     # Express server
│   │   ├── webhooks.ts  # Webhook handlers
│   │   ├── scanner.ts   # Backend API integration
│   │   └── github-client.ts # GitHub API client
│   ├── package.json
│   └── tsconfig.json
├── github-action/      # GitHub Action (TypeScript)
│   └── src/
│       └── index.ts    # Action implementation
├── config/              # Configuration files
│   ├── policies/        # Policy configurations (YAML)
│   │   └── default.yaml
│   └── rule_packs/      # Enterprise rule packs
│       ├── banking.yaml
│       ├── healthcare.yaml
│       ├── telecom.yaml
│       └── government.yaml
├── docker-compose.yml   # Docker orchestration
├── render.yaml          # Render.com deployment config
└── README.md           # This file
```

## 🔌 API Endpoints

### Scan API

- `POST /api/v1/scan/` - Scan code files
  ```json
  {
    "repository": "owner/repo",
    "pull_request_number": 123,
    "files": [
      {
        "path": "src/file.py",
        "content": "code content...",
        "metadata": {}
      }
    ],
    "detect_copilot": true,
    "policy_config": {}
  }
  ```

### Policy API

- `GET /api/v1/policies/{repository}` - Get policy configuration
- `PUT /api/v1/policies/{repository}` - Update policy configuration
- `GET /api/v1/policies/` - List all policies

### Audit API

- `GET /api/v1/audit/logs` - Get audit logs
  - Query params: `repository`, `start_date`, `end_date`, `limit`
- `GET /api/v1/audit/export` - Export audit logs
  - Query params: `format` (json/csv), `repository`, `start_date`, `end_date`

### Dashboard API

- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/dashboard/violations/trends` - Violation trends over time
- `GET /api/v1/dashboard/copilot/insights` - Copilot-related insights

Full interactive API documentation available at `/docs` when server is running.

## ⚙️ Configuration

### Policy Configuration

Create repository-specific policies in `config/policies/{owner}/{repo}.yaml`:

```yaml
enforcement_mode: blocking  # advisory, warning, blocking
severity_threshold: medium  # low, medium, high, critical
allow_blocking_override: true  # Allow users to override blocking
enabled_rules: []  # List of enabled rule IDs (empty = all enabled)
disabled_rules: []  # List of disabled rule IDs
rule_packs:
  - banking
  - default
custom_rules: []
```

### Rule Packs

Pre-built enterprise rule packs:

- **banking.yaml** - Banking & financial services compliance (PCI-DSS, SOX)
- **healthcare.yaml** - Healthcare & HIPAA compliance
- **telecom.yaml** - Telecommunications compliance
- **government.yaml** - Government & public sector compliance

Each rule pack includes:
- Industry-specific security rules
- Compliance requirements
- Regulatory mappings
- Custom severity thresholds

### Environment Variables

#### Backend (.env)

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Security
SECRET_KEY=change-me-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Data Residency
DATA_RESIDENCY_REGION=us-east-1
ENABLE_CODE_RETENTION=False

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/guardrails.log
```

#### GitHub App (.env)

```env
# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Backend API
BACKEND_API_URL=https://guardrails-backend.onrender.com

# Server
PORT=3000
```

## 🚢 Deployment

### Render.com Deployment

The project is configured for deployment on Render.com:

1. **Backend Service**:
   - Connect GitHub repository
   - Set root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment variables: Set all from backend/.env

2. **GitHub App Service**:
   - Connect GitHub repository
   - Set root directory: `github-app`
   - Build command: `npm install && npm run build`
   - Start command: `node dist/index.js`
   - Environment variables: Set all from github-app/.env
   - Set webhook URL in GitHub App settings to: `https://your-app.onrender.com/webhook`

See `render.yaml` for blueprint deployment.

### Docker Deployment

```bash
docker-compose up -d
```

Services:
- Backend: http://localhost:8000
- GitHub App: http://localhost:3000

## 🧪 Testing

### Quick Test

1. **Health Checks**:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:3000/health
   ```

2. **Basic Scan**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/scan/ \
     -H "Content-Type: application/json" \
     -d '{
       "repository": "test/repo",
       "files": [{
         "path": "test.py",
         "content": "api_key = \"sk_test_1234567890\""
       }]
     }'
   ```

3. **Create Test PR**:
   - Create a branch with code containing security issues
   - Open a pull request
   - Check PR comments for violations

### Comprehensive Testing

See `TESTING_AND_CONFIG.md` for detailed testing scenarios from basic to advanced.

## 📊 Features in Detail

### AI + Static Analysis Hybrid

The system combines:
- **Static Analysis**: Fast pattern-based detection of known vulnerabilities
- **AI Analysis**: Contextual understanding using Gemini AI for:
  - Intent analysis
  - False positive reduction
  - Complex vulnerability detection
  - Performance and maintainability insights

### Copilot Detection

Automatically identifies AI-generated code using:
- Code style patterns
- Comment characteristics
- Variable naming patterns
- Code structure analysis

Applies stricter security standards and clearly flags violations in AI-generated code.

### Policy Enforcement

Three enforcement modes:

1. **Advisory**: Informational comments only, merge always allowed
2. **Warning**: PR annotations and alerts, merge allowed with warnings
3. **Blocking**: Prevents merge until issues resolved (with override option)

Policies configurable per repository or organization.

### Developer Experience

- **Inline Comments**: Violations appear directly on code lines
- **Clear Explanations**: Why the issue matters and its impact
- **Fix Suggestions**: Specific code improvements
- **Standards Mapping**: Links to OWASP/CWE for learning
- **Copilot Indicators**: Clear marking of AI-generated code issues

### Audit & Compliance

- **Comprehensive Logging**: All scans, violations, and actions logged
- **Exportable Reports**: JSON and CSV formats for compliance teams
- **Trend Analysis**: Track violation patterns over time
- **Copilot Insights**: Monitor AI-generated code risk

## 🔒 Security

- **No Code Retention**: Source code not stored beyond analysis
- **Secure Secrets**: Environment variables and secret management
- **Data Residency**: Configurable data storage regions
- **Webhook Verification**: HMAC signature validation
- **API Authentication**: Token-based API access (optional)

## 🤝 Contributing

This is a Topcoder challenge submission. The solution is production-ready and includes:

- ✅ All functional requirements
- ✅ All non-functional requirements
- ✅ Bonus features (dashboard, reporting)
- ✅ Comprehensive documentation
- ✅ Deployment configurations
- ✅ Enterprise-grade security

## 📄 License

MIT License

## 🙏 Acknowledgments

Built for Topcoder Enterprise GitHub Copilot Guardrails Challenge

---

**Status**: ✅ Production Ready | All Requirements Met | Enterprise-Grade Solution

**Deployed Services**:
- GitHub App: https://guardrails-github-app.onrender.com
- Backend API: https://guardrails-backend.onrender.com
