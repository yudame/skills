# Code Review

The judgment half of `/yudame-dev:do-pr-review`. The PR branch is already checked out.
The aim is a verdict that is grounded, verified, and reproducible: the same PR
reviewed twice should get the same verdict, and every finding should point at
code you actually read.

## Gather

```bash
gh pr view $PR --json title,body,headRefName,baseRefName,files,additions,deletions,headRefOid
gh pr diff $PR
gh issue view $ISSUE        # if resolved
```

Read the plan if there is one: acceptance criteria, no-gos, architectural
decisions, and any `## Verification` table.

## Prior reviews: stay consistent

Find this skill's earlier reviews (bodies starting `## Review:`) in both PR
comments and formal reviews:

```bash
gh api repos/$REPO/issues/$PR/comments --jq '[.[] | select(.body | startswith("## Review:")) | {body, created_at}]'
gh api repos/$REPO/pulls/$PR/reviews  --jq '[.[] | select(.body | startswith("## Review:")) | {body, submitted_at}]'
```

Each review ends with a marker recording what it judged:
`<!-- REVIEW_CONTEXT head_sha=<sha> pr_body_hash=<sha256> -->`. Compute the
current values (`headRefOid`, and
`gh pr view $PR --json body --jq .body | shasum -a 256`). If the most recent
review's marker matches both, return its verdict and findings unchanged with
the note `_Idempotent: prior review on HEAD <sha7> / body hash <hash7> is still
valid._` and go straight to posting.

If either changed, review fresh, then add a `### Review Delta (vs prior review
on HEAD <sha7>)` listing findings that were resolved (and why), new, and
unchanged, so drift between runs is visible instead of silent.

## Author disclosures

Authors often document what they deliberately left out. Re-raising a documented
decision as tech debt is a calibration error, so read the PR body for sections
like *Out of scope*, *Deferred*, *Not in this PR*, *Follow-up(s)*, *Known
limitations*, *Disclosures*, and inline phrases like "deferred", "tracked
separately", "filed as follow-up #N", "out of scope", "dropped".

Check each follow-up claim: `gh issue view N --json state`. An open issue
verifies it. A closed or missing issue, or a claim with no number, is itself a
tech debt finding ("claimed follow-up for X does not resolve to an open
issue"). A plain out-of-scope exclusion with sound reasoning needs no issue.

A candidate finding is **acknowledged** (not tech debt or blocker) when it
matches a disclosure by path, feature, symbol, or issue number, and the
disclosure is verified or a reasoned exclusion. Two exceptions: a disclosure
never excuses violating a plan no-go (that stays a blocker), and if the diff
actually satisfies a disclosed criterion, it is a `pass`, not acknowledged.
That second rule stops a patch from ticking a criterion and the next review
unticking it because the disclosure is still in the body.

## Review the diff

For each changed file, judge correctness against the plan and PR description,
security, error handling at system boundaries, tests, fit with project
patterns, and docs for user-facing changes. Watch for leftover debug code,
unhandled external calls, hardcoded values that should be config, and breaking
changes without a migration path. Grep the callers of changed functions; a
caller whose behaviour could silently change needs a test or a
backward-compatible change.

Against the plan: locate each acceptance criterion in the diff and check its
edge cases. Walk unchecked `- [ ]` items: unmet Acceptance/Success Criteria are
blockers; unmet Test Impact, Documentation, or Update System items are tech
debt. Report only items genuinely unaddressed; a false positive costs more than
a miss. For no-gos tagged `[DESTRUCTIVE]` or `[SEPARATE-SLUG]` with no matching
anti-criterion row in `## Verification`, and authored anti-criteria without
pasted red-state FAIL output in the PR body, add an advisory note; neither
blocks.

If the plan has a `## Verification` table, run each `Command` on this branch
and compare to `Expected` (or use the addendum's runner). A failed check is a
blocker.

Numbers in the PR body, commits, or earlier stage reports ("suite green",
"mypy +0", "2x faster") were measured somewhere else. Reproduce any number your
verdict relies on. Dependency sets, tool versions, and stubs all move results,
and a suite that silently deselects tests reports green while running fewer. A
number you can't reproduce is unverified: don't credit it, and say so.

Also look for legacy cruft: deprecated fields still read or written, fallback
chains, dual implementations, dead imports, stale comments. If the repo defines
a cruft-auditor agent, dispatch it. Cruft goes in a `### Legacy Cruft` section
and is advisory.

## Rubric and verdict

Rate each item `pass`, `fail`, `acknowledged` (unmet but covered by a verified
disclosure), or `n/a`. Critical items are marked (C).

1. **Plan vs implementation** (C): every acceptance criterion delivered or
   acknowledged; no no-go violated; the plan's spike findings agree with its
   task steps.
2. **New code quality** (C): type hints where the project uses them, clear
   names, boundary error handling, no copy-paste blocks. Every new
   `except Exception` logs, re-raises, or is explicitly marked as a safe
   swallow. New public APIs have docstrings.
3. **Tests** (C): new behaviour and code paths are tested, including the
   failure path, not just the happy path. New integration tests cross the real
   serialization boundary rather than staying in memory. Existing tests pass.
4. **Regression risk to callers** (C).
5. **Data integrity** (C): migrations for schema changes; `update_fields`
   includes `modified_at` when the model has `auto_now`; new JSON fields don't
   break reads of existing rows.
6. **Security** (C): no new `mark_safe`, `raw()`, `eval`, `exec`, `subprocess`
   with request-derived input, SQL string interpolation, hardcoded secrets, or
   debug artifacts.
7. **Documentation accuracy**: docs updated for user-facing or architectural
   changes, including a migration path for breaking changes; no stale
   references to removed code.
8. **PR body accuracy**: claimed file counts, test counts, migrations, and
   disclosures match the diff.
9. **Disclosed deferrals** (C): each has an open issue or is a reasoned
   exclusion.
10. **Follow-up claims** (C): every "follow-up #N" resolves to an open issue.

Also note whether UI screenshots were captured, when UI changed.

Findings that don't fit any item go in `### Miscellaneous` with their own
severity. Use it for real issues outside the rubric, not for findings you're
unsure about.

The verdict follows from the ratings, not from overall impression:

- Any critical `fail`, or a Miscellaneous blocker: **Changes Requested** (blockers).
- Otherwise any `fail` on 7 or 8, or Miscellaneous tech debt or nit: **Changes Requested** (tech debt).
- Otherwise: **Approved**.

## Findings

Severities: **blocker** (breaks functionality, security, or data), **tech_debt**
(must be fixed before merge; `/yudame-dev:do-patch` handles it), **nit** (fixed unless
purely subjective), **acknowledged** (listed only under *Acknowledged Deferrals
(verified)*, never in the other sections).

Every blocker, tech_debt, and nit uses this block with every field; a finding
you can't fill in completely is dropped, not shortened:

```
**File:** `path/to/file.py:42`
**Code:** `the_actual_code_on_that_line()`
**Issue:** what is wrong
**Severity:** blocker | tech_debt | nit
**Fix:** suggested fix
```

Before reporting, confirm for each finding that you read the file, the code is
at or near the cited line, and your description is accurate. Drop anything that
fails. A false blocker is worse than a missed issue: an earlier review cited
functions and files that didn't exist and sent a patch cycle chasing them.

## Hand back to posting

The rubric with notes, findings by section (Blockers, Tech Debt, Nits,
Miscellaneous, Acknowledged Deferrals), the review delta if any, verification
results, legacy cruft, the derived verdict, and the `REVIEW_CONTEXT` marker
values. If the idempotency check fired, hand back the prior review unchanged.
