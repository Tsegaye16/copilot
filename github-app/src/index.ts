/**
 * GitHub App for Enterprise Copilot Guardrails
 */
import express, { Request, Response } from 'express';
import { App } from '@octokit/app';
import dotenv from 'dotenv';
import { handleWebhook } from './webhooks';

dotenv.config();

const app = express();

// Initialize GitHub App first (before body parsing for webhook signature verification)
const githubApp = new App({
  appId: process.env.GITHUB_APP_ID!,
  privateKey: process.env.GITHUB_APP_PRIVATE_KEY!,
  webhooks: {
    secret: process.env.GITHUB_WEBHOOK_SECRET!
  }
});

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

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'healthy' });
});

// Note: We don't use createNodeMiddleware because we handle webhooks directly
// and use installation-based authentication, not OAuth

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`GitHub App server running on port ${PORT}`);
});

export { app, githubApp };
