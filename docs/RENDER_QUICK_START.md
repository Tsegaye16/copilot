# Render Deployment - Quick Start

Fastest way to deploy to Render in 10 minutes.

## Prerequisites Checklist

- [ ] Render account (https://render.com)
- [ ] Code pushed to GitHub
- [ ] Gemini API key ready
- [ ] GitHub App credentials ready

## Quick Deploy Steps

### 1. Deploy Backend (5 min)

1. Go to https://dashboard.render.com
2. **New +** → **Web Service**
3. Connect GitHub repo
4. Settings:
   - **Name**: `guardrails-backend`
   - **Root Directory**: `backend`
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable:
   - `GEMINI_API_KEY` = your key
6. **Create Web Service**
7. **Copy the URL** (e.g., `https://guardrails-backend.onrender.com`)

### 2. Deploy GitHub App (3 min)

1. **New +** → **Web Service** (same repo)
2. Settings:
   - **Name**: `guardrails-github-app`
   - **Root Directory**: `github-app`
   - **Build**: `npm install && npm run build`
   - **Start**: `npm start`
3. Add environment variables:
   - `GITHUB_APP_ID` = your app ID
   - `GITHUB_APP_PRIVATE_KEY` = your converted key
   - `GITHUB_WEBHOOK_SECRET` = your secret
   - `BACKEND_API_URL` = backend URL from step 1
4. **Create Web Service**
5. **Copy the URL** (e.g., `https://guardrails-github-app.onrender.com`)

### 3. Update GitHub App Webhook (2 min)

1. Go to https://github.com/settings/apps
2. Click your app → **Edit**
3. Set **Webhook URL** = GitHub App URL from step 2 + `/webhook`
4. **Update**

### 4. Test (1 min)

1. Create a test PR
2. Check if comments appear
3. Check Render logs if issues

## Using Blueprint (Alternative)

If you have `render.yaml` in your repo:

1. **New +** → **Blueprint**
2. Select your repo
3. Render will create all services automatically
4. Set environment variables in dashboard

## Troubleshooting

**Service won't start?**
- Check build logs
- Verify environment variables
- Check start command

**Webhook not working?**
- Verify webhook URL in GitHub App settings
- Check GitHub App logs on Render
- Verify webhook secret matches

**Need help?**
- Check full guide: `docs/DEPLOYMENT_RENDER.md`
- Render docs: https://render.com/docs
- Check service logs on Render dashboard

Done! 🎉
