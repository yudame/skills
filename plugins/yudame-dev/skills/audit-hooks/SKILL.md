---
name: audit-hooks
description: "Audit Claude Code hooks for ones that hang, can't block, or fail silently. Use when checking hook health or after changing a hook."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Hook Audit

**Goal:** for every hook in scope, report PASS, WARN, or FAIL against the rules below, with a specific fix for each WARN and FAIL. The three things that matter: advisory hooks can never block or stall a session, validators really block what they exist to block, and no hook fails without leaving a trace. This audit is read-only; a human applies the fixes.

**Scope:** the `hooks` blocks in `.claude/settings.json`, `.claude/settings.local.json`, and `~/.claude/settings.json`, plus `hooks/hooks.json` in any plugin being audited. Some repos generate these blocks from another file; if so, report fixes against the generator, not the generated output. Check the repo's CLAUDE.md for its validator inventory, logging helper, and hook log path; the defaults below apply when it says nothing.

## How hooks fail

Claude Code reads a hook's exit code. Exit 2 is a blocking error: on PreToolUse it blocks the tool call, on Stop it forces Claude to keep going, and stderr is fed back to Claude. Any other non-zero exit is a non-blocking error shown to the user. A hook that runs past its timeout is killed, but until then the session waits on it. Everything below follows from that.

## Rules

Classify each hook first. A **validator** exists to block bad operations: typically a `validate_*` script on PreToolUse/PostToolUse with a matcher, or anything the repo lists as one. Everything else (logging, tracking, memory, reminders, Stop hooks) is **advisory**.

1. **Advisory hooks end in `|| true`.** It guarantees a crash or a stray exit 2 can never block a tool call or trap a Stop. Missing on an advisory hook: FAIL.
2. **Validators do not end in `|| true`.** It turns their exit 2 into 0, so they never block anything. Present on a validator: FAIL.
3. **Advisory hooks log their own failures.** `|| true` swallows the error, so the script must catch exceptions at the top level and write them somewhere (default: a `log_hook_error()` helper writing `YYYY-MM-DD HH:MM:SS - hook_name - ERROR - message` to `logs/hooks.log`). A bare `main()` under `|| true`: WARN.
   ```python
   if __name__ == "__main__":
       try:
           main()
       except Exception as e:
           log_hook_error("my_hook", str(e))
   ```
4. **The interpreter resolves under `/bin/sh`.** Hooks run through a non-interactive shell with the system PATH, so a bare `python`, or a project CLI that lives only in `.venv/bin`, can exit 127 and silently disable the hook. Reference absolute or `$CLAUDE_PROJECT_DIR`-relative paths. A bare `python` or venv-only command name: FAIL.
5. **Bash hooks use `set +e`, not `set -e`.** Under `set -e` a benign failure (a `grep` with no match) exits the hook early and silently: WARN.
6. **No bare `exec` in bash hooks.** It replaces the shell, so nothing after it can log or recover: WARN.
7. **Python hooks import heavy modules lazily.** Hooks run on every matching event, so a top-level `anthropic`, `openai`, `pandas`, `numpy`, `httpx`, or `pydantic` import (often over 50 ms each) taxes every tool call. Import inside the function that needs it: WARN.
8. **Timeouts fit the work.** Roughly 5 s for file reads and JSON, 10 s for git and local tools, 15 s for network APIs. An empty matcher on PreToolUse fires on every tool call, so a timeout over 5 s there is a WARN.
9. **The hook can actually run.** Every referenced script exists, Python scripts compile, shell scripts are executable, and the logging helper imports from where the hook expects it. Any miss: FAIL.

Finally, if the hook log exists, summarize its last 24 hours: error count, which hooks errored, and the most frequent message.

## Report

```
## Hook Audit Report
Total hooks: 14 | PASS: 11 | WARN: 2 | FAIL: 1

| Hook | Event | Type | Finding | Severity |
|------|-------|------|---------|----------|
| stop.py | Stop | Advisory | `|| true`, logs errors | PASS |
| validate_commit_message.py | PreToolUse(Bash) | Validator | no `|| true` (correct) | PASS |
| calendar_prompt_hook.sh | UserPromptSubmit | Advisory | missing `|| true` | FAIL |
| memory_recall.py | PreToolUse("") | Advisory | timeout 15s on empty matcher | WARN |

Hook log (24h): 3 errors, all memory_recall.py: "ConnectionRefusedError"

### Fixes
- calendar_prompt_hook.sh: append `|| true` to the command in .claude/settings.json.
- memory_recall.py: narrow the matcher or cut the timeout to 5s.
```
