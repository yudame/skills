---
name: do-plan-critique
description: "Run independent critics over a plan before build and return a readiness verdict. Use for 'critique this plan' or 'war room'."
argument-hint: "<plan-path-or-issue-number>"
---

# Plan Critique (War Room)

Critique a plan document before it is built: run structural checks, then dispatch independent critics (one for a small plan, three for a large or risky one), aggregate their findings, and return a verdict: READY TO BUILD (no concerns), READY TO BUILD (with concerns), NEEDS REVISION, or MAJOR REWORK.

The value of the war room is independent convergence. Two critics reaching the same blocker without seeing each other's reasoning is stronger evidence than one pass listing it twice. A good critique finds the few things that would actually cause rework, each specific enough that the reviser can fix it without re-investigating, and says plainly when the plan is ready.

This skill does not rewrite the plan, expand scope, or argue for a different architecture. Its output is findings and a verdict; `/yudame-dev:do-plan` does the revision.

## Run inline

This skill runs in the context that invokes it, not as a forked skill. The harness withholds the Agent tool from subagents at its spawn-depth limit (three layers below the main conversation by default). A pipeline that already runs each stage in its own subagent put a forked critique exactly at that limit, so it could spawn no critics and quietly collapsed into one agent applying every lens in sequence while the report still looked like a war room. Inline, the critics are one layer shallower.

## 1. Resolve the plan

The argument is an issue number or a plan path. Resolve both the absolute plan path and the issue number. Assign `ISSUE_NUMBER` fresh on every run, never with a `${ISSUE_NUMBER:-…}` default: a stale value inherited from an earlier context once sent a verdict to the wrong issue. These commands avoid `grep -P`, which macOS grep lacks:

```bash
ARG="$ARGUMENTS"; ISSUE_NUMBER=""; PLAN_PATH=""
if [[ "$ARG" =~ ^#?[0-9]+$ ]]; then
  ISSUE_NUMBER="${ARG#\#}"
  PLAN_PATH=$(gh issue view "$ISSUE_NUMBER" --json body -q .body | grep -oE 'docs/plans/[^[:space:])]+\.md' | head -1)
elif [[ "$ARG" == *.md ]]; then
  PLAN_PATH="$ARG"
  ISSUE_NUMBER=$(sed -nE 's/^tracking:[[:space:]]*(.*\/issues\/|#)?([0-9]+).*/\2/p' "$PLAN_PATH" | head -1)
fi
```

Make `PLAN_PATH` absolute (try `$(git rev-parse --show-toplevel)/$PLAN_PATH`, then the cwd) and confirm the file exists; stop with a clear error if it does not. Pass the absolute path everywhere downstream. A repo-relative path resolved from a worktree cwd finds nothing, and a critic that finds nothing may improvise a critique of a plan that does not exist.

## 2. Load context

Read the plan in full. If it has a tracking issue, read it (`gh issue view N --json title,body,comments`). Fetch up to five issues or PRs from its Prior Art section for their title and state.

Bundle the files the plan references into a `SOURCE_FILES` block for the critics: extract paths from the plan (backticked paths, paths in code blocks), read each, and include its contents under a `--- path ---` header, or `[FILE NOT FOUND]` for a missing one. Critics work from this verified source instead of recalling or guessing file contents.

## 3. Structural checks

Do these yourself, without a model call:

| Check | Severity if it fails |
|---|---|
| Required sections present and non-empty (the repo's mandated set if it declares one, otherwise problem, solution, tasks, verification) | BLOCKER |
| Every `Depends On` points to a real task ID; no cycles | BLOCKER |
| Task numbering has no gaps | CONCERN |
| Every task has a way to validate it | CONCERN |
| Referenced file paths and Test Impact test paths exist (a missing one may be intentionally new) | CONCERN |
| Every Success Criterion maps to at least one task | CONCERN |
| No No-Go or Rabbit Hole appears as planned work in Solution or tasks | CONCERN |

Run each Prerequisites check command and report its current status.

## 4. Triage and fix the roster

Choose LITE (one Consolidated Critic) or FULL (Risk & Robustness, Scope & Value, History & Consistency).

FULL is forced, with no model call, when the plan has `appetite: Large` or touches high-risk paths: the repo's skills, hooks, agent or persona config, and core pipeline or routing code (or whatever paths the repo declares as doctrine). Nothing downgrades a forced FULL.

Otherwise spawn one foreground `sonnet` agent with:

```
You are a plan triage agent. Classify this plan as LITE or FULL critique depth.
LITE = purely internal, small scope (one bug fix, one CLI flag, one config key).
FULL = critical paths, cross-component changes, new abstractions, architectural decisions.
Bias to FULL when ambiguous.
Reply with exactly one line: "LITE: <reason>" or "FULL: <reason>".

PLAN:
{frontmatter + first 1000 characters}
```

Write the roster names down before dispatching. Completion is checked against this list, so it cannot be satisfied by dispatching fewer critics than it names.

## 5. Dispatch the critics

Read `CRITICS.md` for the prompt template and each critic's lens. Each critic gets the full plan, the SOURCE_FILES block, the issue and prior-art context, and its lens.

- Issue every critic call in one message so they run concurrently, each a general-purpose agent with `model: "sonnet"`.
- Pass `run_in_background: false` explicitly on each. A backgrounded subagent dies with the turn that spawned it.
- Do not pass `name`: a named spawn from inside a subagent is refused where an unnamed one succeeds.

Record the mode for the report. If the critics were dispatched, the mode is `independent roster ({M} critics)`. If the Agent tool is not available here, or every dispatch is refused with the spawn-depth error, apply each lens yourself in sequence, writing each lens's findings under its roster name, and set the mode to `sequential lenses (Agent tool unavailable: {exact error, or "not in tool list"})`. A sequential run still produces verified findings; what it cannot produce is corroboration, and the report must make that visible.

## 6. Check completion

Before aggregating, confirm every roster member returned findings or `No findings.`, and that each result's `GROUNDING:` line quotes text that actually appears in the plan. A result with no verifiable quote is a fabricated critique of some other plan and counts as missing.

Re-dispatch only the missing critics, in the foreground, at most twice (three attempts per critic in total). If any are still missing, do not aggregate. The verdict is:

```
MAJOR REWORK (CRITIQUE INCOMPLETE: roster N/M — missing: {names})
```

The stage always ends with a verdict, never a silent or empty exit.

## 7. Aggregate

Go through every roster member by name, not just whatever came back. Combine structural and critic findings, then:

- Deduplicate: when critics flag the same issue, keep the higher severity and list every critic that agreed.
- When two different critics independently flag the same component, raise it to BLOCKER.
- Drop any CONCERN or BLOCKER without an Implementation Note, and say in the report that it was dropped. Do not re-run the critic: a finding without a concrete note is not yet specific enough to act on.
- Sort BLOCKERs, then CONCERNs, then NITs.

## 8. Report and verdict

Print every section header, writing `None.` under an empty one:

```markdown
# Plan Critique: {plan name}

**Plan**: {absolute plan path}
**Issue**: #{issue_number}
**Critics**: {roster} ({LITE | FULL})
**Mode**: {independent roster (M critics) | sequential lenses (Agent tool unavailable: reason)}
**Findings**: {N} total ({b} blockers, {c} concerns, {n} nits)

## Blockers

### {finding title}
- **Severity**: BLOCKER
- **Critics**: {who flagged it}
- **Location**: {plan section}
- **Finding**: {what is wrong}
- **Suggestion**: {how to fix}
- **Implementation Note**: {guard condition, call signature, or gotcha}

## Concerns
{same shape}

## Nits
{same shape; Implementation Note optional}

## Structural Check Results

| Check | Status | Detail |
|-------|--------|--------|
| Required sections | PASS/FAIL | ... |
| Task numbering | PASS/FAIL | ... |
| Dependencies valid | PASS/FAIL | ... |
| File paths exist | PASS/FAIL | N of M exist |
| Prerequisites met | PASS/FAIL | ... |
| Cross-references | PASS/FAIL | ... |

## Verdict

{one verdict string}
```

| Verdict | When | Next step |
|---|---|---|
| READY TO BUILD (no concerns) | No BLOCKERs or CONCERNs (NITs don't count) | `/yudame-dev:do-build` |
| READY TO BUILD (with concerns) | CONCERNs but no BLOCKERs | `/yudame-dev:do-plan` revision pass, then critique again; never straight to build |
| NEEDS REVISION | One or more BLOCKERs | `/yudame-dev:do-plan` with the blockers |
| MAJOR REWORK | Fundamental problems, or an incomplete roster | Back to issue discussion and re-planning |

A "with concerns" revision is a clarity pass, not rework: `/yudame-dev:do-plan` embeds each concern's Implementation Note in the plan so the builder doesn't re-investigate. The revise-and-recritique loop exits to build when a round comes back with no concerns, or when the pipeline's own bound on concern rounds runs out and the remaining concerns are accepted on the record.

The Mode line is part of the result: `sequential lenses` tells whoever reads the verdict that no finding was independently corroborated, whatever the Critics line lists.

## Recording the verdict

Standalone, the printed verdict is the output and nothing else is needed. If the plan has a `## Critique Results` table, write the aggregated findings into it.

