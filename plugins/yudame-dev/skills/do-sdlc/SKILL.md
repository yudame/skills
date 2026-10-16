---
name: do-sdlc
description: "Take an issue to a merged PR by running the do-* stage skills one at a time, each in a subagent where the harness has them. Use for 'ship this issue end to end'."
context: fork
---

# do-sdlc: pipeline supervisor

You take one issue (or PR, or feature description) to a merged PR by running the
do-* stage skills in order, each inside its own subagent. You assess state,
pick the stage, dispatch it, read the report, and repeat. Outside sequential mode
you write no code, plans, tests, or docs yourself: a supervisor doing stage work
loses the clean context it needs to judge each stage, and collides with the
stage that owns the artifact.

## Two modes

- **Supervisor** (the default): loop stage after stage until one of the exits above.
- **Router**: when asked for only the next stage, or when another live session is
  already supervising this issue, do the assessment, dispatch one stage, report,
  and return. Never loop in router mode; whoever invoked you owns progression.
- **Sequential** (a harness without subagents, such as Pi): run each stage
  skill yourself in this session, in the same order and under the same guards.
  Before each stage, re-read only that stage's inputs (the issue, the plan
  file, the PR diff) instead of trusting what earlier stages left in context,
  and finish one stage's commits before starting the next.

## Repo-specific rules

If the repo has an SDLC addendum (for example `docs/sdlc/do-sdlc.md`), read it
first and follow it; it can declare worktree conventions and a
recorded-verdict store. Without one, the pipeline runs on `gh` and `git`, and
the posted GitHub review is the authoritative REVIEW verdict. Say which mode you
are in on your first status line ("no verdict store declared: GitHub reviews are
the verdict"). That is a mode, not a reason to refuse.

## Stages and models

| Stage | Skill | `model:` | Why |
|-------|-------|----------|-----|
| ISSUE | do-issue | sonnet | Structured writing |
| PLAN | do-plan | opus | Architectural design |
| CRITIQUE | do-plan-critique | opus | Adversarial review |
| BUILD | do-build | sonnet | Tool-heavy plan execution |
| TEST | do-test | sonnet | Deterministic test runs |
| PATCH | do-patch | sonnet | Targeted fix |
| REVIEW | do-pr-review | opus | Code review judgment |
| DOCS | do-docs | sonnet | Structured writing |
| MERGE | do-merge | sonnet | Programmatic gate |

Claude Code note: pass `model:` explicitly on every dispatch; the inherited
default is wrong for half the stages.

## Resolve the input

Scope every `gh` call with `--repo <owner/name>` (from `gh repo view --json
nameWithOwner -q .nameWithOwner` at the target repo root). From the wrong cwd or
under a stray `GH_REPO`, a bare `gh` answers about a different repository and
still exits 0.

- **Issue** (`123`, `#123`): `gh issue view`.
- **PR**: `gh pr view {n} --json number,title,state,headRefName,reviewDecision,statusCheckRollup,body`,
  then take the issue from `Closes #N` / `Fixes #N` in the body.
- **Bare description**: in supervisor mode, dispatch ISSUE first and continue
  with the issue it creates. In router mode, return and ask for an issue number.

Never restart from scratch: existing artifacts show where to resume.

## Assess state and choose the stage

### Route from artifacts

Gather the evidence before deciding, as separate commands whose output you read:

- the plan: a `docs/plans/*.md` whose `tracking:` frontmatter or body references the issue;
- the branch: `session/{slug}` (local or remote);
- the PR: `gh pr list --head session/{slug} --state open` (live refs; `--search
  "#N"` uses an index that lags, so use it only as a cross-check);
- PR state: `reviewDecision`, `statusCheckRollup`, `mergeStateStatus`, posted
  reviews and review comments with their timestamps versus the head commit
  (on a self-authored PR `reviewDecision` stays empty even after a full review,
  because GitHub won't let you approve your own PR; the verdict is the posted
  review comment, such as `## Review: Approved`);
- docs: the plan's `## Documentation` checklist and whether the PR diff touches `docs/`.

Then pick the earliest stage that is not done:

- No plan: PLAN. Plan with no critique verdict, or revised since the last
  critique: CRITIQUE. A critique saying NEEDS REVISION or MAJOR REWORK: PLAN
  again.
- Plan accepted, no branch or PR: BUILD. Branch with commits but no PR: BUILD
  (it resumes and opens the PR).
- PR with failing tests or CI: PATCH, then TEST.
- PR with no review on the current head: REVIEW. Changes requested: PATCH, then
  REVIEW again.
- Approved on the current head, docs tasks open: DOCS.
- Approved on the current head, docs done, merge state CLEAN, CI green: MERGE.
- PR merged: done.

Some issues legitimately skip PLAN and CRITIQUE (a small fix with no plan doc).
Don't send those back to planning.

### Routing guards

Apply these when choosing the next stage:

- **Open PR locks out planning.** Once a PR exists, never dispatch PLAN or
  CRITIQUE; route to PATCH, REVIEW, DOCS, or MERGE. A stale pre-PR critique
  must not send a shipped PR back to planning.
- **Critique cap.** After 2 critique rounds that still demand revision, stop and
  escalate to the human rather than looping.
- **Oscillation.** The same stage dispatched 3 times with no state change is a
  stuck loop: stop and report it. This applies to every stage, including DOCS
  and MERGE.
- **Approval must be fresh.** An approval that predates the latest PATCH commit
  does not count; dispatch REVIEW again before MERGE. MERGE needs positive
  evidence that the approval judged the current head; with no such evidence,
  do not merge.
- **Merge conflicts stop the run.** No stage skill resolves conflicts. If the PR
  is conflicted (`DIRTY`), report the PR, its merge state, and that it needs a
  rebase.
- **Build finished but no branch and no PR** means the build output was lost,
  not that planning must restart: find the branch, or report.

## Dispatch a stage

One stage at a time, in the foreground (Claude Code note: pass
`run_in_background: false`). This skill runs in a forked context that gets exactly one turn; a background child
notifies a turn that never comes, so the run silently stalls with work
unpushed. Nor use agent-team teammates: an idle one is not a finished one. One child
at a time also keeps one writer per artifact; the plan doc in particular is a
single file no worktree separates, so never edit it yourself while a stage holds it.

Use a general-purpose subagent (it needs Bash) with this prompt:

```
You are executing ONE SDLC stage for issue #{issue} in {repo_path}.

Run the {skill-name} skill now (in Claude Code, the Skill tool with
"yudame-dev:{skill-name}"), on {issue number, PR number, or plan path as the skill expects}.
The skill is the procedure for this stage; follow it rather than improvising.
Keep working until the stage is done and checked. Stop early only when you
cannot go on without the supervisor or before a risky or irreversible step.
Do not start work that belongs to a later stage.

Context:
- Issue: #{issue}, {title}
- PR: {#pr or "none yet"}
- Plan: {plan path or "none yet"}
- Prior stage outcome: {one line, or "first stage"}
- Commit to session/{slug} at small logical checkpoints, not only at the end,
  so an interruption never loses work.

Report back (data for the supervisor, not prose):
- outcome: success | failure
- verdict: any verdict the skill emitted (READY TO BUILD, NEEDS REVISION, APPROVED, CHANGES REQUESTED, ...)
- artifacts: plan path, PR number, branch, whatever changed
- open items: anything the stage left unfinished, and what blocks it
- failures: errors or test failures verbatim
```

Stage skills also end with an `<!-- OUTCOME {...} -->` line; use it as the
machine-readable status.

Carry context forward: once BUILD reports a PR number, include it in every later
prompt.

### Reading the report

- **A report is a claim; the repo is the evidence.** Check it against reality
  before advancing (the PR exists, the commits are pushed, the review is posted).
- **Open items with no stated blocker** mean the stage stopped early, not that
  it finished. Re-brief the same stage once, naming the open items. If it stops
  again, treat it as a failure and report.
- **A bare shell command as the final message** with zero tool calls means the
  child lacked the tools. Re-dispatch once on a general-purpose agent; if it
  repeats, stop and report the mismatch.

## Loop and exits (supervisor mode)

After each stage, reassess and dispatch the next. Write one progress line per
iteration, for example `CRITIQUE done (READY TO BUILD), dispatching BUILD on sonnet`.

Cap the run at 15 dispatches. A happy path is 8; the oscillation rule catches
real loops well before the cap.

Exit when:
- MERGE reports a merge and `gh pr view {pr} --json state,mergedAt` confirms
  `MERGED`: success.
- The pipeline is already complete (PR merged): success. Report it as done, not as a failure.
- A guard blocks, a stage fails in a way the next stage cannot fix, or a
  conflict needs a human: stop and report.
- The cap is reached: stop and report how far it got.

Don't stop to check in between stages; status lines go with the next dispatch.
Stop for the human only when blocked as above, or at a risky action a stage flags.

## Final report

1. Outcome: merged, already complete, blocked (guard and reason), or cap reached.
2. Stage trail: each dispatch in order with its outcome and verdict.
3. Artifacts: issue, plan, PR, merge commit.
4. What needs the human: blockers, accepted concerns, follow-ups.
