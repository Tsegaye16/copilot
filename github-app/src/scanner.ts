/**
 * Scanner integration with backend API
 */
import axios from 'axios';
import { App } from '@octokit/app';
import { getPRFiles, getCommitFiles } from './github-client';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

export async function scanPullRequest(
  repository: string,
  prNumber: number,
  app: App
): Promise<any> {
  try {
    // Get PR files
    const files = await getPRFiles(repository, prNumber, app);
    
    // Prepare scan request
    const scanRequest = {
      repository,
      pull_request_number: prNumber,
      files: files.map((file: any) => ({
        path: file.filename,
        content: file.patch || file.contents || '',
        metadata: {
          additions: file.additions,
          deletions: file.deletions,
          changes: file.changes,
          status: file.status
        }
      })),
      detect_copilot: true
    };

    // Call backend API
    const response = await axios.post(
      `${BACKEND_API_URL}/api/v1/scan/`,
      scanRequest,
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 300000 // 5 minutes
      }
    );

    return response.data;
  } catch (error: any) {
    console.error('Scan failed:', error);
    throw error;
  }
}

export async function scanCommit(
  repository: string,
  commitSha: string,
  app: App
): Promise<any> {
  try {
    // Get commit files
    const files = await getCommitFiles(repository, commitSha, app);
    
    // Prepare scan request
    const scanRequest = {
      repository,
      commit_sha: commitSha,
      files: files.map((file: any) => ({
        path: file.filename,
        content: file.patch || file.contents || '',
        metadata: {
          additions: file.additions,
          deletions: file.deletions,
          changes: file.changes
        }
      })),
      detect_copilot: true
    };

    // Call backend API
    const response = await axios.post(
      `${BACKEND_API_URL}/api/v1/scan/`,
      scanRequest,
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 300000
      }
    );

    return response.data;
  } catch (error: any) {
    console.error('Scan failed:', error);
    throw error;
  }
}
