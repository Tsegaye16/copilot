# Deploying to Render

Complete guide to deploy the Enterprise Guardrails solution on Render platform.

## Overview

You'll need to deploy:
1. **Backend API** (Python FastAPI) - Web Service
2. **GitHub App** (Node.js/Express) - Web Service
3. **PostgreSQL** (Optional) - Database
4. **Redis** (Optional) - Cache

## Prerequisites

- Render account (sign up at https://render.com)
- GitHub repository with your code
- Google Gemini API key
- GitHub App credentials (from previous setup)

## Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Deploy Backend API

### 2.1 Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository

### 2.2 Configure Backend Service

**Basic Settings:**
- **Name**: `guardrails-backend` (or your choice)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- **Auto-Deploy**: `Yes` (deploys on git push)

### 2.3 Set Environment Variables

Click **"Environment"** tab and add:

```env
# Server
HOST=0.0.0.0
PORT=10000
DEBUG=false

# Gemini API (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key_here

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# OR use Render's PostgreSQL service (see Step 4)

# Redis (if using)
REDIS_URL=redis://host:6379
# OR use Render's Redis service

# GitHub (for webhook verification, optional)
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Security
SECRET_KEY=generate-a-random-secret-key-here
ALLOWED_ORIGINS=https://your-github-app-url.onrender.com
# Note: ALLOWED_ORIGINS can be comma-separated: https://app1.com,https://app2.com

# Data Residency
DATA_RESIDENCY_REGION=us-east-1
ENABLE_CODE_RETENTION=false

# Logging
LOG_LEVEL=INFO
```

**Important**: 
- Replace `your_gemini_api_key_here` with your actual Gemini API key
- Generate a random `SECRET_KEY` (use: `openssl rand -hex 32`)
- Update `ALLOWED_ORIGINS` after deploying GitHub App

### 2.4 Deploy

Click **"Create Web Service"**

Render will:
1. Clone your repo
2. Install dependencies
3. Start the service
4. Provide a URL like: `https://guardrails-backend.onrender.com`

**Note the URL** - you'll need it for the GitHub App!

### 2.5 Verify Backend

1. Wait for deployment to complete (green status)
2. Visit: `https://your-backend-url.onrender.com/health`
3. Should return: `{"status":"healthy","service":"guardrails"}`
4. Visit: `https://your-backend-url.onrender.com/docs` for API docs

## Step 3: Deploy GitHub App

### 3.1 Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Select the same GitHub repository

### 3.2 Configure GitHub App Service

**Basic Settings:**
- **Name**: `guardrails-github-app` (or your choice)
- **Region**: Same as backend (for lower latency)
- **Branch**: `main`
- **Root Directory**: `github-app`
- **Runtime**: `Node`
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm start`

**Advanced Settings:**
- **Auto-Deploy**: `Yes`

### 3.3 Set Environment Variables

Add these environment variables:

```env
# GitHub App Configuration (REQUIRED)
GITHUB_APP_ID=your_github_app_id
GITHUB_APP_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Backend API URL (REQUIRED)
BACKEND_API_URL=https://your-backend-url.onrender.com

# Server
PORT=10000
NODE_ENV=production
```

**Important**:
- Use the **converted private key** (single line with `\n`)
- Use the backend URL from Step 2.5
- All values must match your GitHub App settings

### 3.4 Deploy

Click **"Create Web Service"**

You'll get a URL like: `https://guardrails-github-app.onrender.com`

**Note this URL** - you need it for GitHub App webhook!

## Step 4: Set Up PostgreSQL (Optional but Recommended)

For audit logs and persistent storage:

### 4.1 Create Database

1. Click **"New +"** → **"PostgreSQL"**
2. **Name**: `guardrails-db`
3. **Database**: `guardrails_db`
4. **User**: Auto-generated
5. **Region**: Same as backend
6. Click **"Create Database"**

### 4.2 Get Connection String

1. Go to your database dashboard
2. Find **"Internal Database URL"** or **"Connection String"**
3. Copy it

### 4.3 Update Backend Environment

1. Go to your backend service
2. **Environment** tab
3. Update `DATABASE_URL` with the connection string from step 4.2
4. Save changes (triggers redeploy)

## Step 5: Set Up Redis (Optional)

For caching and task queues:

### 5.1 Create Redis Instance

1. Click **"New +"** → **"Redis"**
2. **Name**: `guardrails-redis`
3. **Region**: Same as backend
4. Click **"Create Redis"**

### 5.2 Get Connection String

1. Go to Redis dashboard
2. Copy **"Internal Redis URL"**

### 5.3 Update Backend Environment

1. Go to backend service
2. Update `REDIS_URL` with Redis connection string
3. Save changes

## Step 6: Update GitHub App Webhook URL

1. Go to https://github.com/settings/apps
2. Click on your GitHub App
3. Click **"Edit"**
4. Update **"Webhook URL"** to:
   ```
   https://your-github-app-url.onrender.com/webhook
   ```
5. Make sure **"Webhook secret"** matches your `GITHUB_WEBHOOK_SECRET`
6. Click **"Update GitHub App"**

## Step 7: Update Backend CORS

1. Go to backend service on Render
2. **Environment** tab
3. Update `ALLOWED_ORIGINS`:
   ```
   https://your-github-app-url.onrender.com
   ```
4. Save changes

## Step 8: Test the Deployment

### 8.1 Test Backend

```bash
# Health check
curl https://your-backend-url.onrender.com/health

# API docs
open https://your-backend-url.onrender.com/docs
```

### 8.2 Test GitHub App

```bash
# Health check
curl https://your-github-app-url.onrender.com/health
```

### 8.3 Test Webhook

1. Create a test repository (or use existing)
2. Install your GitHub App on it
3. Create a test PR with some code
4. Check if webhook is received:
   - Go to GitHub App settings → Advanced → Recent Deliveries
   - Should see webhook events
5. Check if scan runs:
   - Look for PR comments
   - Check backend logs on Render

## Step 9: Monitor and Debug

### View Logs

1. **Backend Logs**:
   - Go to backend service on Render
   - Click **"Logs"** tab
   - See real-time logs

2. **GitHub App Logs**:
   - Go to GitHub App service on Render
   - Click **"Logs"** tab

### Common Issues

**Backend won't start:**
- Check build logs for dependency errors
- Verify `GEMINI_API_KEY` is set
- Check Python version compatibility

**GitHub App won't start:**
- Verify `GITHUB_APP_PRIVATE_KEY` format (must be single line with `\n`)
- Check `BACKEND_API_URL` is correct
- Verify all environment variables are set

**Webhooks not working:**
- Verify webhook URL in GitHub App settings
- Check webhook secret matches
- View GitHub App logs for errors
- Check "Recent Deliveries" in GitHub App settings

**Database connection errors:**
- Verify `DATABASE_URL` is correct
- Check database is running
- Use "Internal Database URL" for same-region services

## Step 10: Production Optimizations

### 10.1 Enable Auto-Deploy

Both services should have **Auto-Deploy: Yes** (already set)

### 10.2 Set Up Custom Domain (Optional)

1. Go to service settings
2. **"Custom Domains"** section
3. Add your domain
4. Follow DNS configuration instructions

### 10.3 Set Up Monitoring

1. **Render Dashboard**: Monitor service health
2. **GitHub App**: Check "Recent Deliveries" for webhook status
3. **Backend Logs**: Monitor for errors

### 10.4 Environment-Specific Configs

Create separate services for:
- **Staging**: `guardrails-backend-staging`
- **Production**: `guardrails-backend-prod`

Use different environment variables for each.

## Render-Specific Configuration Files

Render will automatically detect and use these files if present:

### render.yaml (Optional)

You can create a `render.yaml` in your repo root to define all services:

```yaml
services:
  - type: web
    name: guardrails-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: guardrails-db
          property: connectionString
      - key: PORT
        value: 10000

  - type: web
    name: guardrails-github-app
    env: node
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: GITHUB_APP_ID
        sync: false
      - key: GITHUB_APP_PRIVATE_KEY
        sync: false
      - key: BACKEND_API_URL
        value: https://guardrails-backend.onrender.com

databases:
  - name: guardrails-db
    databaseName: guardrails_db
    user: guardrails_user
```

Then deploy via: **"New +"** → **"Blueprint"** → Select `render.yaml`

## Cost Estimation

**Free Tier** (for testing):
- Web Services: Free (with limitations)
- PostgreSQL: Free (90 days, then $7/month)
- Redis: Not available on free tier

**Paid Tier** (production):
- Web Service: ~$7/month per service
- PostgreSQL: ~$7/month
- Redis: ~$10/month (if needed)

**Total**: ~$21-31/month for full setup

## Security Checklist

- ✅ Environment variables set (not in code)
- ✅ Secrets not committed to git
- ✅ HTTPS enabled (automatic on Render)
- ✅ CORS configured correctly
- ✅ Database uses internal URLs
- ✅ Webhook secret matches
- ✅ Private key properly formatted

## Next Steps

1. ✅ Test with a sample PR
2. ✅ Monitor logs for errors
3. ✅ Configure policies for repositories
4. ✅ Set up alerting (optional)
5. ✅ Document your deployment URLs

Your application is now live on Render! 🚀
