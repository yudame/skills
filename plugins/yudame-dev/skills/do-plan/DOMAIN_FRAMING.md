# Domain Framing

There are no standing specialist agents. When a plan task needs domain expertise, assign a general builder (or a reviewer for review-only work), add a `Domain: <tag>` line to the task, and paste the matching rules below into the task's assignment. The do-build skill reads the tag to inject the same rules, and reviewers use it to know what to check.

These are only the rules a strong general model tends not to apply unprompted. The repo's own conventions (its AGENTS.md or CLAUDE.md, contributing docs, enforced hooks) take precedence and are not restated here.

## `Domain: async` (concurrency, event loop)

- Bound fan-out with a semaphore; never run an unbounded `gather` over a dynamic collection.
- Keep a reference to every `create_task(...)` for its lifetime; an unreferenced task can be garbage-collected mid-flight.
- Install a loop exception handler so fire-and-forget failures surface instead of vanishing.
- On shutdown, cancel outstanding tasks and await them; `CancelledError` there is expected, not an error to log.
- Put a timeout on every await that can block indefinitely (network, Redis, LLM calls, locks).
- In long in-coroutine loops, `await asyncio.sleep(0)` between batches so the loop is not starved.
- Wrap a dependency that can stay down long enough to pile up blocked coroutines in a circuit breaker, with exponential backoff and jitter.

## `Domain: redis-data` (Redis, Popoto models)

- Popoto indexes are not retroactive: after adding `Field(indexed=True)`, run `rebuild_indexes()` so existing records become queryable.
- Redis has no joins, foreign keys, constraints, or cascades. Model relations as explicit id fields with query helpers, and enforce enums, bounds, and cascades in application code.
- Prefer a model TTL (`Meta.ttl` in Popoto) for time-based expiry over a bespoke archive-then-delete job.
- Index rebuilds and storage-shape changes must be idempotent and safe while live workers read and write the same keys.

## `Domain: security` (untrusted input, secrets, subprocess)

- Inbound user or channel messages cross a trust boundary: their text never becomes shell arguments, file paths, or instructions without sanitization.
- Build subprocess calls from dynamic input as an argument list, never a shell string; reject shell metacharacters.
- Confine any message- or model-supplied path to an allowed base directory; reject `..` and absolute paths.
- Scrub secret-shaped strings (API keys, tokens, private-key headers, JWTs) before logging. Load secrets from the repo's secret store and validate required keys at startup.

## `Domain: debugging` (leaks, deadlocks, repro)

- For memory growth in a long-running process, `gc.collect()` and diff object counts by type across a workload window; look for types growing into the thousands rather than watching RSS alone.
- For hangs, enable `loop.set_debug(True)` with `slow_callback_duration`, and log lock acquire/release with caller identity to expose circular waits.
- When tests pass but the bug reproduces, find the mock hiding reality and add an integration test on the real path before fixing.

## `Domain: api-integration` (external APIs, MCP tools)

- Derive tool schemas from function signatures and type hints so they cannot drift from the implementation.
- Keep MCP servers stateless: pass user and session context per request.
- Give each tool call its own timeout and report a timeout as a distinct error.
- Map status to retry deterministically: 429 backs off for the exact retry-after the API gives; 401 refreshes auth then retries; 5xx goes through a circuit breaker; other 4xx never retries.
- Never cache errors, mutations, or user-specific data in a shared cache.
- Prune long conversation context by tier (keep system messages and a recent window, keep important middle messages selectively), not by blind truncation.

## `Domain: testing` (user-facing text, async side effects, AI judges)

- For any user-text field, test a hostile-string battery: unicode and emoji, 10k-character overflow, injection strings, null bytes, mixed `\n\r`, not just empty or None.
- For async side effects, poll with an `assert_eventually(condition, timeout)` helper instead of a fixed sleep, assert the side effect actually landed, and assert open sessions or handles return to zero.
- Score AI-judge tests against named criteria and a confidence floor (for example `confidence > 0.8`), not a single boolean.
- Format long chat replies with progressive disclosure: show the head, collapse the middle with an explicit "... and N more ..." marker, and name how to see the rest.
