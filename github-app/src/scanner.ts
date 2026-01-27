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
    console.log(`[Scanner] Fetching commit files for ${commitSha}`);
    // Get commit files
    const files = await getCommitFiles(repository, commitSha, app);
    
    console.log(`[Scanner] Found ${files.length} files in commit`);
    
    if (files.length === 0) {
      console.log('[Scanner] No files to scan');
      return {
        scan_id: 'no-files',
        repository,
        violations: [],
        summary: { total_violations: 0 },
        enforcement_action: 'advisory',
        can_merge: true,
        copilot_detected: false,
        processing_time_ms: 0
      };
    }
    
    // Prepare scan request
    const scanRequest = {
      repository,
      commit_sha: commitSha,
      files: files
        .filter((file: any) => file.filename && file.status !== 'removed')
        .map((file: any) => ({
        path: file.filename,
        content: file.patch || file.contents || '',
        metadata: {
          additions: file.additions || 0,
          deletions: file.deletions || 0,
          changes: file.changes || 0
        }
      })),
      detect_copilot: true
    };

    console.log(`[Scanner] Sending scan request for ${scanRequest.files.length} files`);
    
    // Call backend API
    const response = await axios.post(
      `${BACKEND_API_URL}/api/v1/scan/`,
      scanRequest,
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: 300000
      }
    );

    console.log(`[Scanner] Scan completed: ${response.data.violations?.length || 0} violations`);
    return response.data;
  } catch (error: any) {
    console.error('[Scanner] Scan failed:', error?.message || error);
    console.error('[Scanner] Error details:', error?.response?.data || error);
    // Return a safe default instead of throwing
    return {
      scan_id: 'error',
      repository,
      violations: [],
      summary: { total_violations: 0 },
      enforcement_action: 'advisory',
      can_merge: true,
      copilot_detected: false,
      processing_time_ms: 0,
      error: error?.message || 'Scan failed'
    };
  }
}
