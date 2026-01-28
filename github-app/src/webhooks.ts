/**
 * GitHub webhook handlers
 */
import { Request, Response } from 'express';
import { App } from '@octokit/app';
import { createHmac } from 'crypto';
import { scanPullRequest, scanCommit } from './scanner';
import { postPRComments, getInstallationOctokit } from './github-client';

export async function handleWebhook(
  req: Request,
  res: Response,
  app: App
): Promise<void> {
  const event = req.headers['x-github-event'] as string;
  const deliveryId = req.headers['x-github-delivery'] as string;
  const signature = req.headers['x-hub-signature-256'] as string;

  console.log(`[Webhook] Received: ${event} (${deliveryId})`);
  console.log(`[Webhook] Event type: ${event}`);
  console.log(`[Webhook] Has signature: ${!!signature}`);

  // Verify webhook signature if secret is set
  const webhookSecret = process.env.GITHUB_WEBHOOK_SECRET;
  if (webhookSecret && signature) {
    try {
      // Get raw body for signature verification
      const rawBody = JSON.stringify(req.body);
      const expectedSignature = 'sha256=' + createHmac('sha256', webhookSecret)
        .update(rawBody)
        .digest('hex');
      
      if (signature !== expectedSignature) {
        console.error('[Webhook] Signature verification failed');
        console.error(`[Webhook] Expected: ${expectedSignature.substring(0, 20)}...`);
        console.error(`[Webhook] Received: ${signature.substring(0, 20)}...`);
        res.status(401).json({ error: 'Unauthorized: Invalid signature' });
        return;
      }
      console.log('[Webhook] Signature verified successfully');
    } catch (sigError: any) {
      console.error('[Webhook] Signature verification error:', sigError?.message);
      res.status(401).json({ error: 'Unauthorized: Signature verification failed' });
      return;
    }
  } else if (webhookSecret && !signature) {
    console.warn('[Webhook] Warning: Webhook secret configured but no signature received');
  }

  try {
    switch (event) {
      case 'pull_request':
        console.log('[Webhook] Handling pull_request event');
        await handlePullRequest(req.body, app);
        break;
      case 'push':
        console.log('[Webhook] Handling push event');
        await handlePush(req.body, app);
        break;
      case 'pull_request_review':
        console.log('[Webhook] Handling pull_request_review event');
        await handlePullRequestReview(req.body, app);
        break;
      default:
        console.log(`[Webhook] Unhandled event type: ${event}`);
    }

    res.status(200).json({ status: 'ok', event });
  } catch (error: any) {
    console.error('[Webhook] Handling error:', error);
    console.error('[Webhook] Error stack:', error?.stack);
    console.error('[Webhook] Error message:', error?.message);
    // Still return 200 to GitHub so it doesn't retry, but log the error
    res.status(200).json({ status: 'error', error: error?.message });
  }
}

async function handlePullRequest(payload: any, app: App): Promise<void> {
  const action = payload.action;
  const pr = payload.pull_request;
  const repo = payload.repository;

  console.log(`[PR] Event action: ${action}`);
  console.log(`[PR] PR number: ${pr?.number}`);
  console.log(`[PR] Repository: ${repo?.full_name}`);

  if (!pr || !repo) {
    console.error('[PR] Invalid payload: missing pr or repo');
    console.error('[PR] PR:', !!pr);
    console.error('[PR] Repo:', !!repo);
    return;
  }

  // Process PR events - handle all actions that might need scanning
  const actionsToProcess = ['opened', 'synchronize', 'reopened', 'ready_for_review'];
  
  if (actionsToProcess.includes(action)) {
    console.log(`[PR] Processing PR #${pr.number} in ${repo.full_name} (action: ${action})`);
    
    try {
      const result = await scanPullRequest(
        repo.full_name,
        pr.number,
        app
      );

      if (!result) {
        console.error(`[PR] Scan returned no result for PR #${pr.number}`);
        // Try to post a comment about the failure
        try {
          const octokit = await getInstallationOctokit(repo.owner.login, repo.name, app);
          await octokit.rest.issues.createComment({
            owner: repo.owner.login,
            repo: repo.name,
            issue_number: pr.number,
            body: '⚠️ **Guardrails Scan Failed**\n\nUnable to scan this PR. Please check the logs for details.'
          });
        } catch (e) {
          console.error(`[PR] Failed to post error comment:`, e);
        }
        return;
      }

      // Check if scan had an error (e.g., backend unavailable)
      if (result.error) {
        console.warn(`[PR] Scan completed with error: ${result.error_message || 'Unknown error'}`);
        console.warn(`[PR] Error details:`, result.error_details);
        console.log(`[PR] Violations: ${result.violations?.length || 0} (error state - backend unavailable)`);
        console.log(`[PR] Can merge: ${result.can_merge} (advisory mode due to error)`);
        console.log(`[PR] Enforcement: ${result.enforcement_action}`);
      } else {
        console.log(`[PR] Scan completed successfully`);
        console.log(`[PR] Violations: ${result.violations?.length || 0}`);
        console.log(`[PR] Can merge: ${result.can_merge}`);
        console.log(`[PR] Enforcement: ${result.enforcement_action}`);
      }

      // Always post results, even if no violations
      console.log(`[PR] Posting comments to PR #${pr.number}`);
      try {
        await postPRComments(
          repo.owner.login,
          repo.name,
          pr.number,
          result,
          app
        );
        console.log(`[PR] Successfully posted comments to PR #${pr.number}`);
      } catch (commentError: any) {
        console.error(`[PR] Failed to post comments:`, commentError?.message || commentError);
        console.error(`[PR] Comment error stack:`, commentError?.stack);
        console.error(`[PR] Comment error response:`, commentError?.response?.data);
        console.error(`[PR] Comment error status:`, commentError?.response?.status);
        
        // Try to at least set commit status
        try {
          const octokit = await getInstallationOctokit(
            repo.owner.login,
            repo.name,
            app
          );
          // Determine status based on result
          let state: 'success' | 'failure' | 'error' = result.error 
            ? 'error' 
            : (result.can_merge ? 'success' : 'failure');
          const description = result.error 
            ? (result.error_message || 'Backend unavailable')
            : `Scan completed: ${result.violations?.length || 0} violations`;
          
          await octokit.rest.repos.createCommitStatus({
            owner: repo.owner.login,
            repo: repo.name,
            sha: pr.head.sha,
            state,
            description,
            context: 'guardrails/security-scan'
          });
          console.log(`[PR] Set commit status as fallback`);
        } catch (statusError: any) {
          console.error(`[PR] Failed to set commit status:`, statusError?.message || statusError);
          console.error(`[PR] Status error:`, statusError?.response?.data);
        }
      }
    } catch (error: any) {
      console.error(`[PR] Error processing PR #${pr.number}:`, error?.message || error);
      console.error(`[PR] Error stack:`, error?.stack);
      console.error(`[PR] Error code:`, error?.code);
      console.error(`[PR] Error response:`, error?.response?.data);
      console.error(`[PR] Error response status:`, error?.response?.status);
      
      // Try to post error comment
      try {
        const octokit = await getInstallationOctokit(repo.owner.login, repo.name, app);
        await octokit.rest.issues.createComment({
          owner: repo.owner.login,
          repo: repo.name,
          issue_number: pr.number,
          body: `❌ **Guardrails Scan Error**\n\nError: ${error?.message || 'Unknown error'}\n\nPlease check the service logs.`
        });
      } catch (e) {
        console.error(`[PR] Failed to post error comment:`, e);
      }
    }
  } else {
    console.log(`[PR] Skipping action ${action} (only processing: ${actionsToProcess.join(', ')})`);
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
  try {
    // Get authenticated octokit for this installation
    const octokit = await getInstallationOctokit(owner, repo, app);

    // Handle error states (e.g., backend unavailable)
    let state: 'success' | 'failure' | 'error';
    let description: string;
    
    if (result.error) {
      state = 'error';
      description = result.error_message || 'Backend unavailable';
    } else if (result.can_merge) {
      state = 'success';
      description = 'All checks passed';
    } else {
      state = 'failure';
      description = `${result.violations?.length || 0} violations found`;
    }

    await octokit.rest.repos.createCommitStatus({
      owner,
      repo,
      sha,
      state,
      description,
      context: 'guardrails/security-scan'
    });
    
    console.log(`[CommitStatus] Set status to ${state}: ${description}`);
  } catch (error: any) {
    console.error(`[CommitStatus] Failed to set status for ${sha}:`, error?.message || error);
    throw error;
  }
}
