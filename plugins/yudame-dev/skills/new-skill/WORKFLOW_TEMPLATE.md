# Workflow Skill Template

Skeleton for a skill that captures a repeatable multi-step process, the shape [SESSION_CAPTURE.md](SESSION_CAPTURE.md) produces. Reference skills use [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md) instead.

```markdown
---
name: {{skill-name}}
description: {{what it does, then when to use it, with trigger phrases}}
allowed-tools: {{space-separated minimum patterns, e.g. Bash(gh:*) Read rather than Bash}}
argument-hint: "{{only if it takes arguments}}"
context: {{fork, only if it needs no mid-course input; omit for inline}}
---

# {{Skill Title}}

`$ARGUMENTS`: {{what the input is and its default}}; if empty or literal, use what followed the skill name in the message (omit if no input)

**Done means:** {{the end state, as artifacts someone can check: "an open PR with CI green", not "write code"}}

## Constraints
- {{each hard rule, with its reason; user corrections from the reference session belong here}}

## Steps

### 1. {{Step name}}
{{What to do and anything non-obvious about doing it: the exact command, the format, the trap.}}
**Done when:** {{the evidence that lets the next step start}}

### 2. {{Step name}} [human]
...
```

## Annotations, used only where they carry information

- **Done when** on each step that is not self-evidently finished; it is how the model knows it can move on without checking back.
- **Produces:** data later steps need (PR number, commit SHA, an ID).
- **Execution:** `subagent` for a self-contained piece of work, or `parallel` with sibling steps numbered 3a, 3b. Default is direct; without subagents, both run directly in sequence.
- **Checkpoint:** pause for the user only before irreversible or outward-facing actions (merging, sending, deleting) or where judgment is genuinely theirs. Everything else runs through.
- **`[human]`** in a step title when the user has to do it.

Keep simple workflows simple: a two-step skill needs a goal and two short paragraphs, not every annotation. When a step only restates what any competent engineer would do, cut it and keep its "done when."
