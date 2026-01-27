# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication for local development. In production, implement API key or OAuth authentication.

## Endpoints

### Scan Code

**POST** `/scan/`

Scan code files for violations.

**Request Body:**
```json
{
  "repository": "owner/repo",
  "pull_request_number": 123,
  "commit_sha": "abc123",
  "files": [
    {
      "path": "src/main.py",
      "content": "code content here",
      "metadata": {
        "additions": 10,
        "deletions": 5
      }
    }
  ],
  "detect_copilot": true,
  "policy_config": {
    "enforcement_mode": "warning",
    "severity_threshold": "medium"
  }
}
```

**Response:**
```json
{
  "scan_id": "uuid",
  "repository": "owner/repo",
  "timestamp": "2024-01-01T00:00:00Z",
  "violations": [
    {
      "rule_id": "SEC001",
      "rule_name": "Hardcoded API Key",
      "category": "security",
      "severity": "critical",
      "file_path": "src/main.py",
      "line_number": 15,
      "message": "Hardcoded secret detected",
      "explanation": "Detailed explanation...",
      "fix_suggestion": "Use environment variables",
      "standard_mappings": ["CWE-798", "OWASP-A07:2021"],
      "is_copilot_generated": false
    }
  ],
  "summary": {
    "total_violations": 1,
    "by_severity": {
      "critical": 1,
      "high": 0,
      "medium": 0,
      "low": 0
    }
  },
  "enforcement_action": "blocking",
  "can_merge": false,
  "copilot_detected": false,
  "processing_time_ms": 1234.56
}
```

### Get Policy

**GET** `/policies/{repository}`

Get policy configuration for a repository.

**Response:**
```json
{
  "enforcement_mode": "warning",
  "severity_threshold": "medium",
  "enabled_rules": [],
  "disabled_rules": [],
  "rule_packs": ["default"],
  "allow_blocking_override": true
}
```

### Update Policy

**PUT** `/policies/{repository}`

Update policy configuration.

**Request Body:**
```json
{
  "enforcement_mode": "blocking",
  "severity_threshold": "high",
  "rule_packs": ["banking", "default"]
}
```

### Get Audit Logs

**GET** `/audit/logs`

Get audit logs with optional filtering.

**Query Parameters:**
- `repository` (optional): Filter by repository
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)
- `limit` (optional): Max results (default: 100, max: 1000)

### Export Audit Logs

**GET** `/audit/logs/export`

Export audit logs in JSON or CSV format.

**Query Parameters:**
- `repository` (optional): Filter by repository
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `format`: `json` or `csv`

### Dashboard Stats

**GET** `/dashboard/stats`

Get dashboard statistics.

**Query Parameters:**
- `repository` (optional): Filter by repository
- `start_date` (optional): Start date
- `end_date` (optional): End date

### Violation Trends

**GET** `/dashboard/violations/trends`

Get violation trends over time.

**Query Parameters:**
- `repository` (optional): Filter by repository
- `days`: Number of days (default: 30, max: 365)

### Copilot Insights

**GET** `/dashboard/copilot/insights`

Get Copilot-related insights.

**Query Parameters:**
- `repository` (optional): Filter by repository

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error
