# Render Deployment Checklist

Use this checklist to ensure successful deployment.

## Pre-Deployment

- [ ] Code pushed to GitHub
- [ ] Gemini API key obtained
- [ ] GitHub App created (see `docs/GITHUB_APP_SETUP.md`)
- [ ] GitHub App credentials ready:
  - [ ] App ID
  - [ ] Private Key (converted to single line)
  - [ ] Webhook Secret

## Deploy Backend

- [ ] Created new Web Service on Render
- [ ] Connected GitHub repository
- [ ] Set Root Directory: `backend`
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- [ ] Added environment variables:
  - [ ] `GEMINI_API_KEY` = your key
  - [ ] `PORT` = 10000 (or let Render set automatically)
  - [ ] `DEBUG` = false
- [ ] Service deployed successfully
- [ ] Backend URL noted: `https://________________.onrender.com`
- [ ] Health check passed: `/health` endpoint works
- [ ] API docs accessible: `/docs` endpoint works

## Deploy GitHub App

- [ ] Created new Web Service on Render
- [ ] Connected same GitHub repository
- [ ] Set Root Directory: `github-app`
- [ ] Set Build Command: `npm install && npm run build`
- [ ] Set Start Command: `npm start`
- [ ] Added environment variables:
  - [ ] `GITHUB_APP_ID` = your app ID
  - [ ] `GITHUB_APP_PRIVATE_KEY` = converted key (single line with \n)
  - [ ] `GITHUB_WEBHOOK_SECRET` = your webhook secret
  - [ ] `BACKEND_API_URL` = backend URL from above
  - [ ] `PORT` = 10000
  - [ ] `NODE_ENV` = production
- [ ] Service deployed successfully
- [ ] GitHub App URL noted: `https://________________.onrender.com`
- [ ] Health check passed: `/health` endpoint works

## Configure GitHub App Webhook

- [ ] Went to GitHub App settings
- [ ] Updated Webhook URL to: `https://your-github-app-url.onrender.com/webhook`
- [ ] Verified Webhook Secret matches
- [ ] Saved changes

## Update Backend CORS

- [ ] Went to backend service on Render
- [ ] Updated `ALLOWED_ORIGINS` environment variable
- [ ] Set to: `https://your-github-app-url.onrender.com`
- [ ] Saved changes (triggers redeploy)

## Optional: Database Setup

- [ ] Created PostgreSQL database on Render
- [ ] Noted connection string
- [ ] Updated `DATABASE_URL` in backend environment
- [ ] Verified connection works

## Optional: Redis Setup

- [ ] Created Redis instance on Render
- [ ] Noted connection string
- [ ] Updated `REDIS_URL` in backend environment
- [ ] Verified connection works

## Testing

- [ ] Backend health check: ✅
- [ ] GitHub App health check: ✅
- [ ] Created test repository
- [ ] Installed GitHub App on test repo
- [ ] Created test PR with code
- [ ] Verified webhook received (check GitHub App → Advanced → Recent Deliveries)
- [ ] Verified scan ran (check PR comments)
- [ ] Checked backend logs for errors
- [ ] Checked GitHub App logs for errors

## Post-Deployment

- [ ] All services running (green status)
- [ ] No errors in logs
- [ ] Webhooks working correctly
- [ ] PR scanning working
- [ ] Documentation updated with production URLs
- [ ] Team notified of deployment

## Troubleshooting Notes

_Use this space to note any issues and solutions:_

```
Issue:
Solution:

Issue:
Solution:
```

## Deployment URLs

**Backend API:**
```
https://________________.onrender.com
```

**GitHub App:**
```
https://________________.onrender.com
```

**API Documentation:**
```
https://________________.onrender.com/docs
```

## Next Steps

- [ ] Configure policies for repositories
- [ ] Set up monitoring/alerting
- [ ] Document deployment process
- [ ] Train team on usage

---

**Deployment Date:** _______________
**Deployed By:** _______________
