---
name: do-integration-audit
description: "Audit a named feature's wiring: orphan code, dead paths, missing tests, config gaps. Use for 'audit this feature's integration'."
allowed-tools: Read Grep Glob Bash Agent
argument-hint: "<feature-topic> [--path <dir>] [--severity critical|warning|info]"
disable-model-invocation: true
---

# Feature Integration Audit

Find the gaps between "the code exists" and "the feature works end to end" for one named feature. A feature can be present but unreachable, tested only with mocks, or documented without its entry points. The deliverable is a report in which every finding survives verification. This is read-only: never modify source files; the human decides fixes.

Arguments: `<feature-topic>` (a semantic label such as "authentication" or "billing", not a path), optional `--path <dir>` to scope the search, optional `--severity` to drop findings below a threshold.

## Map the feature

The topic is a label, so discovery has to be creative. Search for the name and its synonyms in filenames, symbols, comments, and docs; trace what imports the implementation files (this is what shows reachability); find the routes, CLI commands, event handlers, jobs, and menu items that expose it; find the env vars, settings, and flags that control it; find its tests, telling unit tests (mocked, isolated) from integration tests (real wiring); and find its docs.

Classify each file as one or more of: implementation, entry point, test, documentation, configuration, migration. If discovery turns up fewer than three files, the feature may not exist under that name; check with the user before going further.

## The 12 checks

| Check | Severity | What it means, and how to confirm |
|---|---|---|
| orphan-code | CRITICAL | Implementation nothing in the application imports or references; it ships but never runs. Trace imports from the implementation files back to an entry point or app code. |
| dead-entrypoint | CRITICAL | A route, command, or handler that isn't registered in the router, CLI group, event bus, or scheduler, so users can't reach it. Confirm the path from app startup to the entry point is unbroken. |
| partial-wiring | WARNING | Some paths work while others are stubbed: `TODO`, `FIXME`, `NotImplementedError`, bare `pass` in non-trivial methods, commented-out blocks. Ignore stubs in tests. |
| missing-integration-test | WARNING | No test drives the real path from entry point to side effect. Mocked unit tests don't count; they can't catch wiring failures. |
| undocumented-entry | WARNING | An entry point with no README section, doc page, API doc, CLI help, or public docstring. |
| config-gap | WARNING | A config read with no default and no "required" documentation, or missing from example config and setup docs. Works on the developer's machine, fails on a fresh deploy. |
| stale-reference | WARNING | Code outside the feature using old names, removed APIs, or wrong paths that still import but misbehave. |
| inconsistent-interface | WARNING | The same operation named, ordered, or shaped differently across API, CLI, SDK, and internal calls (`create_user` in one, `add_user` in another). |
| non-reusable-interface | WARNING | No clean core or service layer that entry points share: transport types (a request object) leak into core logic, or each entry point reimplements the logic. |
| internal-naming-drift | WARNING | One concept with several names inside the feature (`subscription` in the model, `plan` in the service, `membership` in the template). |
| external-naming-drift | WARNING | Other systems refer to the feature inconsistently in foreign keys, config prefixes, import aliases, log messages, URL segments. Worst in database columns, where it becomes permanent. |
| missing-error-boundary | INFO | Exceptions from feature internals can escape into the caller's context (a request, a command, a job). Ignore cases a global framework handler covers. |

## Verify before reporting

Notes taken early in an audit go stale: line numbers shift, hypotheses form before every file is read, and static reads get mistaken for runtime behavior. After drafting findings, go back and prove each one as a separate pass. These are the ways past audits went wrong:

- **Stale line numbers.** Re-open every cited `file:line` with Read and confirm it still says what the finding claims.
- **Local-scope negatives.** "Nothing handles X", "no test covers Y", "nothing imports Z" need a project-wide search. Watchdogs, hooks, monitors, migration scripts, and sibling services often handle the concern from outside the feature's directory.
- **Static-to-dynamic reasoning.** "A calls B" doesn't prove B executes; it may early-return on a guard, flag, or idempotency check. For "runs twice", "never called", or "silently drops data", trace the actual function bodies. If the code alone can't prove it, mark the finding suspected or drop it.
- **Contradictions within one report**, such as "saved only by idempotency" next to "runs side effects twice". Keep the one the code supports.
- **Hypothesis-confirming search.** For each claim, run the search that would prove you wrong.

Drop findings that don't survive; a smaller correct report beats a larger overstated one. When a finding survives in a changed form, say so inline ("draft claimed X; verification showed Y"). For each CRITICAL finding that survives, give a fresh subagent only the claim and its location and ask it to disprove it, returning PASS, FAIL, or REVISE with reasons; without subagents, set your notes aside and re-read only the cited code.

## Report

```
## Integration Audit Report: {feature-topic}

### Discovery
Found N files across M surfaces: implementation N, entry points N (routes/CLI/events),
tests N (unit N, integration N), docs N, config keys N, migrations N

### Integration Map
| Surface | File | Status |
|---------|------|--------|
| entry point | path/to/route.py:45 | connected |
| implementation | path/to/service.py | orphaned |

### Findings
#### CRITICAL
#### WARNING
#### INFO

### Summary
PASS: N  WARN: N  FAIL: N
```

Each finding names its check, cites `file:line` evidence, and states the runtime consequence:

- [orphan-code] auth/backends.py: Custom auth backend is never used. AUTH_BACKEND defaults to ModelBackend, not TokenBackend, so the code ships but never runs.
- [config-gap] SEARCH_TIMEOUT: read in engine.py:12 via os.environ.get() with no default; missing from .env.example. Silently misconfigured on fresh deploys.
- [missing-integration-test] Only 1 of 5 tests exercises the real auth flow; the other 4 mock the backend, so none can catch the orphaned backend above.

Close with suggested order (critical first, since they mean the feature isn't actually working; warnings in a follow-up; info as opportunities) and stop for the human to decide.
