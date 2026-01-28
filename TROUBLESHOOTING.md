# Troubleshooting Guide

## Issue: No Comments or Warnings Appearing on PRs

If you're not seeing comments or warnings when you push code and create PRs, follow these debugging steps:

### Step 1: Verify GitHub App Installation

1. **Check if GitHub App is installed on your repository:**
   - Go to your repository → Settings → Integrations → GitHub Apps
   - Look for your guardrails app
   - Verify it's installed and has the correct permissions

2. **Verify App Permissions:**
   - Contents: Read
   - Pull requests: Read and write
   - Issues: Write
   - Commit statuses: Write

3. **Check Subscribed Events:**
   - Pull request ✓
   - Push ✓

### Step 2: Verify Webhook Configuration

1. **Check Webhook URL in GitHub App Settings:**
   - Go to GitHub → Settings → Developer settings → GitHub Apps
   - Select your app
   - Check "Webhook URL" is set to: `https://guardrails-github-app.onrender.com/webhook`
   - Verify "Webhook secret" matches your `GITHUB_WEBHOOK_SECRET` environment variable

2. **Test Webhook Delivery:**
   - In GitHub App settings, go to "Advanced" → "Recent deliveries"
   - Check if webhooks are being received
   - Click on a delivery to see the response
   - Look for any errors (401, 500, etc.)

### Step 3: Check Environment Variables

Verify all environment variables are set correctly in your Render.com services:

**GitHub App Service (.env):**
```env
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your_webhook_secret
BACKEND_API_URL=https://guardrails-backend.onrender.com
PORT=3000
```

**Backend Service (.env):**
```env
GEMINI_API_KEY=your_gemini_api_key
HOST=0.0.0.0
PORT=8000
```

### Step 4: Check Service Logs

1. **GitHub App Logs (Render.com):**
   - Go to your GitHub App service on Render
   - Check "Logs" tab
   - Look for:
     - `[Webhook] Received: pull_request`
     - `[PR] Processing PR #X`
     - `[Scanner] Starting scan`
     - Any error messages

2. **Backend Logs (Render.com):**
   - Go to your Backend service on Render
   - Check "Logs" tab
   - Look for:
     - Scan requests received
     - Any API errors

### Step 5: Test Backend API Directly

Test if the backend is accessible:

```bash
# Health check
curl https://guardrails-backend.onrender.com/health

# Test scan
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

### Step 6: Common Issues and Solutions

#### Issue: Webhook Signature Verification Failed

**Symptoms:** Logs show "Signature verification failed"

**Solution:**
- Verify `GITHUB_WEBHOOK_SECRET` matches the secret in GitHub App settings
- Ensure the secret doesn't have extra spaces or quotes
- Restart the GitHub App service after updating the secret

#### Issue: Backend API Not Reachable

**Symptoms:** Logs show "ECONNREFUSED" or "ENOTFOUND"

**Solution:**
- Verify `BACKEND_API_URL` is correct (should be `https://guardrails-backend.onrender.com`)
- Check backend service is running
- Test backend health endpoint
- Ensure backend service is not sleeping (Render free tier services sleep after inactivity)

#### Issue: No Files Found in PR

**Symptoms:** Logs show "No files found in PR"

**Solution:**
- Check if PR has any file changes
- Verify GitHub App has "Contents: Read" permission
- Check if files are in a private repository (may need additional permissions)

#### Issue: GitHub API Authentication Failed

**Symptoms:** Logs show "401 Unauthorized" or "403 Forbidden"

**Solution:**
- Verify `GITHUB_APP_ID` is correct
- Check `GITHUB_APP_PRIVATE_KEY` is properly formatted (with `\n` for newlines)
- Ensure GitHub App is installed on the repository
- Verify installation has correct permissions

#### Issue: Comments Not Posting

**Symptoms:** Scan completes but no comments appear

**Solution:**
- Check GitHub App has "Pull requests: Read and write" permission
- Verify "Issues: Write" permission (PR comments use Issues API)
- Check logs for specific error messages
- Try posting a manual comment to verify permissions

### Step 7: Enable Debug Logging

Add more detailed logging by checking the console output. The enhanced logging will show:

- Webhook reception
- Event type and action
- File fetching progress
- Scan progress
- Comment posting attempts
- Error details

### Step 8: Manual Testing

1. **Create a test PR with violations:**
   ```python
   # test_violations.py
   api_key = "sk_live_1234567890abcdef"
   password = "admin123"
   
   def unsafe_query(user_input):
       query = "SELECT * FROM users WHERE id = " + user_input
       return execute(query)
   ```

2. **Push and create PR:**
   ```bash
   git checkout -b test-guardrails
   git add test_violations.py
   git commit -m "Test guardrails"
   git push origin test-guardrails
   # Create PR on GitHub
   ```

3. **Check logs immediately after creating PR**

### Step 9: Verify Render.com Services

1. **Check both services are running:**
   - GitHub App: https://guardrails-github-app.onrender.com/health
   - Backend: https://guardrails-backend.onrender.com/health

2. **If services are sleeping (free tier):**
   - First webhook after sleep may fail
   - Wait a few seconds and try again
   - Consider upgrading to prevent sleeping

### Step 10: Check GitHub App Status

1. Go to your repository → Settings → Integrations → GitHub Apps
2. Click on your app
3. Check "Recent deliveries" tab
4. Look for failed deliveries
5. Click on a delivery to see:
   - Request payload
   - Response status
   - Response body

## Quick Diagnostic Checklist

- [ ] GitHub App is installed on repository
- [ ] Webhook URL is correct: `https://guardrails-github-app.onrender.com/webhook`
- [ ] Webhook secret matches environment variable
- [ ] Backend API is accessible: `https://guardrails-backend.onrender.com/health`
- [ ] `BACKEND_API_URL` is set correctly in GitHub App service
- [ ] `GEMINI_API_KEY` is set in Backend service
- [ ] Both services are running (not sleeping)
- [ ] GitHub App has correct permissions
- [ ] PR has file changes
- [ ] Check logs for errors

## Getting Help

If issues persist:

1. **Collect logs:**
   - GitHub App service logs
   - Backend service logs
   - GitHub App webhook delivery logs

2. **Test endpoints:**
   - Health checks
   - Direct API scan test

3. **Verify configuration:**
   - Environment variables
   - GitHub App settings
   - Repository permissions

---

**Note:** This file can be removed after troubleshooting is complete.
