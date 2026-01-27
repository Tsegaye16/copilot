/**
 * GitHub webhook handlers
 */
import { Request, Response } from 'express';
import { App } from '@octokit/app';
import { createHmac } from 'crypto';
import { scanPullRequest, scanCommit } from './scanner';
import { postPRComments } from './github-client';

export async function handleWebhook(
  req: Request,
  res: Response,
  app: App
): Promise<void> {
  const event = req.headers['x-github-event'] as string;
  const deliveryId = req.headers['x-github-delivery'] as string;
  const signature = req.headers['x-hub-signature-256'] as string;

  console.log(`Received webhook: ${event} (${deliveryId})`);

  // Verify webhook signature if secret is set
  const webhookSecret = process.env.GITHUB_WEBHOOK_SECRET;
  if (webhookSecret && signature) {
    const expectedSignature = 'sha256=' + createHmac('sha256', webhookSecret)
      .update(JSON.stringify(req.body))
      .digest('hex');
    
    if (signature !== expectedSignature) {
      console.error('Webhook signature verification failed');
      res.status(401).send('Unauthorized');
      return;
    }
  }

  try {
    switch (event) {
      case 'pull_request':
        await handlePullRequest(req.body, app);
        break;
      case 'push':
        await handlePush(req.body, app);
        break;
      case 'pull_request_review':
        await handlePullRequestReview(req.body, app);
        break;
      default:
        console.log(`Unhandled event type: ${event}`);
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error('Webhook handling error:', error);
    res.status(500).send('Internal Server Error');
  }
}

async function handlePullRequest(payload: any, app: App): Promise<void> {
  const action = payload.action;
  const pr = payload.pull_request;
  const repo = payload.repository;

  if (action === 'opened' || action === 'synchronize' || action === 'reopened') {
    console.log(`Scanning PR #${pr.number} in ${repo.full_name}`);
    
    const result = await scanPullRequest(
      repo.full_name,
      pr.number,
      app
    );

    // Post results as PR comments
    await postPRComments(
      repo.owner.login,
      repo.name,
      pr.number,
      result,
      app
    );
  }
}

async function handlePush(payload: any, app: App): Promise<void> {
  const commits = payload.commits || [];
  const repo = payload.repository;

  for (const commit of commits) {
    console.log(`Scanning commit ${commit.id} in ${repo.full_name}`);
    
    const result = await scanCommit(
      repo.full_name,
      commit.id,
      app
    );

    // Post commit status check
    await postCommitStatus(
      repo.owner.login,
      repo.name,
      commit.id,
      result,
      app
    );
  }
}

async function handlePullRequestReview(payload: any, app: App): Promise<void> {
  // Handle review events if needed
  console.log('Pull request review event received');
}

async function postCommitStatus(
  owner: string,
  repo: string,
  sha: string,
  result: any,
  app: App
): Promise<void> {
  // Get installation ID for the repository using the app's octokit
  const { data: installation } = await app.octokit.request('GET /repos/{owner}/{repo}/installation', {
    owner,
    repo
  });
  
  // Get authenticated octokit for this installation
  const octokit: any = await app.getInstallationOctokit(installation.id);

  const state = result.can_merge ? 'success' : 'failure';
  const description = result.can_merge
    ? 'All checks passed'
    : `${result.violations.length} violations found`;

  await octokit.rest.repos.createCommitStatus({
    owner,
    repo,
    sha,
    state,
    description,
    context: 'guardrails/security-scan'
  });
}
