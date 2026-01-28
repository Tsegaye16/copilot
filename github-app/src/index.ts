/**
 * GitHub App for Enterprise Copilot Guardrails
 */
import express, { Request, Response } from 'express';
import { App } from '@octokit/app';
import dotenv from 'dotenv';
import { handleWebhook } from './webhooks';

dotenv.config();

const app = express();

// Helper function to format private key (handles both single-line and multi-line formats)
function formatPrivateKey(key: string | undefined): string {
  if (!key) {
    throw new Error('GITHUB_APP_PRIVATE_KEY is not set');
  }
  
  // If key already contains literal \n (escaped), convert to actual newlines
  if (key.includes('\\n') && !key.includes('\n')) {
    // Key is stored as single line with \n escape sequences
    return key.replace(/\\n/g, '\n');
  }
  
  // If key contains actual newlines (multi-line format from environment)
  // This happens when Render.com preserves newlines in the env var
  if (key.includes('\n') && key.split('\n').length > 1) {
    // Key is already in correct format with actual newlines
    // Just return it as-is (Octokit can handle this)
    return key;
  }
  
  // If it's a single line without newlines, it might be missing them
  // Check if it looks like a private key
  if (key.includes('BEGIN') && key.includes('END') && !key.includes('\n')) {
    console.warn('Private key appears to be on a single line without newlines. This may cause issues.');
    console.warn('Please format the key with \\n for newlines in Render.com environment variables.');
  }
  
  return key;
}

// Initialize GitHub App first (before body parsing for webhook signature verification)
let githubApp: App;
try {
  const privateKey = formatPrivateKey(process.env.GITHUB_APP_PRIVATE_KEY);
  
  githubApp = new App({
    appId: process.env.GITHUB_APP_ID!,
    privateKey: privateKey,
    webhooks: {
      secret: process.env.GITHUB_WEBHOOK_SECRET!
    }
  });
  
  console.log('GitHub App initialized successfully');
} catch (error: any) {
  console.error('Failed to initialize GitHub App:', error?.message);
  console.error('Make sure GITHUB_APP_PRIVATE_KEY is set correctly in environment variables');
  console.error('The key should be on a single line with \\n for newlines');
  throw error;
}

// Parse JSON body (after app initialization)
app.use(express.json());

// Root endpoint for testing
app.get('/', (req: Request, res: Response) => {
  res.json({ 
    status: 'ok', 
    service: 'github-app',
    endpoints: ['/health', '/webhook']
  });
});

// Webhook endpoint
app.post('/webhook', async (req: Request, res: Response) => {
  console.log('Webhook received at /webhook');
  await handleWebhook(req, res, githubApp);
});

// Manual trigger endpoint for testing (POST /trigger/:owner/:repo/:pr)
app.post('/trigger/:owner/:repo/:pr', async (req: Request, res: Response) => {
  try {
    const { owner, repo, pr } = req.params;
    const prNumber = parseInt(pr);
    
    console.log(`[Manual] Triggering scan for ${owner}/${repo} PR #${prNumber}`);
    
    const { scanPullRequest } = await import('./scanner');
    const { postPRComments } = await import('./github-client');
    
    const result = await scanPullRequest(`${owner}/${repo}`, prNumber, githubApp);
    
    if (result) {
      await postPRComments(owner, repo, prNumber, result, githubApp);
      res.json({ status: 'success', result });
    } else {
      res.status(500).json({ status: 'error', message: 'Scan returned no result' });
    }
  } catch (error: any) {
    console.error('[Manual] Trigger error:', error);
    res.status(500).json({ status: 'error', error: error?.message });
  }
});

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ 
    status: 'healthy',
    backend_url: process.env.BACKEND_API_URL || 'not set',
    github_app_id: process.env.GITHUB_APP_ID ? 'set' : 'not set'
  });
});

// Note: We don't use createNodeMiddleware because we handle webhooks directly
// and use installation-based authentication, not OAuth

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`GitHub App server running on port ${PORT}`);
});

export { app, githubApp };
