# Quality checks after a green run

Run after tests pass, before the OUTCOME line. The exception-swallow gate can
fail the TEST stage; the other checks are advisory notes in the report. Examples
are Python; apply the same ideas in the project's language.

## Exception-swallow gate (blocking)

A handler that catches a broad exception and does nothing hides the failure it
caught; tests stay green while the behavior is broken. So the branch may not add
one silently.

Look only at lines this branch adds (`git diff main...HEAD`, or `HEAD~1` on
`main`). For each new broad catch (`except Exception`, `except BaseException`,
bare `except:`; `catch (e) {}` and the like elsewhere), it passes if either:

- the handler body, within its first three lines, logs (`logger`, `log.`,
  `warning`, `error`) or re-raises; or
- the `except` line carries an inline justification of at least 10 characters:
  `except Exception:  # swallow-ok: safe during shutdown, task already cancelled`.
  A bare or near-empty `# swallow-ok:` doesn't count.

If any new catch fails, list each with file and line, explain the two ways to
satisfy the gate, and end with
`<!-- OUTCOME {"status":"fail","stage":"TEST","artifacts":{"swallow_gate":"failed","new_swallows":[...]}} -->`
instead of a success OUTCOME.

## Stale expected-failure markers

When a bug is fixed, its xfail marker should become a hard assertion.

- Decorator form (`@pytest.mark.xfail`): the runner reports `XPASS` when the
  test now passes. Flag each.
- Runtime form (`pytest.xfail("...")` inside the test body) is worse: it exits
  before the assertion, so the test reports xfail forever and can never show
  the bug is fixed. Find them with
  `grep -rn 'pytest.mark.xfail\|pytest.xfail(' tests/`. For a conditional call,
  check whether the condition still holds; flag an unconditional one for review.
  In `--changed` runs on a bug fix, runtime xfails in related test files are
  blockers, not notes.

Report each as `STALE XFAIL: <file>:<line> (decorator|runtime)` with the
suggestion to remove the marker and assert directly.

## Advisory notes

Mention briefly when they apply to the changed code:

- existing broad catches in the source that neither log nor carry a justification;
- code that processes model or user output with no tests for empty, `None`, or
  whitespace input;
- new nested functions or closures that duplicate logic tested elsewhere instead
  of calling the shared function.
