# GitHub App Setup Guide

Complete step-by-step guide to create and configure your GitHub App for the Enterprise Guardrails solution.

## Prerequisites

- A GitHub account
- Admin access to the repositories you want to scan
- Your backend API running (or know the URL where it will run)

## Step 1: Create the GitHub App

1. **Go to GitHub App Settings**:
   - Navigate to: https://github.com/settings/apps
   - Or: GitHub → Your Profile → Settings → Developer settings → GitHub Apps

2. **Click "New GitHub App"** (top right)

3. **Fill in Basic Information**:

   **GitHub App name**: 
   - Example: `Enterprise Guardrails` or `Copilot Guardrails`
   - Must be unique across GitHub

   **Homepage URL**: 
   - Your organization's website or the project repository URL
   - Example: `https://github.com/your-org/guardrails`

   **User authorization callback URL**: 
   - Leave empty (we're using installation-based auth)

   **Webhook URL**: 
   - **For local development**: Use ngrok (see Step 2 below)
   - **For production**: Your deployed app URL + `/webhook`
   - Example: `https://your-domain.com/webhook` or `https://abc123.ngrok.io/webhook`

   **Webhook secret**: 
   - Generate a random secret (you'll need this later)
   - Use: `openssl rand -hex 20` or any password generator
   - **IMPORTANT**: Save this secret! You'll need it for `.env` file
   - Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

   **Repository permissions**: 
   - Select "Only select repositories" (recommended) or "All repositories"
   - You can change this later

## Step 2: Configure Permissions

Scroll down to **"Permissions & events"** section:

### Repository Permissions

Set the following permissions:

1. **Contents**: 
   - Permission: `Read-only`
   - Why: Need to read file contents for scanning

2. **Pull requests**: 
   - Permission: `Read and write`
   - Why: Need to read PRs, post comments, and set status

3. **Issues**: 
   - Permission: `Write`
   - Why: Post summary comments on PRs

4. **Metadata**: 
   - Permission: `Read-only` (default)
   - Why: Basic repository metadata

5. **Commit statuses**: 
   - Permission: `Write`
   - Why: Set commit status checks

### Subscribe to Events

Check the following events:

- ✅ **Pull request** (required)
- ✅ **Push** (required)
- ⬜ Pull request review (optional)

## Step 3: Where Can This GitHub App Be Installed?

Choose based on your needs:

- **Only on this account**: Only you can install it
- **Any account**: Anyone can install it (for public distribution)

For enterprise use, select **"Only on this account"**.

## Step 4: Create the GitHub App

1. Click **"Create GitHub App"** (green button at bottom)

2. **IMPORTANT - Save These Credentials**:
   - You'll see the App ID immediately
   - You need to generate a private key

## Step 5: Generate Private Key

1. On the app page, scroll to **"Private keys"** section

2. Click **"Generate a private key"**

3. **CRITICAL**: 
   - A `.pem` file will download automatically
   - **Save this file securely** - you can only download it once!
   - This is your `GITHUB_APP_PRIVATE_KEY`

4. **Convert the key format**:
   - The downloaded file is a multi-line PEM file
   - For the `.env` file, you need it as a single line with `\n` for newlines
   - See Step 6 for conversion

## Step 6: Prepare Private Key for .env File

The private key needs to be in a specific format for the `.env` file.

### Option A: Manual Conversion

1. Open the downloaded `.pem` file in a text editor
2. Copy the entire content (including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`)
3. Replace each actual newline with `\n`
4. The result should be one long line

Example:
```
-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n...\n-----END RSA PRIVATE KEY-----
```

### Option B: Use a Script

Create a file `convert-key.js`:

```javascript
const fs = require('fs');
const keyPath = process.argv[2];
const key = fs.readFileSync(keyPath, 'utf8');
console.log(key.replace(/\n/g, '\\n'));
```

Run:
```bash
node convert-key.js path/to/your-key.pem
```

Copy the output to your `.env` file.

## Step 7: Configure Your .env File

Edit `github-app/.env`:

```env
# GitHub App Configuration
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n...\n-----END RSA PRIVATE KEY-----
GITHUB_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# Backend API
BACKEND_API_URL=http://localhost:8000

# Server
PORT=3000
NODE_ENV=development
```

**Replace**:
- `123456` with your actual App ID
- The private key with your converted key (single line with `\n`)
- `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6` with your webhook secret

## Step 8: Set Up Webhook URL (Local Development)

For local testing, you need to expose your local server:

### Using ngrok (Recommended)

1. **Install ngrok**:
   ```bash
   # Download from https://ngrok.com/download
   # Or use package manager
   ```

2. **Start your GitHub App**:
   ```bash
   cd github-app
   npm start
   ```

3. **Start ngrok**:
   ```bash
   ngrok http 3000
   ```

4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

5. **Update GitHub App webhook URL**:
   - Go back to your GitHub App settings
   - Edit the app
   - Set Webhook URL to: `https://abc123.ngrok.io/webhook`
   - Save changes

**Note**: ngrok URLs change each time you restart (free tier). For production, use a permanent domain.

## Step 9: Install the GitHub App

1. **Go to your GitHub App page**:
   - https://github.com/settings/apps
   - Click on your app name

2. **Click "Install App"** (top right)

3. **Choose installation target**:
   - **Only select repositories**: Choose specific repos (recommended for testing)
   - **All repositories**: Install on all repos (use with caution)

4. **Click "Install"**

5. **Grant permissions** if prompted

## Step 10: Test the Integration

1. **Start your backend**:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn backend.main:app --reload
   ```

2. **Start your GitHub App**:
   ```bash
   cd github-app
   npm start
   ```

3. **Start ngrok** (if testing locally):
   ```bash
   ngrok http 3000
   ```

4. **Create a test PR**:
   - Create a new branch
   - Add some code with a security issue (e.g., hardcoded API key)
   - Open a pull request

5. **Check the results**:
   - The app should automatically scan the PR
   - You should see comments on the PR
   - Check backend logs for scan activity
   - Check GitHub App logs for webhook events

## Step 11: Verify Webhook Delivery

1. **Go to your GitHub App settings**
2. **Click "Advanced"** in the sidebar
3. **Click "Recent Deliveries"**
4. You should see webhook events listed
5. Click on an event to see:
   - Request payload
   - Response status
   - Delivery status

**Green checkmark** = Success
**Red X** = Failed (check your webhook URL and secret)

## Troubleshooting

### Webhook Not Receiving Events

1. **Check webhook URL is accessible**:
   ```bash
   curl https://your-webhook-url.com/webhook
   ```

2. **Verify webhook secret matches**:
   - Check `GITHUB_WEBHOOK_SECRET` in `.env`
   - Must match the secret in GitHub App settings

3. **Check GitHub App logs**:
   - Look for webhook events in console
   - Check for error messages

4. **Verify ngrok is running** (if using):
   - ngrok must be running while testing
   - URL changes on restart

### "Installation not found" Error

- Make sure you've installed the app on the repository
- Check that the repository owner matches the installation

### "Bad credentials" Error

- Verify `GITHUB_APP_ID` is correct
- Verify `GITHUB_APP_PRIVATE_KEY` is properly formatted (single line with `\n`)
- Check that the private key file wasn't corrupted

### PR Comments Not Appearing

1. **Check backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check backend logs** for scan errors

3. **Verify permissions**:
   - App needs "Read and write" on Pull requests
   - App needs "Write" on Issues

4. **Check GitHub App logs** for API errors

## Production Deployment

For production:

1. **Deploy GitHub App** to a cloud platform:
   - AWS, Azure, GCP, Heroku, etc.
   - Use a permanent domain (not ngrok)

2. **Update webhook URL** in GitHub App settings:
   - Set to your production URL: `https://your-domain.com/webhook`

3. **Use environment variables**:
   - Don't commit `.env` files
   - Use platform-specific secret management

4. **Set up monitoring**:
   - Monitor webhook deliveries
   - Set up alerts for failures
   - Log all scan activities

## Security Best Practices

1. **Never commit**:
   - `.env` files
   - Private key files (`.pem`)
   - Webhook secrets

2. **Rotate secrets regularly**:
   - Generate new webhook secrets periodically
   - Regenerate private keys if compromised

3. **Limit repository access**:
   - Only install on repositories that need scanning
   - Use "Only select repositories" option

4. **Monitor app activity**:
   - Review webhook deliveries regularly
   - Check for unauthorized access

## Next Steps

Once your GitHub App is set up:

1. ✅ Test with a sample PR
2. ✅ Configure policies for your repositories
3. ✅ Set up rule packs as needed
4. ✅ Monitor scan results
5. ✅ Adjust enforcement modes based on your needs

Your GitHub App is now ready to scan pull requests and commits automatically!
