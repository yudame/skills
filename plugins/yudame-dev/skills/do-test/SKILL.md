---
name: do-test
description: "Run tests and lint and report a verdict separating regressions from flaky and pre-existing failures. Use for 'run tests'."
argument-hint: "[unit|integration|e2e|tools|performance|<path>|frontend <url> \"<scenario>\"|happy-paths] [--changed] [--no-lint] [--direct]"
---

# Do Test

Run the right tests for the request, then say plainly whether this branch is
safe: what passed, what failed, and for each failure whether this branch caused
it. Only regressions block. This skill is read-only: it runs tests and reports;
fixing is `/yudame-dev:do-patch`'s job.

The workflow is language-agnostic. Use the project's own runner (`pytest`,
`cargo test`, `npm test`, `go test ./...`); [PYTHON.md](PYTHON.md) has the pytest
specifics.

## Find how this repo tests

Before running anything, read the repo's own guidance: CLAUDE.md or AGENTS.md,
an SDLC addendum such as `docs/sdlc/do-test.md`, a Makefile or package scripts,
and any project skill about testing. Repos often wrap the runner (a script that
pins the interpreter, bounds timeouts, or isolates the test database) or forbid
the bare command; the repo's way wins over the defaults here. The addendum can
also declare test tiers, lint commands, a happy-path runner, and quality-gate
thresholds.

## Arguments

`$ARGUMENTS` (if empty or the literal `$ARGUMENTS`, take what follows `/yudame-dev:do-test`
in the invoking message):

| Input | Runs |
|-------|------|
| _(empty)_ | All tests, plus lint |
| `unit`, `integration`, `e2e`, `tools`, `performance` | `tests/<type>/`, plus lint |
| a file or directory | That path, plus lint |
| `--changed` | Tests mapped from files changed on this branch, plus lint |
| `--no-lint` | Skip lint and format checks |
| `--direct` | Run in-process; never fan out to subagents |
| `frontend <url> "<scenario>"` | A browser scenario (see below) |
| `happy-paths` | The repo's declared happy-path runner (see below) |

Flags combine with any target. A test directory that doesn't exist is skipped
silently.

**`--changed`**: diff against `main` (against `HEAD~1` when on `main`), map each
changed source file to its tests (`foo/bar.py` to `tests/*/test_bar.py`; changed
test files run directly; PYTHON.md has the table), and keep only files that
exist. If nothing maps, say so and run lint only. If git fails, run everything.

Run in the current working directory as-is. When `/yudame-dev:do-build` calls this, the
cwd is already the worktree.

## Running

A single target runs directly in this agent. For all tests, run directly too
unless the suite is large (50 or more test files), there is no `--direct`, and
the runner has no built-in parallelism you can use instead (such as
`pytest -n auto`). Then fan out one subagent per test directory, plus one for
lint, all in a single message with `run_in_background: false`. This skill can
run in a one-turn forked context, where a background child's notification never
arrives; same-message foreground calls run concurrently and return together.

Give each fan-out child the exact command and a hard bound, since a hung child
holds the whole run: "finish within 10 minutes; pass the runner's own timeout
flag if it has one (pytest `--timeout=<s>`); if it's still running at the bound,
kill it and report TIMEOUT first with whatever output you have. Report pass,
fail, and skip counts with failure details and the raw output. Don't edit files
or fix anything." If a child errors, times out, or returns anything but test
output, run that group directly yourself and note in the results that it fell
back.

Lint runs after tests using the repo's configured tools (Python default:
`ruff check .` and `ruff format --check .`). Skip cleanly if none is configured.
If the runner itself is missing, report that clearly.

If the plan behind this work describes components wired together (A's output
feeds B), check that at least one test exercises the whole chain, not only each
part alone.

## Special targets

**`frontend`**: dispatch one foreground subagent with browser tools (whatever
browser automation this session has) to run the scenario: URL, scenario, steps
(given after `-- steps:` or inferred), and expected result. It drives the
browser; you don't. When running all tests and `tests/frontend/` holds scenario
files (`{"url", "scenario", "steps": [...], "expected"}` as JSON or YAML), run one
such subagent per file alongside the other suites. Report each with pass or fail
and a screenshot path.

**`happy-paths`**: only when the repo declares a deterministic happy-path runner
and its scenario directory. Run it directly via bash and fold its summary table
into the results. If none is declared, say "no happy-path runner configured" and
skip.

## Report

```
## Test Results

| Suite | Status | Passed | Failed | Skipped | Duration |
|-------|--------|--------|--------|---------|----------|
| unit | PASS | 42 | 0 | 2 | 3.1s |
| integration | FAIL | 8 | 1 | 0 | 12.4s |
| lint | PASS | - | - | - | 0.5s |

### Failures
**tests/integration/test_api_auth.py::test_expired_token**
AssertionError: Expected 401, got 200 (line 45)
```

Keep the raw runner output visible for failures; it is what someone debugging needs.

- Everything passed: run [quality-gates.md](quality-gates.md), then report
  `ALL TESTS PASSED`.
- Anything failed on a branch other than `main`: run
  [baseline-verification.md](baseline-verification.md) before giving a verdict.
  Never call a failure "pre-existing" without running it on `main`.

End with the OUTCOME line the pipeline parses:

- Passed: `<!-- OUTCOME {"status":"success","stage":"TEST","artifacts":{"passed":<N>,"failed":0}} -->`
- Regressions: `<!-- OUTCOME {"status":"fail","stage":"TEST","artifacts":{"passed":<N>,"failed":<N>}} -->`
- Passed with flaky tests, or only pre-existing failures: `<!-- OUTCOME {"status":"partial","stage":"TEST","artifacts":{"passed":<N>,"failed":0,"flaky":<N>}} -->`
- Blocked by the regression circuit breaker or the exception-swallow gate: see those files for the exact shape.
