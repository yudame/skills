---
name: do-docs
description: "Find every doc a code change invalidated and make surgical edits so docs match code. Use for 'update docs' or after a merge."
---

# Docs Cascade

After a change lands, every document that describes the changed area should match what the code now does. The input is a PR number, a commit SHA, or a description of the change. The outcome is a minimal set of targeted doc edits, notices on open issues the change affects, and a report of what was updated, what was checked and left alone, and what needs a human.

If the repo documents its own doc conventions (an index file to maintain, canonical doc locations, a doc-impact or link-fixing tool), use them; otherwise everything here runs on `git`, `gh`, and grep.

## Principles

- **Document what is, not what was planned.** Match the actual API and behavior, not the plan or PR description.
- **Surgical edits.** Change only what the code change invalidated; keep structure, tone, and formatting. Don't rewrite accurate sections or document future work.
- **Link, don't duplicate.** Point to the source of truth rather than restating it.
- **When a doc conflicts in a way the code can't settle** (for example a plan describing work that may no longer be valid), flag it for a human rather than guessing.

## Understand the change

Read the change in full, not just the diff: `gh pr view <n> --json title,body,files` plus `gh pr diff <n>`, or `git show <sha>`, or the recent `git log` for a description. Then read each modified file whole; the diff shows what moved, the file shows what it means. Trace data that crosses modified files (string keys matched in two places, shared structures). Compare what the PR or commit message claims against what the diff does, and flag discrepancies.

Come out with: what changed (files, functions, config keys, commands), public-interface and behavior changes, key identifiers docs might mention, and **retired terms**: the old names, paths, and concepts the change replaced. Retired terms drive the stale-reference sweep and catch the most misses.

In parallel, inventory the docs (`git ls-files '*.md' 'docs/**' 'README*'`), noting each file's purpose and the identifiers it references from headings and grep, without reading everything in full. For large changes, subagents work well for the change read, the inventory, and the issue scan below; give them shell tools, or they wedge on the first `git` command. Without subagents, do these yourself in sequence.

## Find affected docs

A doc needs updating if it references the changed area, describes behavior the change alters, teaches a pattern or example using the old interface, or walks through a workflow whose steps changed. Then:

- **Stale-reference sweep:** `git grep -n "<retired-term>" -- '*.md' docs/` for every retired term. After a refactor, the old word usually survives somewhere the triage missed.
- **What's missing:** a new feature, command, skill, config key, or env var with no doc entry gets a task to create one, not just edits elsewhere.
- Order the work foundational docs first (primary guidance, feature docs), derivative docs after.

If nothing is affected, say so and stop.

## Edit

Read each affected file in full before editing it. Update examples to new signatures, paths that moved, descriptions of changed defaults or workflows, and table or list entries that were added, removed, or renamed. Add new docs to the repo's index or table of contents if it has one. Edge cases:

- Deleted feature: remove references to it, but flag the feature's own doc for human review rather than deleting it.
- Renamed function or file: grep every reference across docs and update each.
- Config key change: check setup, deployment, and env-example docs as well as the main guidance file.

## Notify affected open issues

When `gh` and issues are available, check open issues (`gh issue list --state open --json number,title,body --limit 50`) for ones the change concretely affects: a prerequisite now met, an approach invalidated, a new capability to use. Comment on those; never edit issue bodies. Only comment where the impact is concrete and actionable.

```
**Upstream change notice**: a related change just landed that may affect this issue.
**What changed:** ...
**Impact on this issue:** ...
**Action needed:** ...
```

## Verify and finish

- `git diff --name-only` should list only files you meant to touch (including any a repo fixing tool changed, whose diffs you still review). Revert anything unexpected.
- Read `git diff`: each change should be a targeted update, not a rewrite.
- For conflicts needing human judgment, open an issue naming the doc, what it says, and what the code now does.
- Commit the doc changes, staging the specific paths you edited rather than `git add -A` (other work may be in the tree): `Docs: cascade updates for <change>`. Push if the workflow expects it.

Report: the triggering change, docs updated (with what changed), docs reviewed and still accurate, issues opened for review, and open issues commented on.

Pairs with the do-build skill (run after a build ships), the do-plan skill (plans may need updating when prerequisites land), and the do-pr-review skill (to check docs match implementation).
