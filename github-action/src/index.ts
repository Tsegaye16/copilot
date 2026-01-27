/**
 * GitHub Action for Enterprise Copilot Guardrails
 */
import * as core from '@actions/core';
import * as github from '@actions/github';
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';

async function run(): Promise<void> {
  try {
    const backendUrl = core.getInput('backend_url') || 'http://localhost:8000';
    const apiKey = core.getInput('api_key');
    const policyConfigInput = core.getInput('policy_config');
    const detectCopilot = core.getInput('detect_copilot') !== 'false';

    const context = github.context;
    const repo = context.repo;

    // Get changed files
    const changedFiles = await getChangedFiles(context);

    // Prepare scan request
    const scanRequest = {
      repository: `${repo.owner}/${repo.repo}`,
      pull_request_number: context.payload.pull_request?.number,
      commit_sha: context.sha,
      files: changedFiles,
      detect_copilot: detectCopilot,
      policy_config: policyConfigInput ? JSON.parse(policyConfigInput) : undefined
    };

    // Call backend API
    const headers: any = { 'Content-Type': 'application/json' };
    if (apiKey) {
      headers['Authorization'] = `Bearer ${apiKey}`;
    }

    core.info(`Scanning ${changedFiles.length} files...`);
    const response = await axios.post(
      `${backendUrl}/api/v1/scan/`,
      scanRequest,
      { headers, timeout: 300000 }
    );

    const result = response.data;

    // Set outputs
    core.setOutput('scan_id', result.scan_id);
    core.setOutput('violations_count', result.violations.length);
    core.setOutput('can_merge', result.can_merge);

    // Post summary
    core.summary
      .addHeading('Guardrails Scan Results')
      .addTable([
        [
          { data: 'Metric', header: true },
          { data: 'Value', header: true }
        ],
        ['Total Violations', result.violations.length.toString()],
        ['Critical', result.summary.by_severity.critical.toString()],
        ['High', result.summary.by_severity.high.toString()],
        ['Medium', result.summary.by_severity.medium.toString()],
        ['Low', result.summary.by_severity.low.toString()],
        ['Can Merge', result.can_merge ? 'Yes' : 'No'],
        ['Copilot Detected', result.copilot_detected ? 'Yes' : 'No']
      ])
      .write();

    // Fail if blocking and cannot merge
    if (!result.can_merge && result.enforcement_action === 'blocking') {
      core.setFailed(`Scan failed: ${result.violations.length} violations found (blocking mode)`);
    }

    core.info(`Scan completed: ${result.violations.length} violations found`);
  } catch (error: any) {
    core.setFailed(`Action failed: ${error.message}`);
  }
}

async function getChangedFiles(context: any): Promise<any[]> {
  const files: any[] = [];

  if (context.eventName === 'pull_request') {
    const octokit = github.getOctokit(process.env.GITHUB_TOKEN!);
    const { data: prFiles } = await octokit.rest.pulls.listFiles({
      owner: context.repo.owner,
      repo: context.repo.repo,
      pull_number: context.payload.pull_request.number
    });

    for (const file of prFiles) {
      if (file.status === 'removed') continue;

      try {
        const { data: content } = await octokit.rest.repos.getContent({
          owner: context.repo.owner,
          repo: context.repo.repo,
          path: file.filename,
          ref: context.payload.pull_request.head.sha
        });

        if ('content' in content && content.encoding === 'base64') {
          files.push({
            path: file.filename,
            content: Buffer.from(content.content, 'base64').toString('utf-8'),
            metadata: {
              additions: file.additions,
              deletions: file.deletions,
              changes: file.changes,
              status: file.status
            }
          });
        }
      } catch (error) {
        core.warning(`Failed to fetch content for ${file.filename}`);
      }
    }
  } else {
    // For push events, get files from the commit
    const octokit = github.getOctokit(process.env.GITHUB_TOKEN!);
    const { data: commit } = await octokit.rest.repos.getCommit({
      owner: context.repo.owner,
      repo: context.repo.repo,
      ref: context.sha
    });

    for (const file of commit.files || []) {
      if (file.status === 'removed') continue;

      files.push({
        path: file.filename,
        content: '', // Would need to fetch separately
        metadata: {
          additions: file.additions,
          deletions: file.deletions,
          changes: file.changes
        }
      });
    }
  }

  return files;
}

run();
