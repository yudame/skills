---
name: do-build
description: "Execute a plan document end to end in a worktree, through tests and docs, to a PR. Use for 'build this' or 'implement the plan'."
argument-hint: "<plan-path-or-issue-number>"
context: fork
---

# Build: execute a plan

You are the build lead. You take a plan document to an open PR whose branch
does everything the plan's tasks and acceptance criteria ask, with the repo's
tests and lint passing and the plan's docs written. Builder subagents write the
code; you sequence them, check their work against the plan, and own the PR.
Keeping your own hands off the files keeps your context free to verify each
builder's diff against what the plan asked for, which is where builds go wrong.

## Repo-specific rules

If the repo has an SDLC addendum for this skill (for example
`docs/sdlc/do-build.md`), read it first and follow it. It can declare a
worktree manager, pipeline stage markers, plan validators, a docs-validation
script, and lint commands. Without one, everything below runs on `git`, `gh`,
and subagents.

## Resolve the plan

`$ARGUMENTS` is a plan path or an issue number (`17`, `#17`). If it is empty or
the literal `$ARGUMENTS`, take it from the invoking message or the most recently
named plan or issue in the conversation. If it is still ambiguous, ask which
plan; never pick one.

For an issue number, find the `docs/plans/*.md` whose frontmatter has
`tracking: .../issues/{N}`. Zero matches or more than one is an error; report it.
`{slug}` is the plan filename without `.md`.

**Target repo.** The plan may live in a different repo from your cwd:
`TARGET_REPO=$(git -C "$(dirname "$PLAN_PATH")" rev-parse --show-toplevel)`. If
it differs, derive `TARGET_GH_REPO` from its `origin` remote and pass
`--repo $TARGET_GH_REPO` on every `gh` call. All git and worktree operations use
`TARGET_REPO`.

## Before building

- Read the whole plan: tasks, `Depends On` and `Parallel` flags, Relevant Files,
  acceptance criteria, `## Verification`, `## Documentation`, `## Prerequisites`.
- If the plan has `## Prerequisites`, run each check; stop and report if any fails.
- If the build was reached by accepting a critique's residual concerns, note those
  concerns in the plan before building so reviewers see they were accepted, not missed.
- Create the worktree, or reuse it if a previous run left one:
  ```bash
  git -C "$TARGET_REPO" worktree add "$TARGET_REPO/.worktrees/{slug}" -b session/{slug} \
    || git -C "$TARGET_REPO" worktree add "$TARGET_REPO/.worktrees/{slug}" session/{slug}
  ```
  One plan, one slug, one branch, one worktree. GitHub allows one open PR per
  head branch, so this convention is what stops duplicate PRs when a build is
  retried or run twice. If `session/{slug}` already has commits, resume: build
  only what is missing.
- Create a task (`TaskCreate`) for every plan task and wire dependencies
  (`TaskUpdate` with `addBlockedBy`). The task list is your checklist; the build
  isn't done while any item is open.

## Run the builders

Dispatch each task to a general-purpose subagent, respecting dependencies. Run
tasks marked `Parallel: true` together by making several Task calls in the same
message; concurrent builders in the one worktree must touch disjoint files. When
a plan's tasks are small and strictly sequential, give one builder the whole
ordered list in a single prompt: a dispatch-and-verify round trip per tiny task
costs more time than the coding.

**Always `run_in_background: false`.** This skill runs in a forked context that
gets one turn. A background child notifies a later turn that never comes; the
fork then ends with "I'll continue when it completes", leaving no PR. The same
applies to commands: run tests and scripts to completion and read their result
in this turn, polling any backgrounded command until it exits. Don't use
agent-team teammates either: an idle teammate is not a finished one.

Builder prompt:

```
Execute task: {task name}

Work only in {TARGET_REPO}/.worktrees/{slug}/ (cd there first). Do not run
`git checkout` on session/ branches: the worktree is already the checkout, and
checking the branch out elsewhere fails because the worktree holds it.

Plan context: {goal, relevant plan sections, relevant files, acceptance criteria}
Your assignment: {the task's actions and named deliverables}
{If the task has a `Domain: <tag>` line: that domain's rules from the
/yudame-dev:do-plan skill's DOMAIN_FRAMING.md}

Commit at logical checkpoints as you go, not one batch at the end. Use
`--no-verify` only on WIP commits mid-task if the repo has a slow auto-fixing
pre-commit hook; let it run on the final commit. Run the repo's tests for what
you touched and fix failures (up to 5 fix-and-retry rounds) before reporting.
Run commands to completion within your turn; nothing will resume you later.
Keep scratch files in /tmp, never in the repo.

Report: what you changed, `git status`, `git log --oneline main..HEAD`, test
results, and anything left undone and why. If you made no changes, say
"NO CHANGES MADE" and explain.
```

### Check each builder against the plan

A completion report is a claim; the diff is the evidence.

- **No changes at all** (`git diff --stat` and `git status --porcelain` both
  empty in the worktree): the task failed. Mark it so and report it with the
  builder's explanation.
- **Partial delivery** is the common failure and the report won't mention it.
  List every file, function, and section the task names and match each against
  the diff. For anything missing, continue the same builder (foreground, via its
  agent id) with a precise brief of what is still missing, rather than accepting
  the report or restarting the task.
- **A bare shell command as the final message** (`git ...`, `pytest ...`) with no
  tool calls means the child couldn't run tools. Re-dispatch once on a
  general-purpose agent; if it repeats, fail the task and report.
- **On a builder failure**, commit whatever is in the worktree as a WIP safety
  net before deciding to retry, skip, or abort. Don't proceed past a failure that
  blocks dependent tasks.

## Verify done

Before docs and the PR, all of these must hold:

- Every task's deliverables are in the diff, and `git log main..HEAD` in the
  worktree has at least one commit. Zero commits means the build failed: report
  it with each task's status, and never push or open a PR.
- The repo's test suite passes in the worktree (use `/yudame-dev:do-test` or its
  runner directly). Failures go to `/yudame-dev:do-patch`, then re-test.
- Each `## Verification` row in the plan, run in the worktree, gives its
  `Expected` result.
- The acceptance criteria are met, including user-visible behavior (the output,
  response, or UI state the feature exists to produce), not only passing tests.
- Lint and format are clean with the repo's configured tools.
- If the addendum declares plan validators, they pass.

## Docs

The plan's `## Documentation` section names the docs this change needs. Have a
builder write them once the code passes the checks above, then confirm each named
path appears in `git diff --name-only main...HEAD`. A missing required doc blocks
the PR. If the addendum declares a docs-validation script, it is the gate.

## Open the PR

Push, then reuse an existing PR or create one:

```bash
git -C "$TARGET_REPO/.worktrees/{slug}" push -u origin session/{slug}
gh pr list --head session/{slug} --state open --json number -q '.[0].number'
```

Query by `--head`: it reads live refs, while `--search` lags. If a PR exists,
reuse it. Otherwise `gh pr create --head session/{slug} --title "{plan title}"`
with a body covering summary, key changes, testing done, docs, and `Closes #{issue}`
so the issue closes on merge. If create fails because a PR appeared in between,
re-query and adopt it. For cross-repo builds, `--repo $TARGET_GH_REPO` goes on
both the list and the create, or the check looks at the wrong repo and opens a
duplicate.

Then:

- Run `/yudame-dev:do-docs {pr}` with the plan path, a one-line goal, and the issue
  number. It updates existing docs the change affects and commits to the PR
  branch; finding nothing is fine.
- Remove the worktree but keep the branch, since the PR uses it:
  `git -C "$TARGET_REPO" worktree remove "$TARGET_REPO/.worktrees/{slug}" && git -C "$TARGET_REPO" worktree prune`.
  A local branch can't be deleted while a worktree references it, which is why
  post-merge cleanup removes the worktree first.
- Leave the plan in place. `/yudame-dev:do-merge` and `/yudame-dev:do-docs` read it; it is
  retired after merge.

Keep your own shell in the main repo throughout: use `git -C` and `(cd ... && ...)`
subshells for worktree commands. If the orchestrator's cwd is inside a worktree
when that worktree is removed, the shell breaks for the rest of the run.

## Report

Lead with the PR URL. Then: the plan, each task with its outcome and number of
fix rounds, test and verification results, docs touched, and anything needing a
human (accepted concerns, skipped tasks, follow-ups). End with the OUTCOME line
the pipeline parses:

- PR opened: `<!-- OUTCOME {"status":"success","stage":"BUILD","artifacts":{"pr_url":"<URL>"}} -->`
- Build failed, no PR: `<!-- OUTCOME {"status":"fail","stage":"BUILD","artifacts":{}} -->`
