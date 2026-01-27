# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Get Your API Keys

1. **Google Gemini API Key**:
   - Visit https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key

2. **GitHub App** (if using GitHub App):
   - Go to GitHub Settings > Developer settings > GitHub Apps
   - Create a new app
   - Note: App ID, generate private key, set webhook secret

## Step 2: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd GithubCopilot

# Run setup script
./setup.sh  # Linux/Mac
# OR
.\setup.ps1  # Windows
```

## Step 3: Configure Environment

### Backend Configuration

Edit `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/guardrails_db
REDIS_URL=redis://localhost:6379/0
```

### GitHub App Configuration (Optional)

Edit `github-app/.env`:

```env
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----
GITHUB_WEBHOOK_SECRET=your_webhook_secret
BACKEND_API_URL=http://localhost:8000
```

## Step 4: Start Services

### Option A: Docker (Easiest)

```bash
docker-compose up -d
```

### Option B: Manual

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn backend.main:app --reload
```

**Terminal 2 - GitHub App (Optional):**
```bash
cd github-app
npm start
```

## Step 5: Test the API

1. **Check health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **View API docs**:
   Open http://localhost:8000/docs in your browser

3. **Test scan**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/scan/ \
     -H "Content-Type: application/json" \
     -d '{
       "repository": "test/repo",
       "files": [{
         "path": "test.py",
         "content": "api_key = \"sk_live_1234567890\""
       }],
       "detect_copilot": true
     }'
   ```

## Step 6: Configure GitHub App (Optional)

1. **Install GitHub App**:
   - Go to your GitHub App settings
   - Install on repositories you want to scan

2. **Configure Webhook**:
   - Set webhook URL: `https://your-domain.com/webhook`
   - Or use ngrok for local testing: `ngrok http 3000`

3. **Test Webhook**:
   - Create a test PR
   - Check if scan runs automatically

## Step 7: Configure Policies

Create a policy file for your repository:

```bash
mkdir -p config/policies/owner
cat > config/policies/owner/repo.yaml << EOF
enforcement_mode: warning
severity_threshold: medium
rule_packs:
  - default
EOF
```

## Next Steps

- Read [Usage Guide](docs/USAGE.md) for detailed usage
- Configure [Policies](docs/CONFIGURATION.md) for your needs
- Explore [API Documentation](docs/API.md)
- Check [Architecture](docs/ARCHITECTURE.md) for system design

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Check if port 8000 is available
- Verify `.env` file is configured

### GitHub App not receiving webhooks
- Verify webhook URL is accessible
- Check webhook secret matches
- Review GitHub App logs

### No violations detected
- Check if files are being scanned
- Verify rule packs are enabled
- Review backend logs for errors

## Need Help?

- Check [Documentation](docs/) folder
- Review [Setup Guide](docs/SETUP.md)
- Check API docs at http://localhost:8000/docs
