# Architecture Overview

## System Architecture

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │
         │ Webhooks
         ▼
┌─────────────────┐
│   GitHub App    │  (TypeScript)
│  (Express.js)   │
└────────┬────────┘
         │
         │ HTTP API
         ▼
┌─────────────────┐
│  Backend API    │  (Python FastAPI)
│                 │
│  ┌───────────┐  │
│  │  Scanner  │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  Engines  │  │
│  │           │  │
│  │ • Static  │  │
│  │ • AI      │  │
│  │ • License │  │
│  │ • Policy  │  │
│  └───────────┘  │
└────────┬────────┘
         │
         │
    ┌────▼────┐
    │ Gemini │
    │   API  │
    └────────┘
```

## Components

### 1. GitHub App (TypeScript)

- **Purpose**: GitHub integration layer
- **Responsibilities**:
  - Receive webhooks from GitHub
  - Fetch PR/commit data
  - Post scan results as PR comments
  - Set commit status checks

### 2. Backend API (Python FastAPI)

- **Purpose**: Core scanning and analysis engine
- **Components**:
  - **Scanner**: Orchestrates all analysis engines
  - **Static Analyzer**: Pattern-based security scanning
  - **AI Analyzer**: Gemini-powered contextual analysis
  - **Copilot Detector**: Identifies AI-generated code
  - **License Checker**: License and IP compliance
  - **Policy Engine**: Rule management and enforcement

### 3. Analysis Engines

#### Static Analyzer
- Regex-based pattern matching
- Detects: secrets, SQL injection, unsafe operations
- Maps to OWASP/CWE standards

#### AI Analyzer
- Uses Google Gemini API
- Contextual code understanding
- Explains violations and suggests fixes
- Reduces false positives

#### Copilot Detector
- Heuristic-based detection
- Metadata analysis
- Content pattern matching

#### License Checker
- License header detection
- Third-party attribution checking
- Duplicate code detection

#### Policy Engine
- YAML/JSON configuration
- Rule pack management
- Enforcement mode logic

## Data Flow

1. **PR Opened/Updated**:
   - GitHub sends webhook → GitHub App
   - GitHub App fetches PR files
   - GitHub App calls Backend API
   - Backend scans files
   - Results returned to GitHub App
   - GitHub App posts PR comments

2. **Commit Pushed**:
   - GitHub sends webhook → GitHub App
   - GitHub App fetches commit files
   - Backend scans files
   - GitHub App sets commit status

## Security Considerations

- **No Code Retention**: Code is processed and discarded
- **Data Residency**: Configurable data storage location
- **Secure Secrets**: Environment variables, no hardcoding
- **API Authentication**: (To be implemented in production)

## Scalability

- **Async Processing**: FastAPI async/await
- **Background Tasks**: Audit logging in background
- **Caching**: Redis for rule packs and policies
- **Database**: PostgreSQL for audit logs (optional)

## Extensibility

- **Pluggable Rules**: Easy to add new rules
- **Rule Packs**: Industry-specific rule sets
- **Custom Policies**: Per-repository configuration
- **API-First**: Easy integration with other tools
