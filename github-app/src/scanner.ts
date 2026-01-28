/**
 * Scanner integration with backend API
 */
import axios from 'axios';
import { App } from '@octokit/app';
import { getPRFiles, getCommitFiles } from './github-client';

// Get backend URL and ensure it has protocol and correct domain
function getBackendUrl(): string {
  let url = process.env.BACKEND_API_URL || 'http://localhost:8000';
  
  // Trim whitespace
  url = url.trim();
  
  // If URL doesn't start with http:// or https://, add https://
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    console.warn(`[Scanner] Backend URL missing protocol, adding https://: ${url}`);
    url = `https://${url}`;
  }
  
  // If URL is just "guardrails-backend" or similar, add .onrender.com
  if (url === 'https://guardrails-backend' || url === 'http://guardrails-backend') {
    console.warn(`[Scanner] Backend URL incomplete, adding .onrender.com: ${url}`);
    url = 'https://guardrails-backend.onrender.com';
  }
  
  // Ensure it ends with .onrender.com if it's a render service
  if (url.includes('guardrails-backend') && !url.includes('.onrender.com')) {
    url = url.replace(/guardrails-backend.*$/, 'guardrails-backend.onrender.com');
    // Ensure https://
    if (!url.startsWith('https://')) {
      url = url.replace(/^http:\/\//, 'https://');
    }
    console.warn(`[Scanner] Backend URL corrected to: ${url}`);
  }
  
  return url;
}

const BACKEND_API_URL = getBackendUrl();

// Helper function to check backend health
async function checkBackendHealth(): Promise<boolean> {
  try {
    const healthUrl = `${BACKEND_API_URL}/health`;
    console.log(`[Scanner] Checking backend health at: ${healthUrl}`);
    const response = await axios.get(healthUrl, { timeout: 10000 });
    console.log(`[Scanner] Backend health check: ${response.status} ${response.statusText}`);
    return response.status === 200;
  } catch (error: any) {
    console.warn(`[Scanner] Backend health check failed: ${error?.message || error}`);
    return false;
  }
}

// Helper function to call backend API with retry logic
async function callBackendAPI(endpoint: string, data: any, retries = 3): Promise<any> {
  const endpoints = [
    `${BACKEND_API_URL}${endpoint}`,
    `${BACKEND_API_URL}${endpoint.replace(/\/$/, '')}`, // Try without trailing slash
    `${BACKEND_API_URL}/api/v1/scan`, // Try alternative endpoint
  ];

  for (let attempt = 0; attempt < retries; attempt++) {
    for (const url of endpoints) {
      try {
        console.log(`[Scanner] Attempt ${attempt + 1}/${retries}: POST ${url}`);
        const response = await axios.post(
          url,
          data,
          {
            headers: { 'Content-Type': 'application/json' },
            timeout: 300000, // 5 minutes
            validateStatus: (status) => status < 500 // Don't throw on 4xx errors
          }
        );

        if (response.status === 200 || response.status === 201) {
          console.log(`[Scanner] Success: ${response.status} ${response.statusText}`);
          return response.data;
        }

        if (response.status >= 400 && response.status < 500) {
          // Client error - don't retry
          console.error(`[Scanner] Client error ${response.status}: ${JSON.stringify(response.data)}`);
          throw new Error(`Backend returned ${response.status}: ${JSON.stringify(response.data)}`);
        }

        // Server error - will retry
        console.warn(`[Scanner] Server error ${response.status}, will retry...`);
      } catch (error: any) {
        const isLastAttempt = attempt === retries - 1;
        const isLastEndpoint = url === endpoints[endpoints.length - 1];

        if (error.response) {
          // HTTP error response
          const status = error.response.status;
          if (status >= 400 && status < 500) {
            // Client error - don't retry
            throw error;
          }
          // Server error (5xx) - retry
          console.warn(`[Scanner] HTTP ${status} error, ${isLastAttempt && isLastEndpoint ? 'giving up' : 'retrying...'}`);
        } else if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND' || error.code === 'ETIMEDOUT') {
          console.warn(`[Scanner] Connection error (${error.code}), ${isLastAttempt && isLastEndpoint ? 'giving up' : 'retrying...'}`);
        } else {
          console.warn(`[Scanner] Error: ${error?.message || error}, ${isLastAttempt && isLastEndpoint ? 'giving up' : 'retrying...'}`);
        }

        if (isLastAttempt && isLastEndpoint) {
          throw error;
        }

        // Wait before retry (exponential backoff)
        if (!isLastAttempt || !isLastEndpoint) {
          const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
          console.log(`[Scanner] Waiting ${delay}ms before retry...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
  }

  throw new Error('All retry attempts failed');
}

export async function scanPullRequest(
  repository: string,
  prNumber: number,
  app: App
): Promise<any> {
  const startTime = Date.now();
  try {
    console.log(`[Scanner] Starting scan for PR #${prNumber} in ${repository}`);
    console.log(`[Scanner] Backend URL: ${BACKEND_API_URL}`);
    
    // Check backend health first
    const isHealthy = await checkBackendHealth();
    if (!isHealthy) {
      console.warn('[Scanner] Backend health check failed, but proceeding with scan attempt...');
    }
    
    // Get PR files
    console.log(`[Scanner] Fetching PR files...`);
    const files = await getPRFiles(repository, prNumber, app);
    console.log(`[Scanner] Found ${files.length} files in PR`);
    
    if (files.length === 0) {
      console.warn(`[Scanner] No files found in PR #${prNumber}`);
      return {
        scan_id: 'no-files',
        repository,
        violations: [],
        summary: { 
          total_violations: 0,
          by_severity: { critical: 0, high: 0, medium: 0, low: 0 },
          by_category: {},
          copilot_violations: 0,
          files_affected: 0
        },
        enforcement_action: 'advisory',
        can_merge: true,
        copilot_detected: false,
        processing_time_ms: Date.now() - startTime
      };
    }
    
    // Prepare scan request
    const scanRequest = {
      repository,
      pull_request_number: prNumber,
      files: files
        .filter((file: any) => file.filename && file.status !== 'removed')
        .map((file: any) => ({
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

    console.log(`[Scanner] Sending scan request for ${scanRequest.files.length} files`);
    console.log(`[Scanner] Files: ${scanRequest.files.map((f: any) => f.path).join(', ')}`);

    // Call backend API with retry logic
    const responseData = await callBackendAPI('/api/v1/scan/', scanRequest);

    console.log(`[Scanner] Scan completed: ${responseData.violations?.length || 0} violations`);
    return {
      ...responseData,
      processing_time_ms: Date.now() - startTime
    };
  } catch (error: any) {
    const processingTime = Date.now() - startTime;
    console.error('[Scanner] Scan failed:', error?.message || error);
    console.error('[Scanner] Error code:', error?.code);
    console.error('[Scanner] Error status:', error?.response?.status);
    console.error('[Scanner] Error response:', error?.response?.data ? JSON.stringify(error?.response?.data).substring(0, 500) : 'No response data');
    console.error('[Scanner] Backend URL was:', BACKEND_API_URL);
    
    // Return a graceful fallback response instead of throwing
    // This allows the PR to still get a comment explaining the issue
    return {
      scan_id: `error-${Date.now()}`,
      repository,
      violations: [],
      summary: { 
        total_violations: 0,
        by_severity: { critical: 0, high: 0, medium: 0, low: 0 },
        by_category: {},
        copilot_violations: 0,
        files_affected: 0
      },
      enforcement_action: 'advisory',
      can_merge: true,
      copilot_detected: false,
      processing_time_ms: processingTime,
      error: true,
      error_message: error?.response?.status === 502 
        ? 'Backend service unavailable (502). The guardrails backend may be starting up or experiencing issues. Please try again in a few moments.'
        : error?.message || 'Scan failed due to backend error',
      error_details: {
        status: error?.response?.status,
        code: error?.code,
        url: BACKEND_API_URL
      }
    };
  }
}

export async function scanCommit(
  repository: string,
  commitSha: string,
  app: App
): Promise<any> {
  const startTime = Date.now();
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
        processing_time_ms: Date.now() - startTime
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
    
    // Call backend API with retry logic
    const responseData = await callBackendAPI('/api/v1/scan/', scanRequest);

    console.log(`[Scanner] Scan completed: ${responseData.violations?.length || 0} violations`);
    return {
      ...responseData,
      processing_time_ms: Date.now() - startTime
    };
  } catch (error: any) {
    const processingTime = Date.now() - startTime;
    console.error('[Scanner] Scan failed:', error?.message || error);
    console.error('[Scanner] Error details:', error?.response?.data || error);
    // Return a safe default instead of throwing
    return {
      scan_id: `error-${Date.now()}`,
      repository,
      violations: [],
      summary: { total_violations: 0 },
      enforcement_action: 'advisory',
      can_merge: true,
      copilot_detected: false,
      processing_time_ms: processingTime,
      error: true,
      error_message: error?.response?.status === 502 
        ? 'Backend service unavailable (502). The guardrails backend may be starting up or experiencing issues.'
        : error?.message || 'Scan failed'
    };
  }
}
