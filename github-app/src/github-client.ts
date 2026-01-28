/**
 * GitHub API client utilities
 */
import { App } from '@octokit/app';
import { Octokit } from '@octokit/rest';
import { createAppAuth } from '@octokit/auth-app';

export async function getInstallationOctokit(
  owner: string,
  repo: string,
  app: App
): Promise<Octokit> {
  try {
    console.log(`[GitHub] Getting installation for ${owner}/${repo}`);
    
    // Get installation ID for the repository using the app's octokit
    const { data: installation } = await app.octokit.request('GET /repos/{owner}/{repo}/installation', {
      owner,
      repo
    });
    
    console.log(`[GitHub] Installation ID: ${installation.id}`);
    
    // Format private key (handle both \n and actual newlines)
    let privateKey = process.env.GITHUB_APP_PRIVATE_KEY || '';
    if (privateKey.includes('\\n')) {
      privateKey = privateKey.replace(/\\n/g, '\n');
    }
    
    // Create auth instance using @octokit/auth-app
    const auth = createAppAuth({
      appId: process.env.GITHUB_APP_ID!,
      privateKey: privateKey,
    });
    
    // Get installation authentication token
    const installationAuthentication = await auth({
      type: 'installation',
      installationId: installation.id,
    });
    
    console.log(`[GitHub] Got installation access token`);
    
    // Create Octokit instance with the installation token
    const octokit = new Octokit({
      auth: installationAuthentication.token
    });
    
    if (!octokit) {
      throw new Error('Failed to create Octokit instance');
    }
    
    if (!octokit.rest) {
      throw new Error('Octokit instance missing rest property');
    }
    
    console.log(`[GitHub] Successfully created Octokit instance with rest API`);
    return octokit;
  } catch (error: any) {
    console.error(`[GitHub] Error getting installation octokit:`, error?.message || error);
    console.error(`[GitHub] Error stack:`, error?.stack);
    throw error;
  }
}

export async function getPRFiles(
  repository: string,
  prNumber: number,
  app: App
): Promise<any[]> {
  try {
    const [owner, repo] = repository.split('/');
    console.log(`[GitHub] Fetching PR files for ${owner}/${repo} PR #${prNumber}`);
    
    const octokit: any = await getInstallationOctokit(owner, repo, app);
    
    if (!octokit) {
      throw new Error('Octokit instance is undefined');
    }
    
    // Use rest.pulls API
    console.log(`[GitHub] Calling octokit.rest.pulls.listFiles`);
    const { data: files } = await octokit.rest.pulls.listFiles({
      owner,
      repo,
      pull_number: prNumber
    });

    console.log(`[GitHub] Found ${files.length} files in PR`);

    if (files.length === 0) {
      console.warn(`[GitHub] No files found in PR #${prNumber}`);
      return [];
    }

    // Fetch full content for each file
    const filesWithContent = await Promise.all(
      files.map(async (file) => {
        if (file.status === 'removed') {
          console.log(`[GitHub] Skipping removed file: ${file.filename}`);
          return file;
        }

        try {
          // Get PR details to find the head SHA
          const { data: pr } = await octokit.rest.pulls.get({
            owner,
            repo,
            pull_number: prNumber
          });

          // Try to get file content from PR head
          const { data: content } = await octokit.rest.repos.getContent({
            owner,
            repo,
            path: file.filename,
            ref: pr.head.sha
          });

          if ('content' in content && content.encoding === 'base64') {
            const fileContent = Buffer.from(content.content, 'base64').toString('utf-8');
            console.log(`[GitHub] Fetched content for ${file.filename} (${fileContent.length} chars)`);
            return {
              ...file,
              contents: fileContent
            };
          }
        } catch (error: any) {
          console.error(`[GitHub] Failed to fetch content for ${file.filename}:`, error?.message || error);
          // Return file with patch if available
          if (file.patch) {
            console.log(`[GitHub] Using patch for ${file.filename}`);
            return file;
          }
        }

        return file;
      })
    );

    const filesWithActualContent = filesWithContent.filter(f => f.contents || f.patch);
    console.log(`[GitHub] Files with content: ${filesWithActualContent.length}/${files.length}`);
    
    return filesWithActualContent;
  } catch (error: any) {
    console.error(`[GitHub] Error fetching PR files:`, error?.message || error);
    console.error(`[GitHub] Error stack:`, error?.stack);
    throw error;
  }
}

export async function getCommitFiles(
  repository: string,
  commitSha: string,
  app: App
): Promise<any[]> {
  try {
    const [owner, repo] = repository.split('/');
    console.log(`[GitHub] Fetching commit ${commitSha} from ${owner}/${repo}`);
    
    const octokit: any = await getInstallationOctokit(owner, repo, app);
    
    if (!octokit) {
      throw new Error('Octokit instance is undefined');
    }
    
    // Use rest.repos API
    console.log(`[GitHub] Calling octokit.rest.repos.getCommit`);
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
  const copilotEmoji = result.copilot_detected ? '🤖' : '';
  
  const criticalCount = result.summary?.by_severity?.critical || 0;
  const highCount = result.summary?.by_severity?.high || 0;
  const mediumCount = result.summary?.by_severity?.medium || 0;
  const lowCount = result.summary?.by_severity?.low || 0;
  const copilotViolations = result.summary?.copilot_violations || 0;
  
  let enforcementNote = '';
  if (result.enforcement_action === 'blocking' && !result.can_merge) {
    enforcementNote = '\n⚠️ **Blocking mode active** - Merge is blocked until violations are resolved.';
    if (result.override_blocking !== undefined) {
      enforcementNote += '\n💡 You can request an override if needed (subject to policy).';
    }
  } else if (result.enforcement_action === 'warning') {
    enforcementNote = '\n⚠️ **Warning mode** - Merge allowed but violations should be addressed.';
  }
  
  return `## ${emoji} Guardrails Security Scan ${status} ${copilotEmoji}

**Scan ID:** \`${result.scan_id}\`  
**Repository:** ${result.repository}  
**Processing Time:** ${result.processing_time_ms.toFixed(2)}ms  
**Copilot Detected:** ${result.copilot_detected ? 'Yes 🤖' : 'No'}

### 📊 Summary
- **Total Violations:** ${result.violations?.length || 0}
- **🔴 Critical:** ${criticalCount}
- **🟠 High:** ${highCount}
- **🟡 Medium:** ${mediumCount}
- **🟢 Low:** ${lowCount}
${copilotViolations > 0 ? `- **🤖 Copilot Violations:** ${copilotViolations}` : ''}

### ⚙️ Enforcement Action
**Mode:** \`${result.enforcement_action.toUpperCase()}\`  
**Can Merge:** ${result.can_merge ? '✅ Yes' : '❌ No'}${enforcementNote}

${result.violations?.length > 0 
  ? `\n### 📝 Details\nSee inline comments below for detailed violation information and fix suggestions.` 
  : '\n### ✨ No violations found! All checks passed.'}

---
*Powered by Enterprise GitHub Copilot Guardrails*
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
    ? '\n\n> ⚠️ **AI-Generated Code Detected** 🤖\n> This violation was found in code likely generated by GitHub Copilot. Stricter security standards apply to AI-generated code.'
    : '';

  const categoryEmoji: { [key: string]: string } = {
    security: '🔒',
    compliance: '📋',
    code_quality: '📝',
    license: '📄',
    ip_risk: '⚖️',
    standard: '📏'
  };

  const catEmoji = categoryEmoji[violation.category] || '📌';

  let standardsSection = '';
  if (violation.standard_mappings && violation.standard_mappings.length > 0) {
    standardsSection = `\n### 📚 Standards Mapping\n${violation.standard_mappings.map((s: string) => `- ${s}`).join('\n')}`;
  }

  let fixSection = '';
  if (violation.fix_suggestion) {
    fixSection = `\n### 🔧 Suggested Fix\n\`\`\`${getLanguageFromPath(violation.file_path)}\n${violation.fix_suggestion}\n\`\`\``;
  }

  return `${emoji} **${violation.severity.toUpperCase()}** ${catEmoji} ${violation.rule_name}

**Rule ID:** \`${violation.rule_id}\`  
**Category:** ${violation.category}  
**File:** \`${violation.file_path}\`  
**Line:** ${violation.line_number}

### 📖 Explanation
${violation.explanation}${fixSection}${standardsSection}${copilotNote}

---
*For more information, see [OWASP Top 10](https://owasp.org/www-project-top-ten/) and [CWE Database](https://cwe.mitre.org/)*
`;
}

function getLanguageFromPath(filePath: string): string {
  const ext = filePath.split('.').pop()?.toLowerCase() || '';
  const langMap: { [key: string]: string } = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'java': 'java',
    'go': 'go',
    'rs': 'rust',
    'cpp': 'cpp',
    'c': 'c',
    'rb': 'ruby',
    'php': 'php',
    'sh': 'bash',
    'sql': 'sql'
  };
  return langMap[ext] || '';
}
