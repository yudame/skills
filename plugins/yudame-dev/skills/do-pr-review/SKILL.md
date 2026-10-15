---
name: do-pr-review
description: "Review a PR against its plan and issue and post a verified verdict to GitHub. Use for 'review this PR' or a PR URL."
argument-hint: "<pr-number>"
allowed-tools: mcp__byob__*, Bash(gh:*), Bash(git:*), Bash(python:*), Bash(jq:*), Read, Write, Edit, Grep, Glob, Agent
---

# PR Review

Decide whether a PR is ready to merge, and leave that decision on GitHub where
the author and the merge gate can see it. A good review is grounded in what
was meant to be built (the plan and issue), cites only code you actually read,
reaches the same verdict when run twice on the same inputs, and approves only
when there is nothing left to do. A review that exists only in your output is
not a review.

The argument is the **PR number**, not the issue number.

## Repo-specific rules

If the repo has a review addendum (for example `docs/sdlc/do-pr-review.md`),
read it first and follow it. It can declare a bot review identity, cross-repo
`gh` targeting (such as `GH_REPO`), pre-resolved context variables
(`$SDLC_PR_NUMBER`, `$SDLC_PLAN_PATH`, `$SDLC_ISSUE_NUMBER`, ...), a
verification-table runner, a multi-judge roster, a verdict-recording substrate,
and extra gates. Everything below marked "if the addendum declares" is skipped
without one; the generic path needs only `git`, `gh`, file reading, and a
browser MCP for screenshots.

## Where this runs

Run inline in whatever context invoked you, not as a forked skill. Subagents
can only nest so deep: a supervisor that already runs each stage in its own
subagent, plus a fork, leaves the review unable to spawn judges, and the
roster silently collapses into one reviewer. Isolation is the dispatcher's job:
because the review checks out the PR branch, a caller that needs its own
working tree preserved spawns this skill as an Agent with
`isolation: "worktree"` and `run_in_background: false`.

## 1. Resolve context and preflight

Resolve the repo, the plan path (from the addendum's variables, else
`docs/plans/<slug>.md` derived from a `session/<slug>` branch, else a plan doc
mentioning the issue, else none), and the issue number.

Take the issue number from the PR body: `Closes|Fixes|Resolves #N` first, then a
`tracking: .../issues/N` URL. An inherited `$SDLC_ISSUE_NUMBER` is a last
resort only, because a stale value from an earlier task once diverted a verdict
onto the wrong issue. If the addendum records verdicts against the issue and
none resolves, fail loudly rather than guess.

Before reading any code, check whether the PR can merge at all. A pass once
approved a PR three times while it had conflicts.

```bash
gh pr view $PR --json state,mergeable,mergeStateStatus
```

`mergeable` is computed asynchronously; on `UNKNOWN`, wait 2s and retry once.

| State | Action |
|---|---|
| `state != OPEN` | `PR_CLOSED`: post a short comment, stop |
| `CONFLICTING`, `DIRTY`, or still `UNKNOWN` | `BLOCKED_ON_CONFLICT`: post a comment citing the `mergeStateStatus` and asking for a rebase, stop |
| `BEHIND` | Note it and review normally; it merges once updated |
| `MERGEABLE` with `CLEAN`, `HAS_HOOKS`, `UNSTABLE`, or `BLOCKED` | Review normally. `BLOCKED` means missing review/checks, which is what this review supplies; `UNSTABLE` (non-required checks failing) goes into findings |

Short-circuit paths post with `gh pr comment`, never `gh pr review`: a formal
review on a conflicted or closed PR records a code verdict that was never
made. Templates are in `sub-skills/post-review.md`.

Then check out the branch so every file you read is the PR's code. Reading
whatever branch was already checked out produces findings about code that
isn't in the diff.

```bash
git merge --abort 2>/dev/null; git rebase --abort 2>/dev/null; git stash --include-untracked 2>/dev/null
gh pr checkout $PR
```

## 2. Review the code

Follow `sub-skills/code-review.md`. It covers reading prior reviews (and
returning the same verdict when nothing changed), honouring the author's
disclosed deferrals, reviewing the diff against the plan, running the plan's
verification table, the rubric, finding format and verification, and how the
verdict is derived.

### Multi-judge (only if the addendum declares a roster)

Dispatch one general-purpose Agent per declared judge, each with its lens and
the same PR context. Pass `run_in_background: false` on every dispatch and wait
for every judge in this turn before aggregating: a parent that returns while
judges are in flight kills them, and nothing gets posted. Don't pass `name` on
these dispatches; a named spawn from inside a subagent is refused with a
misleading "Teammates cannot spawn other teammates" error where the unnamed one
succeeds.

Judges return their findings; they don't post or record anything. You post
per-judge comments under a heading distinct from the aggregate, then the
aggregate `## Review:` comment last, then make exactly one verdict-record call.
A failed optional judge counts as a skip unless the addendum marks it
fail-closed.

The value of a roster is independent agreement, so record which mode actually
ran as `REVIEW_MODE`: `independent roster (M judges)`, or, if the Agent tool is
missing or every dispatch hits the spawn-depth error, apply each lens yourself
and record `sequential lenses (Agent tool unavailable: <exact error or "not in
tool list">)`. State the mode in the posted review, the summary, and the OUTCOME
`notes`. A sequential run is a shortfall: list only the judges that ran, keep
the declared roster size as expected, and never present it as consensus.

## 3. Visual proof for UI changes

If the diff touches UI files, an approval needs at least one screenshot of the
changed UI, because static review can't see visual bugs.

```bash
gh pr diff $PR --name-only | grep -E '\.(html|htm|jsx|tsx|vue|css|scss|sass|less)$|/(ui|frontend|static|web|assets|templates|components)/'
```

Also count `.js`/`.ts` under those directories and Python files that render
templates. Start the app the way the README's `## Running` section says, then
capture with the browser MCP (by default `mcp__byob__browser_*`, which drives
the user's real logged-in Chrome, so authenticated staging URLs work; there is
no headless fallback). Confirm a tab exists with `browser_list_tabs`, navigate,
and save to `generated_images/pr-$PR/01_main_view.png`, `02_feature_demo.png`,
`03_edge_case.png`. One to three shots of the changed paths is typical. If the
addendum requires a dedicated real-Chrome session, honour it, since concurrent
sessions race on the active tab. Stop any dev server you started.

If UI files changed and you captured nothing (no browser, app wouldn't start),
the verdict is `CHANGES_REQUESTED` whatever else you found, with this blocker
naming the UI files:

```
**File:** `(PR diff: UI files without visual proof)`
**Code:** `<the changed UI files>`
**Issue:** UI changes but no screenshots were captured; visual proof is required before approval.
**Severity:** blocker
**Fix:** Start the app, open the affected pages in the browser MCP, capture at least one screenshot, and re-run the review.
```

## 4. Post the review

Follow `sub-skills/post-review.md`: body templates, self-authored PR handling,
the plan-checkbox sync that must be pushed before an approval is posted, and
confirming the review actually landed.

Approve only with zero findings. Any blocker, tech debt, or nit means
`--request-changes`, because approval tells the merge gate there is no work
left, and `/yudame-dev:do-patch` fixes tech debt and nits too. Only a purely subjective
nit may be waived, and that needs a human's say-so. Never drop a finding to make
a review look clean, and never soften a blocker into tech debt to speed a
merge.

## 5. Record the verdict (only if the addendum declares a substrate)

Without a substrate, the posted GitHub review is the verdict; `/yudame-dev:do-sdlc`
skips its own check in that case.

With one, every exit path (approved, changes requested, conflict, closed) goes
through the addendum's single finalize call, before the OUTCOME line. Nothing
else records it for you, and a skipped record leaves the pipeline router blind
and looping on re-review. Count flags take integers (`--blocker-count 2`),
never findings text; the findings live in the posted review. Omit a count to
mean "not assessed"; pass `0` for "assessed, none".

On approval, the finalize call writes the verdict, the head SHA it judged, and
the REVIEW completion marker together and reads them back. A non-zero exit is a
hard stop: don't emit OUTCOME or treat the review as done. It isn't
transactional, so the error says what landed; re-run the identical call, which
is idempotent. On non-approved verdicts the marker stays `in_progress` so the
review re-runs after a patch. If the addendum declares stage markers, also
write REVIEW `in_progress` once the issue number is resolved.

## 6. Report

Summarize as bullets: branch to base, plan path or "none", result, review mode
(if a roster was declared), review URL, counts of blockers / tech debt / nits,
and screenshots captured with their directory.

End with one OUTCOME line, which `/yudame-dev:do-sdlc` parses. It is the last line, not
the last action: posting and any verdict record come first.

```
<!-- OUTCOME {"status":"success","stage":"REVIEW","verdict":"APPROVED","artifacts":{"review_url":"<url>","blockers":0,"tech_debt":0,"nits":0},"notes":"Approved with no findings.","next_skill":"/yudame-dev:do-docs"} -->
<!-- OUTCOME {"status":"partial","stage":"REVIEW","verdict":"CHANGES_REQUESTED","artifacts":{"review_url":"<url>","blockers":0,"tech_debt":2,"nits":1},"notes":"2 tech_debt, 1 nit. Routing to /yudame-dev:do-patch.","next_skill":"/yudame-dev:do-patch"} -->
<!-- OUTCOME {"status":"fail","stage":"REVIEW","verdict":"CHANGES_REQUESTED","artifacts":{"review_url":"<url>","blockers":2,"tech_debt":1,"nits":0},"notes":"2 blockers.","failure_reason":"2 blockers must be fixed before merge","next_skill":"/yudame-dev:do-patch"} -->
<!-- OUTCOME {"status":"fail","stage":"REVIEW","verdict":"BLOCKED_ON_CONFLICT","artifacts":{"review_url":"<comment_url>","mergeStateStatus":"DIRTY","mergeable":"CONFLICTING"},"notes":"Merge conflicts; rebase required before review.","failure_reason":"mergeStateStatus=DIRTY","next_skill":null} -->
<!-- OUTCOME {"status":"fail","stage":"REVIEW","verdict":"PR_CLOSED","artifacts":{"review_url":"<comment_url>","state":"CLOSED"},"notes":"PR is not open; review skipped.","failure_reason":"state=CLOSED","next_skill":null} -->
```

Use `partial`, not `success`, whenever tech debt or nits exist, so the pipeline
patches before moving on. Conflict and closed verdicts use `next_skill: null`;
a human has to rebase or decide.

Multi-judge runs add `"judges_run": M` and `"consensus_disagreement": true|false`
to `artifacts`; single-reviewer runs must not include them. If fewer judges
reported than the roster declared, use `"status":"fail"`,
`"verdict":"CHANGES_REQUESTED"`, `"quorum_shortfall": true`, omit
`consensus_disagreement` (agreement is meaningless when the rule never ran),
and name the shortfall in the first clause of `notes`.
