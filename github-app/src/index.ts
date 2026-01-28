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
  
  // Trim whitespace
  key = key.trim();
  
  // If key contains literal \n (escaped newlines), convert to actual newlines
  // This is the format Render.com needs: single line with \n
  if (key.includes('\\n')) {
    // Replace \\n with actual newlines
    const formatted = key.replace(/\\n/g, '\n');
    console.log('[Config] Private key formatted from escaped \\n format');
    return formatted;
  }
  
  // If key contains actual newlines (multi-line format)
  // This might happen if Render.com preserves newlines
  if (key.includes('\n') && key.split('\n').length > 1) {
    // Check if it's a complete key (has BEGIN and END)
    if (key.includes('BEGIN') && key.includes('END')) {
      console.log('[Config] Private key detected in multi-line format');
      return key;
    }
  }
  
  // If key is on a single line but looks incomplete (only has BEGIN line)
  // This is the error we're seeing - Render.com only read the first line
  if (key.startsWith('-----BEGIN') && !key.includes('\\n') && !key.includes('\n') && key.length < 100) {
    throw new Error(
      'Private key appears incomplete. Render.com may have only read the first line.\n' +
      'Please format the key as a SINGLE LINE with \\n for newlines in Render.com environment variables.\n' +
      'Example: -----BEGIN RSA PRIVATE KEY-----\\nMIIE...\\n-----END RSA PRIVATE KEY-----'
    );
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
