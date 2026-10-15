# Post the Review

The posting half of `/yudame-dev:do-pr-review`: turn the verdict into a GitHub review,
make sure it landed, and get its URL.

## Identity

Post under the operator's `gh` credential unless the addendum declares a bot
review identity. If it does, resolve the bot token before posting and use it
only for the review-posting calls (`env GH_TOKEN="$TOKEN" gh ...`); read-only
queries keep the operator's credential. Never pass an empty `GH_TOKEN` to `gh`,
which corrupts the stored credential. Put the addendum's review marker as the
first line of code-review bodies, but not on conflict or closed comments, which
aren't code verdicts.

## Which call

GitHub won't let you approve or request changes on your own PR, so check:

```bash
[ "$(gh pr view $PR --json author --jq .author.login)" = "$(gh api user --jq .login)" ] && SELF=true
```

First match wins:

1. `PR_CLOSED` or `BLOCKED_ON_CONFLICT`: `gh pr comment`. `gh pr review` needs an
   open PR and would record a code verdict that was never made.
2. Self-authored: `gh pr comment` with the full review body.
3. Any blocker, tech debt, or nit: `gh pr review --request-changes`.
4. Zero findings: `gh pr review --approve`. This is the only path to approval.

## Body

Order: heading, a short summary, `## Rubric`, the finding sections, then the
optional sections, then the marker. Every finding section appears even when
empty (`- None`), so a reader can tell "checked, nothing found" from "skipped".

```
## Review: Changes Requested            (or "Changes Requested — Tech Debt", or "Approved")

<summary>

## Rubric
- [x] **1. Plan vs implementation** — pass — *notes*
- [ ] **2. New code quality** — fail — *notes*
...                                       (tick only pass and n/a; fail and acknowledged stay visible)

### Blockers
- [ ] **`file.py:42`** — `actual_code()` — description   (full finding blocks)
### Tech Debt
- None
### Nits
- None
### Miscellaneous
- None
### Acknowledged Deferrals (verified)
- **<disclosure>** — tracked by #N (OPEN)
- **<disclosure>** — explicit out-of-scope exclusion, no tracking required

### Review Delta (vs prior review on HEAD <sha7>)   (only if a prior review judged different inputs)
### Verification Results                            (if the plan has a table)
### Legacy Cruft                                    (if any)
### Screenshots                                     (if captured)

<!-- REVIEW_CONTEXT head_sha=<HEAD_SHA> pr_body_hash=<PR_BODY_HASH> -->
```

The marker is how the next run detects unchanged inputs; never omit it. For an
idempotent replay, post just the heading with the prior verdict, the
idempotency note, and the marker.

Conflict comment:

```
## Review: Blocked on Conflict

This PR can't be reviewed until it merges cleanly against its base.

- **mergeable:** `<value>`
- **mergeStateStatus:** `<value>`

Please rebase onto the current base (or merge it in), resolve the conflicts,
push, and re-run `/yudame-dev:do-pr-review`. No code review was performed.
```

Closed comment:

```
## Review: PR Closed

This PR is not open (`state=<STATE>`); review skipped. If it was closed in
error, reopen it and re-run `/yudame-dev:do-pr-review`.
```

## Plan checkbox sync (approvals only)

On an approval, and only then, make the plan's criteria checkboxes match the
rubric before posting: `pass` ticks `[x]`; `fail` and `acknowledged` untick
`[ ]` (closing the dishonest-tick loophole); `n/a` leaves the box alone. Use
the addendum's checkbox updater if it declares one, otherwise edit the plan
file directly. If a criterion matches zero or several plan items, leave it
as-is and add `> Could not auto-sync "<criterion>"; please review manually.`
to the review body. A plan with no criteria section is fine; skip it.

If anything changed, commit and push before posting the review:

```bash
git add "$PLAN_PATH"
git commit -m "docs(#$ISSUE): sync plan checkboxes with review verdict"
git push origin "HEAD:$BRANCH"
```

The order matters. Merge gates treat a review older than the latest commit as
stale, so a tick commit pushed after the approval would immediately invalidate
it and force another review round. If the push fails, don't post the approval
(it would point at a commit that only exists locally); stop and emit
`<!-- OUTCOME {"status":"fail","stage":"REVIEW","verdict":"PUSH_FAILED","artifacts":{},"notes":"tick commit failed to push; review not posted","next_skill":"/yudame-dev:do-patch"} -->`.

## Confirm it landed

```bash
gh api repos/$REPO/pulls/$PR/reviews --jq '.[-1].html_url // empty'
gh api repos/$REPO/issues/$PR/comments --jq '[.[] | select(.body | startswith("## Review:"))][-1].html_url // empty'
```

If neither shows your review, post it again as a comment. Use the URL of what
you just posted as `review_url` in the OUTCOME line.
