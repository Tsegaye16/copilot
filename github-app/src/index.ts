/**
 * GitHub App for Enterprise Copilot Guardrails
 */
import express, { Request, Response } from 'express';
import { App } from '@octokit/app';
import dotenv from 'dotenv';
import { handleWebhook } from './webhooks';

dotenv.config();

const app = express();
app.use(express.json());

// Initialize GitHub App
const githubApp = new App({
  appId: process.env.GITHUB_APP_ID!,
  privateKey: process.env.GITHUB_APP_PRIVATE_KEY!,
  webhooks: {
    secret: process.env.GITHUB_WEBHOOK_SECRET!
  }
});

// Webhook endpoint
app.post('/webhook', async (req: Request, res: Response) => {
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
