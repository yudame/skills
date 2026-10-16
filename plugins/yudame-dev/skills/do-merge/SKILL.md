---
name: do-merge
description: "Verify a reviewed PR is truly ready (green, approved, conflict-free), squash-merge it, and clean up. Use for 'merge this PR'."
---

# Do-Merge

You are the last gate before code lands on the base branch. Your job is to
confirm, from checkable facts, that the PR is finished, then squash-merge it.
If any fact can't be confirmed, refuse and say which one and what you saw.
A refused merge is cheap to retry; a bad merge is not.

Out of scope: resolving conflicts, rebasing, force-pushing, or fixing CI. It
stops and reports; the do-patch skill or the author does the fixing.

## Inputs

The PR number (`42` or `#42`). If none is given, take it from the conversation;
if it still isn't clear, ask.

## Repo-specific rules

If the repo has a merge addendum (for example `docs/sdlc/do-merge.md`), read it
first and follow it. Addenda can add gates (lint, lockfile sync, full test
suite, docs), a merge-authorization hook, a recorded review verdict to use in
place of GitHub's review state, plan migration, and post-merge cleanup. If the
addendum declares a single merge-predicate command, run it and honor its result
rather than reassembling the checks yourself: it is the same predicate the
repo's merge guard enforces, so anything else drifts. Addenda only add
requirements; they never relax the gate below.

Without an addendum, the skill runs on `git` and `gh` alone.

## The gate

Read the state in one call:

```bash
gh pr view {PR} --json state,mergeable,mergeStateStatus,statusCheckRollup,reviewDecision,body,author,labels,headRefName
```

All of these must hold:

- `state == "OPEN"`.
- `mergeable == "MERGEABLE"`. GitHub computes this asynchronously, so on
  `UNKNOWN` wait about 8 seconds and re-fetch once. Still `UNKNOWN` is a
  failure, never a pass; ask the user to retry shortly.
- `mergeStateStatus == "CLEAN"`. `BLOCKED`, `BEHIND`, `DIRTY`, and `UNSTABLE`
  all fail.
- Every `statusCheckRollup` entry concluded `SUCCESS`. An empty rollup passes
  only if branch protection requires no checks.
- Review approved: `reviewDecision == "APPROVED"`, or, if the addendum
  declares a recorded review verdict, that verdict contains `APPROVED`.
  `CHANGES_REQUESTED`, `REVIEW_REQUIRED`, or no review fails and routes back
  to the do-pr-review or do-patch skill. Self-authored PRs often carry their
  review as a `## Review: Approved` comment instead of a formal review; accept
  that only if it is the latest review comment and postdates the head commit.
- The body links the tracking issue with `Closes #N`, `Fixes #N`, or
  `Resolves #N`, so the issue closes on merge.

Fail closed: anything you couldn't confirm counts as a failure.

If the addendum declares a docs-completion gate, enforce it alongside review.
If not, docs completion can't be verified here; say so in your report rather
than implying it was checked.

### PRs that didn't come through planning

Dependabot bumps, hand-written fixes, and follow-ups from another PR's review
go through the same gate with no exemption, since an exempt PR is one nobody
confirmed was ready. If the addendum declares a stage substrate, record the
skipped planning stages as not-applicable before checking review, so its
ordering checks see an honest answer.

Dependabot (`author.is_bot` with login `dependabot` or `app/dependabot`, plus a
`dependencies` label) rewrites its own PR body when it rebases, silently
dropping a hand-added `Closes #N`. If you added the link, re-read the body just
before merging and re-apply it if it's gone.

## Merge

Only after every check passes:

1. If the addendum declares a merge-authorization file or hook, create the
   authorization exactly as specified. Creating it without having run the gate
   defeats the guard.
2. `gh pr merge {PR} --squash`
3. Delete the authorization file on every path: success, failure, or error. A
   stale one lets the next merge skip the gate.

If the merge command fails (for example branch protection changed since you
checked), report the error and stop; don't retry blindly.

Then run any addendum post-merge steps. Run each to completion and read its
result in this turn. This skill often runs in one turn, so nothing
will wake you later for a backgrounded command: if you must background
something, poll it until it exits before you finish.

If you were dispatched by an SDLC supervisor with a run identity and the
addendum (or the supervisor) names a stage-marker command, write the MERGE
`in_progress` marker at the start and `completed` after the merge. A failed
marker write is reported, never a reason to block.

## Report

Say what you merged or which precondition failed, with its value. End
with an OUTCOME line, which the do-sdlc skill parses:

- Merged: `<!-- OUTCOME {"status":"success","stage":"MERGE","artifacts":{"pr_url":"<URL>"}} -->`
- Refused or failed: `<!-- OUTCOME {"status":"fail","stage":"MERGE","artifacts":{}} -->`
