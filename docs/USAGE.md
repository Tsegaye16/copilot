# Usage Guide

## For Developers

### Understanding Scan Results

When you open a PR, the guardrails system automatically scans your code and posts comments.

#### Summary Comment

A summary comment appears at the top of the PR with:
- Total violations found
- Breakdown by severity (Critical, High, Medium, Low)
- Enforcement action
- Whether the PR can be merged

#### Inline Comments

Each violation appears as an inline comment on the specific line with:
- Severity indicator (🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low)
- Rule name and ID
- Detailed explanation
- Suggested fix
- Standards mapping (OWASP/CWE)
- Copilot detection indicator (if applicable)

### Fixing Violations

1. **Read the explanation**: Understand why the violation was flagged
2. **Review the suggested fix**: Apply the recommended solution
3. **Check standards**: Review OWASP/CWE mappings for compliance requirements
4. **Update code**: Make the necessary changes
5. **Re-scan**: Push changes to trigger a new scan

### Copilot-Generated Code

If code is detected as Copilot-generated:
- ⚠️ Indicator appears in violation comments
- Stricter security standards may apply
- Review AI-generated code carefully before merging

### Overriding Blocking Mode

If blocking mode is enabled but you need to merge:
1. Review all critical/high violations
2. Document why override is necessary
3. Use the override mechanism (if enabled in policy)
4. Ensure violations are tracked for follow-up

## For Administrators

### Setting Up Policies

1. **Create repository policy**:
   ```bash
   mkdir -p config/policies/owner
   cp config/policies/default.yaml config/policies/owner/repo.yaml
   ```

2. **Edit policy file**:
   - Set enforcement mode
   - Configure rule packs
   - Enable/disable specific rules

3. **Restart backend** (if needed):
   ```bash
   docker-compose restart backend
   ```

### Monitoring

#### Dashboard

Access dashboard stats:
```bash
curl http://localhost:8000/api/v1/dashboard/stats
```

#### Audit Logs

View audit logs:
```bash
curl http://localhost:8000/api/v1/audit/logs?repository=owner/repo
```

Export logs:
```bash
curl http://localhost:8000/api/v1/audit/logs/export?format=csv > audit.csv
```

### Custom Rules

1. **Create rule pack**:
   ```bash
   vim config/rule_packs/custom.yaml
   ```

2. **Add rules** following the format in existing rule packs

3. **Reference in policy**:
   ```yaml
   rule_packs:
     - custom
     - default
   ```

## Best Practices

### For Development Teams

1. **Fix violations early**: Address issues as soon as they're detected
2. **Review Copilot code**: Always review AI-generated code carefully
3. **Understand policies**: Know your organization's enforcement rules
4. **Use suggested fixes**: AI suggestions are often helpful starting points

### For Security Teams

1. **Start with Advisory**: Begin with advisory mode to build awareness
2. **Gradually tighten**: Move to warning, then blocking as team adapts
3. **Customize rules**: Disable false positives, add organization-specific rules
4. **Monitor trends**: Use dashboard to track improvement over time

### For Compliance Teams

1. **Use rule packs**: Leverage industry-specific rule packs
2. **Review audit logs**: Regular review of audit logs for compliance
3. **Export reports**: Generate CSV exports for compliance reporting
4. **Track violations**: Monitor violation trends and resolution rates

## Troubleshooting

### Scan Not Running

1. Check GitHub App is installed on repository
2. Verify webhook is configured correctly
3. Check backend API is running
4. Review logs: `docker-compose logs backend`

### False Positives

1. Identify the rule ID from violation
2. Review rule pattern in rule pack
3. Disable rule in repository policy if needed
4. Consider improving rule pattern

### Performance Issues

1. Large PRs may take time to scan
2. Consider splitting large PRs
3. Check backend logs for errors
4. Verify Gemini API quota/limits

## Support

For issues or questions:
1. Check documentation in `docs/`
2. Review API documentation at `/docs` endpoint
3. Check logs for error messages
4. Open an issue in the repository
