/**
 * GitHub API client utilities
 */
import { App } from '@octokit/app';

export async function getInstallationOctokit(
  owner: string,
  repo: string,
  app: App
): Promise<any> {
  // Get installation ID for the repository using the app's octokit
  const { data: installation } = await app.octokit.request('GET /repos/{owner}/{repo}/installation', {
    owner,
    repo
  });
  
  // Get authenticated octokit for this installation
  return await app.getInstallationOctokit(installation.id);
}

export async function getPRFiles(
  repository: string,
  prNumber: number,
  app: App
): Promise<any[]> {
  const [owner, repo] = repository.split('/');
  const octokit = await getInstallationOctokit(owner, repo, app);

  const { data: files } = await octokit.rest.pulls.listFiles({
    owner,
    repo,
    pull_number: prNumber
  });

  // Fetch full content for each file
  const filesWithContent = await Promise.all(
    files.map(async (file) => {
      if (file.status === 'removed') {
        return file;
      }

      try {
        const { data: content } = await octokit.rest.repos.getContent({
          owner,
          repo,
          path: file.filename,
          ref: file.sha
        });

        if ('content' in content && content.encoding === 'base64') {
          return {
            ...file,
            contents: Buffer.from(content.content, 'base64').toString('utf-8')
          };
        }
      } catch (error) {
        console.error(`Failed to fetch content for ${file.filename}:`, error);
      }

      return file;
    })
  );

  return filesWithContent;
}

export async function getCommitFiles(
  repository: string,
  commitSha: string,
  app: App
): Promise<any[]> {
  try {
    const [owner, repo] = repository.split('/');
    console.log(`[GitHub] Fetching commit ${commitSha} from ${owner}/${repo}`);
    
    const octokit = await getInstallationOctokit(owner, repo, app);

    const { data: commit } = await octokit.rest.repos.getCommit({
      owner,
      repo,
      ref: commitSha
    });

    console.log(`[GitHub] Commit has ${commit.files?.length || 0} files`);
    return commit.files || [];
  } catch (error: any) {
    console.error(`[GitHub] Error fetching commit files:`, error?.message || error);
    throw error;
  }
}

export async function postPRComments(
  owner: string,
  repo: string,
  prNumber: number,
  scanResult: any,
  app: App
): Promise<void> {
  try {
    console.log(`[GitHub] Getting installation octokit for ${owner}/${repo}`);
    const octokit = await getInstallationOctokit(owner, repo, app);
    console.log(`[GitHub] Successfully authenticated`);

    // Get the PR head SHA for comments
    const { data: pr } = await octokit.rest.pulls.get({
      owner,
      repo,
      pull_number: prNumber
    });
    const headSha = pr.head.sha;
    console.log(`[GitHub] PR head SHA: ${headSha}`);

    // Group violations by file
    const violationsByFile: { [key: string]: any[] } = {};
    for (const violation of scanResult.violations || []) {
      if (!violationsByFile[violation.file_path]) {
        violationsByFile[violation.file_path] = [];
      }
      violationsByFile[violation.file_path].push(violation);
    }

    console.log(`[GitHub] Posting summary comment`);
    // Post summary comment
    const summaryComment = buildSummaryComment(scanResult);
    try {
      await octokit.rest.issues.createComment({
        owner,
        repo,
        issue_number: prNumber,
        body: summaryComment
      });
      console.log(`[GitHub] Summary comment posted`);
    } catch (error: any) {
      console.error(`[GitHub] Failed to post summary comment:`, error?.message || error);
    }

    // Post inline comments for each violation
    console.log(`[GitHub] Posting ${scanResult.violations?.length || 0} inline comments`);
    let inlineCommentsPosted = 0;
    for (const [filePath, violations] of Object.entries(violationsByFile)) {
      for (const violation of violations) {
        try {
          // Get file content to find the correct line in the diff
          const { data: fileContent } = await octokit.rest.repos.getContent({
            owner,
            repo,
            path: filePath,
            ref: headSha
          });

          if ('content' in fileContent) {
            const lines = Buffer.from(fileContent.content, 'base64').toString('utf-8').split('\n');
            const lineNumber = Math.min(violation.line_number || 1, lines.length);

            await octokit.rest.pulls.createReviewComment({
              owner,
              repo,
              pull_number: prNumber,
              commit_id: headSha,
              path: filePath,
              line: lineNumber,
              body: buildViolationComment(violation)
            });
            inlineCommentsPosted++;
          }
        } catch (error: any) {
          console.error(`[GitHub] Failed to post comment for ${filePath}:${violation.line_number}:`, error?.message || error);
        }
      }
    }
    console.log(`[GitHub] Posted ${inlineCommentsPosted} inline comments`);

    // Set PR status
    console.log(`[GitHub] Setting commit status`);
    const state = scanResult.can_merge ? 'success' : 'failure';
    const description = scanResult.violations?.length
      ? `${scanResult.violations.length} violation(s) found`
      : 'All checks passed';
    
    try {
      await octokit.rest.repos.createCommitStatus({
        owner,
        repo,
        sha: headSha,
        state,
        description,
        context: 'guardrails/security-scan'
      });
      console.log(`[GitHub] Commit status set to ${state}`);
    } catch (error: any) {
      console.error(`[GitHub] Failed to set commit status:`, error?.message || error);
    }
  } catch (error: any) {
    console.error(`[GitHub] Error in postPRComments:`, error?.message || error);
    console.error(`[GitHub] Error stack:`, error?.stack);
    throw error;
  }
}

function buildSummaryComment(result: any): string {
  const emoji = result.can_merge ? '✅' : '❌';
  const status = result.can_merge ? 'PASSED' : 'FAILED';
  
  return `## ${emoji} Guardrails Scan ${status}

**Scan ID:** \`${result.scan_id}\`
**Repository:** ${result.repository}
**Processing Time:** ${result.processing_time_ms.toFixed(2)}ms
**Copilot Detected:** ${result.copilot_detected ? 'Yes' : 'No'}

### Summary
- **Total Violations:** ${result.violations.length}
- **Critical:** ${result.summary.by_severity.critical}
- **High:** ${result.summary.by_severity.high}
- **Medium:** ${result.summary.by_severity.medium}
- **Low:** ${result.summary.by_severity.low}

### Enforcement Action
**Mode:** ${result.enforcement_action.toUpperCase()}
**Can Merge:** ${result.can_merge ? 'Yes' : 'No'}

${result.violations.length > 0 ? 'See inline comments for details.' : 'No violations found!'}
`;
}

function buildViolationComment(violation: any): string {
  const severityEmoji: { [key: string]: string } = {
    critical: '🔴',
    high: '🟠',
    medium: '🟡',
    low: '🟢'
  };

  const emoji = severityEmoji[violation.severity as string] || '⚪';
  const copilotNote = violation.is_copilot_generated
    ? '\n\n⚠️ **AI-Generated Code Detected** - This violation was found in code likely generated by GitHub Copilot.'
    : '';

  return `${emoji} **${violation.severity.toUpperCase()}**: ${violation.rule_name}

**Rule ID:** \`${violation.rule_id}\`
**Category:** ${violation.category}

${violation.explanation}

${violation.fix_suggestion ? `**Suggested Fix:**\n\`\`\`\n${violation.fix_suggestion}\n\`\`\`` : ''}

${violation.standard_mappings.length > 0 ? `**Standards:** ${violation.standard_mappings.join(', ')}` : ''}${copilotNote}
`;
}
