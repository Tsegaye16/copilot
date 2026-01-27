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
    // Get raw body for signature verification
    const rawBody = JSON.stringify(req.body);
    const expectedSignature = 'sha256=' + createHmac('sha256', webhookSecret)
      .update(rawBody)
      .digest('hex');
    
    if (signature !== expectedSignature) {
      console.error('Webhook signature verification failed');
      console.error(`Expected: ${expectedSignature.substring(0, 20)}...`);
      console.error(`Received: ${signature.substring(0, 20)}...`);
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
  } catch (error: any) {
    console.error('Webhook handling error:', error);
    console.error('Error stack:', error?.stack);
    console.error('Error message:', error?.message);
    // Still return 200 to GitHub so it doesn't retry
    res.status(200).send('OK');
  }
}

async function handlePullRequest(payload: any, app: App): Promise<void> {
  const action = payload.action;
  const pr = payload.pull_request;
  const repo = payload.repository;

  if (action === 'opened' || action === 'synchronize' || action === 'reopened') {
    console.log(`[PR] Scanning PR #${pr.number} in ${repo.full_name}`);
    
    try {
      const result = await scanPullRequest(
        repo.full_name,
        pr.number,
        app
      );

      console.log(`[PR] Scan completed: ${result.violations?.length || 0} violations`);
      console.log(`[PR] Can merge: ${result.can_merge}`);

      // Post results as PR comments
      console.log(`[PR] Posting comments to PR #${pr.number}`);
      await postPRComments(
        repo.owner.login,
        repo.name,
        pr.number,
        result,
        app
      );
      console.log(`[PR] Successfully posted comments to PR #${pr.number}`);
    } catch (error: any) {
      console.error(`[PR] Error processing PR #${pr.number}:`, error?.message || error);
      console.error(`[PR] Error stack:`, error?.stack);
      // Don't throw - log and continue
    }
  }
}

async function handlePush(payload: any, app: App): Promise<void> {
  const commits = payload.commits || [];
  const repo = payload.repository;

  console.log(`[Push] Processing ${commits.length} commits in ${repo.full_name}`);

  // Only scan if there are commits and they're not empty
  if (commits.length === 0) {
    console.log('[Push] No commits to scan');
    return;
  }

  for (const commit of commits) {
    try {
      console.log(`[Push] Scanning commit ${commit.id} in ${repo.full_name}`);
      
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
    } catch (error: any) {
      console.error(`[Push] Error scanning commit ${commit.id}:`, error);
      // Continue with next commit
    }
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
