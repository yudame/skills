---
name: do-patch
description: "Make a targeted, verified fix for failing tests or PR review findings and commit it. Use for 'patch this' or 'fix the failures'."
argument-hint: "<description-of-what-to-patch>"
---

# Do Patch

You make a surgical fix to a specific failure or set of review findings,
prove it in this environment, and commit it. You don't plan features,
refactor neighbouring code, open PRs, or create worktrees: work in the current
directory (run `pwd` once and note it). If the right fix needs an
architectural change, stop and report that rather than attempting it.

The argument describes what to fix: test output, a review comment, or a short
summary. If it's empty or the literal `$ARGUMENTS`, take whatever followed
`/yudame-dev:do-patch` in the user's message, or the most recent test failure or review
in the conversation. If there's nothing to go on, ask what's failing.

## Repo-specific rules

If the repo has a patch addendum (for example `docs/sdlc/do-patch.md`), read it
and follow it. It may declare the branch-to-plan-doc convention, the test and
lint commands, a plan-checkbox updater, cross-repo `gh` targeting, or a
restart needed after patching. Without one, use `git`, `gh`, and the repo's own
test runner.

## Recover the intent before fixing

A fix that makes the test pass but drifts from what was meant to be built is
not a fix. Before editing, gather:

- **The plan**, if the repo keeps plan docs: use the path you were given, or
  derive it from the branch. Note the goal, acceptance criteria, no-gos,
  architectural decisions, and relevant files.
- **The tracking issue** (`gh issue view N`).
- **What the branch has done so far**: `git log --oneline main..HEAD` (use the
  real base branch).
- **For review findings, the actual review**, not just the summary you were
  handed, which often drops items:

  ```bash
  PR=$(gh pr list --head "$(git rev-parse --abbrev-ref HEAD)" --json number -q '.[0].number')
  gh api repos/{owner}/{repo}/pulls/$PR/reviews --jq '.[] | select(.state != "APPROVED") | {user: .user.login, state: .state, body: .body}'
  gh api repos/{owner}/{repo}/pulls/$PR/comments --jq '.[] | {path: .path, line: .line, body: .body}'
  gh pr view $PR --comments   # self-authored PRs carry the review as a "## Review:" comment
  ```

If there's no plan (a hotfix, say), work from the failure alone and say so in
your report.

## Fix

Find the root cause before choosing a fix. For a one-component bug with an
obvious cause (typo, missing import, off-by-one), just fix it. When the failure
crosses components or the cause isn't obvious, trace the data from input to
expected output, find the boundary where the actual values diverge, write a
test that fails for that reason, fix it, and re-run the trace. If tests pass but
the bug is real, look for mocks hiding the real behaviour and add a test that
exercises the actual path.

Every review finding gets a visible disposition, not just blockers: tech debt
and non-subjective nits are fixed too. If a finding should stay as it is (a
style nit in legacy code, a suggestion that contradicts the plan), leave an
inline comment at that spot, such as
`# NOTE: <finding> -- left as-is because <reason>`, so the next reviewer sees a
decision rather than a miss. If a fix would violate a plan no-go or
architectural decision, report the conflict instead of making it.

You can make the fix yourself or hand it to one subagent; for anything beyond a
few lines, a subagent with clean context often does better. If you delegate,
give it everything above (plan, issue, branch history, full failure text, full
review comments, the CWD), and tell it to make minimal edits, not to commit,
and to report what it changed. One fixer, not a team.

If the repo keeps plan checkboxes, note which acceptance criterion (exact text)
the fix satisfies, if any. Cosmetic fixes never tick a criterion: lint or
formatting, test-only changes covering existing behaviour, comments or
docstrings, typos, generated files. When unsure, tick nothing; the next review
will.

## Verify in this environment

Run the repo's test suite and lint yourself (the addendum names the commands;
otherwise the standard runner, plus `ruff check` / `ruff format --check` for
Python when available). Don't route through `/yudame-dev:do-test`; it's heavier than a
patch needs. Exit 0 with lint clean is a pass, and "no tests collected" (pytest
exit 5) counts as a pass. Execution errors (pytest exit 2) are failures.

A count a subagent or earlier stage reported is a claim, not a measurement.
Its environment can differ from yours: a venv missing optional dependencies
silently deselects whole test files, and type-checker error counts move with
stub versions. Report what you measured, including the number of tests that
ran, so a shrunken suite shows up as shrunken rather than green. If your number
disagrees with theirs, say both and which environment produced which. A delta
("no new failures") needs a baseline you measured the same way; without one,
report the absolute number and say the baseline is unmeasured.

## Commit

Commit only after tests pass, so a failing fix never produces a commit. Make it
one fresh commit (never `--amend`) and push to the current branch:

```bash
git add -A
git commit -m "fix: <summary>"
git push origin "HEAD:$(git rev-parse --abbrev-ref HEAD)"
```

If the plan has a criterion to tick, include that edit in the same commit, using
the addendum's checkbox updater if it declares one. A separate "tick the plan"
commit pushed after a review makes that review stale and forces another round,
which is exactly the oscillation to avoid. A failed tick (ambiguous or no match)
is not fatal; commit the code change anyway.

If the repo runs a lint-fixing pre-commit hook, let it run on the final commit
rather than hand-fixing lint; `--no-verify` is only for intermediate WIP
commits. Without such a hook, run lint once before committing and fix what it
reports.

You own this commit. Delegated fixers don't commit, and no caller commits on
your behalf. Stage advancement belongs to the caller, not to this skill.

## When it still fails

Retry with both the original and the new failure output, up to 3 attempts for
the same failure by default (the caller may pass `--max-iterations N`). At the
cap, stop and report:

```
PATCH STUCK ({N}/{CAP} attempts)
Original failure: <summary>
Current failure: <key lines>
Tried: <one line per attempt>
Root-cause hypothesis: <why the fixes aren't landing>
Needs a human or a different approach.
```

On success, report the fix and why, each file changed with a one-line reason,
and the measured test result.
