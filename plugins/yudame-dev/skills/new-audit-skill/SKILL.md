---
name: new-audit-skill
description: "Create a new audit skill that checks part of a codebase and reports or fixes problems. Use for 'new audit' or 'add an audit'."
allowed-tools: Read Write Edit Glob Grep Bash
argument-hint: "<subject-to-audit>"
---

# New Audit Skill

**Goal:** turn "I want to check X for problems" into an audit skill that produces accurate, actionable findings on its first real run. A template that merely looks right is not done; an audit is done when it has been run on real data, caught the problems the user knows about, and raised no false alarms.

Build it with [AUDIT_TEMPLATE.md](AUDIT_TEMPLATE.md). General skill rules (placement, description, frontmatter fields) are in the new-skill skill. For working examples, read the existing audit skills in this plugin: audit-skills (script-backed, auto-fixes trivial issues), audit-models (prompt-only, report only), audit-hooks (rule checklist), do-design-audit (scored rubric), do-integration-audit (semantic wiring checks).

## 1. Pin down the audit

Get these from the conversation first and ask only for what is missing:

- **Subject and scan target:** what is audited and exactly where it lives (`.env*`, `config/*.py`, CI YAML). An audit with an unbounded target never finishes cleanly.
- **Known problems:** what the user has already seen go wrong. These become the first checks and the test of whether the audit works.
- **Disposition:** report only, auto-fix the trivial and report the rest, or apply everything. Auto-fix only when the fix is unambiguous and touches nothing outside the audited files, and always show what changed. Even an apply-everything audit leaves the changes for a human or its caller to commit rather than committing its own output unreviewed.
- **When it runs:** after certain changes, periodically, before a release. This feeds the description and whether to set `disable-model-invocation: true` (when a false trigger would waste real time; with it, add `agents/openai.yaml` setting `allow_implicit_invocation: false` so Codex agrees).

## 2. Design the checks

Each check gets a kebab-case name, one sentence on what it catches and why that matters, a severity, and a way to decide pass or fail. Good checks:

- **Are verifiable.** "Code quality" is not a check; "public function has a return type" is. If two runs could disagree, the check needs a sharper definition.
- **Stand alone.** Each is useful by itself, and new ones can be added without restructuring. A check with a deterministic part and a judgment part is two checks.
- **Generalize from the known problem.** A missing field seen on one model means checking every model for missing fields.
- **Prefer missing a problem to inventing one.** False positives teach people to ignore the audit. When unsure, lower the severity.
- **Explain the why.** "Functions without docstrings are invisible to the agent, which can't use what it can't discover" lets the model handle edge cases; "ALWAYS add docstrings" does not.

Use three severities consistently: **FAIL** (broken, missing, or dangerous; fix before shipping), **WARN** (drifted or inconsistent; fix soon), **INFO** (worth knowing). Four to eight checks suit a focused audit, eight to twelve a broad one.

## 3. Choose script, prompt, or both

If a check can be written as a regex, a structural test, or an AST walk, put it in `scripts/audit.py` with `--json`, `--fix`, and `--target` flags: it is cheaper, reproducible, and costs no context until run. Checks that need cross-referencing or judgment stay as prose in SKILL.md. Most real audits are a hybrid. Match the instruction style to the check: principles for exploratory judgment, exact procedure for mechanical pass/fail. For more than about ten independent items, have the audit batch them across parallel subagents.

## 4. Name and describe it

`audit-{subject}` for an audit tied to one project's architecture; `do-{subject}-audit` for one that makes sense in any repo (the `do-` prefix groups general audits in autocomplete). The description must catch the words people actually use, which are rarely "audit": include "check", "validate", "review", "scan", "lint", "what's wrong with". Shape: `Audit SUBJECT for PROBLEMS. Use when TRIGGER, or on 'phrase', 'phrase'.`

## 5. Write the report format with real examples

The output section shows two or three realistic findings, not a described format. Every finding carries the check and the item and says expected versus found:

```
#### FAIL
- [missing-key] UserSession: no `project_key` field; sessions are global instead of per-project
#### WARN
- [naming-drift] AgentSession.agent_session_id: 4 other models use `session_id`
Summary: PASS 31 | WARN 1 | FAIL 1
```

Group by severity, FAIL first, always include counts, and show the summary before applying any fix. An audit that auto-fixes and commits lists only what changed; past about five changes, put the detail in a GitHub issue and reference it rather than writing a long commit message.

## 6. Run it before calling it done

Invoke the new audit on the real target. Confirm it finds the right items, catches the known problems from step 1, raises nothing wrong or misleading, and reads clearly enough to act on without opening the skill. Revise and rerun until it does.
