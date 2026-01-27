# Configuration Guide

## Policy Configuration

Policies are defined in YAML files under `config/policies/`.

### Default Policy

Location: `config/policies/default.yaml`

```yaml
enforcement_mode: warning  # advisory, warning, or blocking
severity_threshold: medium  # low, medium, high, or critical
allow_blocking_override: true

enabled_rules: []  # List of rule IDs to enable (empty = all)
disabled_rules: []  # List of rule IDs to disable

rule_packs:
  - default

custom_rules: []
```

### Repository-Specific Policy

Create `config/policies/{owner}/{repo}.yaml` for repository-specific settings.

Example: `config/policies/acme/backend.yaml`

```yaml
enforcement_mode: blocking
severity_threshold: high
rule_packs:
  - banking
  - default
disabled_rules:
  - SEC205  # Disable path traversal check for this repo
```

## Rule Packs

Rule packs are located in `config/rule_packs/`.

### Available Rule Packs

- **banking.yaml**: Banking and financial services compliance
- **healthcare.yaml**: Healthcare and HIPAA compliance
- **telecom.yaml**: Telecommunications compliance
- **government.yaml**: Government and public sector compliance

### Custom Rule Pack

Create a new YAML file in `config/rule_packs/`:

```yaml
name: Custom Rule Pack
description: Your custom rules
version: 1.0.0

rules:
  - id: CUSTOM001
    name: Custom Rule Name
    category: security  # security, compliance, code_quality, license, ip_risk, standard
    severity: high  # low, medium, high, critical
    pattern: |
      (?i)your[_-]?pattern[_-]?here
    explanation: "Why this is a problem"
    standard_mappings:
      - CWE-XXX
      - OWASP-AXX:2021
```

## Enforcement Modes

### Advisory
- Issues are reported as informational comments
- PR can always be merged
- Useful for awareness and education

### Warning
- Issues are reported with warnings
- PR can be merged but warnings are visible
- Recommended for most organizations

### Blocking
- Critical/high issues block merge
- PR cannot be merged until issues resolved
- Can be overridden if `allow_blocking_override: true`
- Use for production-critical repositories

## Environment Variables

### Backend

See `backend/.env.example` for all available options.

Key variables:
- `GEMINI_API_KEY`: Google Gemini API key (required)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ENABLE_CODE_RETENTION`: Set to `false` for no code storage

### GitHub App

See `github-app/.env.example` for all available options.

Key variables:
- `GITHUB_APP_ID`: GitHub App ID
- `GITHUB_APP_PRIVATE_KEY`: GitHub App private key
- `GITHUB_WEBHOOK_SECRET`: Webhook secret
- `BACKEND_API_URL`: Backend API URL

## GitHub App Permissions

Required permissions:
- **Repository contents**: Read
- **Pull requests**: Read & Write
- **Issues**: Write
- **Commit statuses**: Write

Required events:
- Pull request
- Push

## Integration with GitHub Actions

Add to `.github/workflows/guardrails.yml`:

```yaml
name: Guardrails Scan

on:
  pull_request:
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Guardrails Scan
        uses: ./github-action
        with:
          backend_url: ${{ secrets.GUARDRAILS_API_URL }}
          api_key: ${{ secrets.GUARDRAILS_API_KEY }}
          detect_copilot: 'true'
```
