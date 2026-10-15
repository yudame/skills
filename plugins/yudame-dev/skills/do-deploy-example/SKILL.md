---
name: do-deploy-example
description: "Template for a repo's own /do-deploy skill: promote a merged PR to production and verify it. Copy into the repo and customize."
argument-hint: "<pr-number-or-branch>"
context: fork
disable-model-invocation: true
---

# Deploy to Production (Template)

This is a template. Copy this skill's directory into the target repo as `.claude/skills/do-deploy/` and customize it; the last section says how.

You are the production deployment operator: confirm the change is merged, run the repo's production deploy, verify production is healthy, and report with evidence. You don't write code, run tests, or open PRs, and you don't fix anything mid-deploy; if something breaks, report it. Deployment is separate from the development pipeline, which ends at merge (and usually covers dev or staging); this is the deliberate promotion of merged work to production.

Two repo-specific files carry the actual procedure:
- `DEPLOYMENT_PROCESS.md`: environment details, deploy commands, freeze or blocker checks, rollback procedure, required access.
- `HEALTH_CHECKS.md`: verification commands and expected outputs.

If either is missing, stop and say the skill hasn't been customized for this repo, listing what the missing file needs to contain. Don't improvise a production deploy.

## Resolve what to deploy

The argument is a PR number (`123` or `#123`), a branch (find its merged PR), or empty (the most recently merged PR). If it arrives empty or as the literal `$ARGUMENTS`, take it from the user's message. `gh` targets the current repo, or `GH_REPO` if set.

```bash
gh pr view <n> --json number,title,state,mergedAt,mergeCommit,baseRefName
gh pr list --state merged --limit 1 --json number,title,mergedAt,mergeCommit,baseRefName
```

If the PR isn't `MERGED`, stop: unmerged code never goes to production. Record the PR number, title, merge commit, and base branch.

## Before deploying

Bring the local checkout of the base branch up to date and confirm the merge commit is present:

```bash
git checkout main && git fetch origin main && git merge --ff-only origin/main
git log --oneline -1 <merge-commit>
```

Use fetch plus a fast-forward of the named ref rather than `git pull`: `.git/FETCH_HEAD` is shared by every worktree of a repo, so a concurrent fetch in another worktree can retarget a bare pull's merge. If the merge commit still isn't present, stop and report the discrepancy.

Run the blocker checks from `DEPLOYMENT_PROCESS.md` (active incidents, deploy freezes, required approvals) and know the rollback procedure before starting.

## Deploy and verify

Run the deploy commands from `DEPLOYMENT_PROCESS.md`, capturing all output and the deployment timestamp. If the deploy fails, don't retry automatically; a retry against a half-applied production change can make it worse. Report the failure with logs and let a human decide.

Then run every check in `HEALTH_CHECKS.md`, continuing past failures so the report is complete. Collect evidence (status codes, log excerpts, timestamps) and compare against the pre-deploy baseline where you can.

## Report

```
## Deploy Report: PR #{number}

**PR**: {title}
**Commit**: {merge commit}
**Environment**: Production
**Status**: SUCCESS | FAILED | PARTIAL
**Timestamp**: {deploy time}

### Health Checks
- Service responding: {result}
- Error rate normal: {result}
- Key flows verified: {result}

### Evidence
{deploy output, check results, log excerpts}

### Rollback
{If failed or partial: the rollback steps. If succeeded: "No rollback needed."}
```

## Customizing this template

First decide, with the team if there is one, what "deploy" means for this repo:

1. Where does production run (cloud platform, own machines, serverless, edge)?
2. What triggers a production deploy (auto on merge, manual promotion, tagged release)?
3. What's the mechanism (platform CLI, SSH, API call, push to a deploy branch, container registry)?
4. One instance or many (single server, fleet, regions)?
5. How do you know it worked (health endpoint, logs, smoke test, dashboard)?
6. How do you roll back?
7. Are there freezes or gates (incident check, approval, time-of-day)?

Then:
1. Copy this directory to the repo's `.claude/skills/do-deploy/`.
2. In `SKILL.md`: set `name: do-deploy`, write a repo-specific `description`, remove `disable-model-invocation: true` if the model may trigger it, drop "(Template)" from the title, and delete this section.
3. Write `DEPLOYMENT_PROCESS.md` and `HEALTH_CHECKS.md` from the answers above.
4. Test it with `/do-deploy` after the next merge.
