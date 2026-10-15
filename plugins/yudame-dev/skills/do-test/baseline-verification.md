# Failure baseline verification

Use when tests fail on a feature branch. The goal is to classify each failure
with evidence, because "pre-existing" is the easiest false claim to make and
the one that lets a real regression ship.

Skip when on `main` (no baseline), or when more than 50 tests fail (that is a
systemic break, not a set of regressions; report it as such).

## 1. Retry the failures once (flaky filter)

Re-run only the failing test IDs on the branch, for example
`pytest <id> <id> ... -v --tb=short`. Anything that passes on retry is FLAKY:
list it in its own table, it doesn't block, and it doesn't go to the baseline.
Typical causes are timing, resource contention, and nondeterministic LLM-backed
tests. If every failure was flaky, stop here.

## 2. Run the rest on `main`

Check out `main` somewhere that doesn't disturb the branch, such as a temporary
worktree (`git worktree add /tmp/baseline-<id> main`, removed afterwards), and run
the still-failing test IDs there with the same runner and environment. For a long
list, a foreground subagent can do this; give it the IDs and have it return one
row per test.

| Branch | Main | Verdict |
|--------|------|---------|
| FAILED | PASSED | **REGRESSION** (blocks) |
| FAILED | FAILED | pre-existing (reported, doesn't block) |
| FAILED | test doesn't exist or can't run on main | inconclusive (flag for manual review) |

Report it as a table headed `Failure Classification (verified against main at <sha>)`
with counts of each verdict.

## 3. Regression circuit breaker

Stops endless test-patch-test loops. If the invoking context carries
`regression_fix_attempt` and `persistent_regressions` from a previous run's
OUTCOME, compare: the same set of regression IDs increments the attempt; a
different set resets it to 1. With no prior context this is attempt 0.

At 3 attempts with regressions still present, stop treating it as a patch
problem: report status `blocked` with `next_skill: /yudame-dev:do-plan`,
`failure_reason: "Regression fix not converging after N attempts. Escalating to planning."`,
and `persistent_regressions` and `regression_fix_attempt` in the artifacts.

## Verdict

- Regressions present (alone or mixed with pre-existing): `fail`. Include
  `regression_fix_attempt` and `persistent_regressions` in the OUTCOME artifacts
  so the next run can count.
- Only pre-existing, inconclusive, or flaky failures: `partial`.
- Circuit breaker tripped: `blocked`.
