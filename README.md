# Enterprise GitHub Copilot Guardrails Solution

An enterprise-grade guardrails solution that integrates with GitHub and provides AI-assisted code review, security scanning, compliance checking, and policy enforcement for both AI-generated and human-written code.

## 🎯 Key Features

- ✅ **Secure Coding Guardrails**: Detects hardcoded secrets, SQL injection, unsafe operations (OWASP Top 10, CWE mapping)
- ✅ **AI-Assisted Code Review**: Google Gemini-powered contextual analysis with explanations and fix suggestions
- ✅ **Enterprise Compliance**: License checking, IP risk detection, industry-specific rule packs (Banking, Healthcare, Telecom, Government)
- ✅ **Policy-Based Enforcement**: Advisory, Warning, or Blocking modes with per-repository configuration
- ✅ **Copilot Awareness**: Detects AI-generated code and applies differentiated guardrails
- ✅ **Developer-Friendly**: Inline PR comments with clear explanations and suggested fixes
- ✅ **Audit & Reporting**: Comprehensive audit logs, dashboard insights, and exportable reports
- ✅ **Production-Ready**: Scalable architecture, Docker support, enterprise security features

## 🏗️ Architecture

- **Backend**: Python FastAPI service for code analysis and AI integration
- **GitHub App**: TypeScript application for GitHub webhook integration
- **GitHub Action**: TypeScript action for CI/CD workflows
- **AI Engine**: Google Gemini API for contextual code analysis
- **Static Analysis**: Pattern-based security and compliance scanning

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (optional, recommended)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- GitHub App credentials (see [Setup Guide](docs/SETUP.md))

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

# 4. Start all services
docker-compose up -d

# 5. Access API documentation
open http://localhost:8000/docs
```

### Option 2: Manual Setup

```bash
# Run setup script
./setup.sh  # Linux/Mac
# OR
.\setup.ps1  # Windows

# Configure .env files (see above)

# Start backend
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn backend.main:app --reload

# In another terminal, start GitHub App
cd github-app
npm start
```

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed setup instructions
- **[API Documentation](docs/API.md)** - Complete API reference
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture overview
- **[Configuration](docs/CONFIGURATION.md)** - Policy and rule configuration
- **[Usage Guide](docs/USAGE.md)** - How to use the system

## 📁 Project Structure

```
├── backend/              # Python FastAPI backend
│   ├── api/             # API endpoints
│   ├── core/            # Core services (scanner, audit, dashboard)
│   ├── engines/         # Analysis engines (static, AI, license, policy)
│   ├── models/          # Pydantic data models
│   └── tests/           # Test files
├── github-app/          # GitHub App (TypeScript)
│   └── src/             # Source code
├── github-action/       # GitHub Action (TypeScript)
│   └── src/             # Source code
├── config/              # Configuration files
│   ├── policies/        # Policy configurations (YAML)
│   └── rule_packs/      # Enterprise rule packs
├── docs/                # Documentation
├── docker-compose.yml   # Docker orchestration
└── README.md           # This file
```

## 🔧 Configuration

### Policy Configuration

Create repository-specific policies in `config/policies/{owner}/{repo}.yaml`:

```yaml
enforcement_mode: warning  # advisory, warning, blocking
severity_threshold: medium
rule_packs:
  - banking
  - default
```

### Rule Packs

Pre-built rule packs available:
- `banking.yaml` - Banking & financial services compliance
- `healthcare.yaml` - Healthcare & HIPAA compliance
- `telecom.yaml` - Telecommunications compliance
- `government.yaml` - Government & public sector compliance

See [Configuration Guide](docs/CONFIGURATION.md) for details.

## 🔌 API Endpoints

- `POST /api/v1/scan/` - Scan code files
- `GET /api/v1/policies/{repository}` - Get policy
- `PUT /api/v1/policies/{repository}` - Update policy
- `GET /api/v1/audit/logs` - Get audit logs
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/dashboard/copilot/insights` - Copilot insights

Full API documentation available at `/docs` when server is running.

## 🧪 Testing

```bash
cd backend
pytest
```

## 🏭 Production Deployment

1. Set up production database (PostgreSQL)
2. Configure Redis for caching
3. Deploy GitHub App to cloud platform
4. Configure webhook URL
5. Set up monitoring and alerting

See [Setup Guide](docs/SETUP.md) for detailed instructions.

## 📊 Features in Detail

### AI + Static Analysis Hybrid
Combines traditional pattern-based static analysis with AI-powered contextual reasoning to reduce false positives and provide better explanations.

### Copilot Detection
Automatically detects AI-generated code and applies stricter security standards, with clear indicators in violation reports.

### Enterprise Rule Packs
Pre-built compliance rule packs for regulated industries, easily extensible with custom rules.

### Developer-Friendly Feedback
- Inline PR comments on specific lines
- Clear explanations of why issues matter
- Suggested code fixes
- Links to standards (OWASP/CWE)

## 🤝 Contributing

This is a Topcoder challenge submission. For questions or issues, please refer to the challenge documentation.

## 📄 License

MIT License

## 🙏 Acknowledgments

Built for Topcoder Enterprise GitHub Copilot Guardrails Challenge
