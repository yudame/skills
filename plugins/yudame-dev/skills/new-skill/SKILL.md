---
name: new-skill
description: "Create a skill or subagent, or capture this session's process as one. Use for 'new skill', 'skillify', or 'save this workflow'."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
argument-hint: "<skill-name>"
disable-model-invocation: true
---

# New Skill

**Goal:** a skill (or subagent) that loads when it should, and that tells a capable model what outcome to reach, what good looks like, and the real constraints with their reasons. A skill is worth writing for knowledge the model would not otherwise have: exact commands, file formats, edge cases that bit before, the user's standing preferences. It is not worth writing to script steps the model would take anyway.

Pick the starting point:
- A reference or how-to skill: the skeleton in [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md).
- A repeatable multi-step workflow: [WORKFLOW_TEMPLATE.md](WORKFLOW_TEMPLATE.md).
- Capturing what was just done in this session ("skillify"): follow [SESSION_CAPTURE.md](SESSION_CAPTURE.md).
- A subagent: see "Subagents" below.
- Current Anthropic field specs or a canonical example: the bundled references in `/yudame-dev:audit-skills` (`../audit-skills/references/anthropic-skills-docs.txt`, `../audit-skills/references/anthropic-skill-creator.md`).

## Where it goes

| Scope | Path | Invoked as |
|---|---|---|
| This repo only | `.claude/skills/<name>/SKILL.md` | `/<name>` |
| A shared plugin (every machine and repo that installs it) | `plugins/<plugin>/skills/<name>/SKILL.md` in the skills repo | `/<plugin>:<name>` |
| Personal, this machine only | `~/.claude/skills/<name>/SKILL.md` | `/<name>` |

Default to the plugin for anything the user would want in more than one repo. Refer to sibling skills as `/<plugin>:<name>`, using the plugin that owns them. The directory name must equal the frontmatter `name` (lowercase, hyphenated). New skills are discovered at session start, so test in a fresh session.

## Writing the description

The description is the only thing the model sees when deciding whether to load the skill, and every installed skill's description shares one context budget. Say what the skill does, then when to use it, including the phrases a user would actually type and their synonyms (users say "check" and "review", not only "audit"). Keep it under about 200 characters where possible; 1024 is the hard limit.

- Good: `Cherry-pick a merged PR onto a release branch. Use on 'cherry-pick to release', 'CP this PR', 'hotfix'.`
- Bad: `A tool for making skills.` (no trigger), `I help you create skills.` (first person, no trigger)

## Writing the body

- Lead with the goal and the done condition. Steps belong only where order matters or a step is non-obvious.
- Give the reason with each constraint. A model that knows why a rule exists handles the edge cases; one given a bare MUST follows it into the wrong place. One calm statement beats ALL CAPS and repeated warnings.
- Keep hard-won specifics verbatim: commands, schemas, error strings, the gotcha that cost a debugging loop.
- Put human checkpoints only before irreversible or outward-facing actions (sending, merging, deleting, spending money); otherwise let it run.
- Keep SKILL.md under about 500 lines. Move large references, templates, and examples to sibling files linked from SKILL.md with a line on when to read each; put deterministic work in `scripts/`, which costs no context until it runs. Use relative links so the skill works in any scope.

## Field constraints

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Must match directory name. Lowercase, hyphenated. |
| `description` | Yes | Max 1024 chars. What it does, then when to use it, with trigger phrases. |
| `allowed-tools` | No | Tools the skill may use without a permission prompt; patterns like `Bash(git log:*)` are tighter than `Bash`. List only what it needs. |
| `hooks` | No | Hooks scoped to the skill's lifecycle. |
| `disable-model-invocation` | No | `true` stops Claude auto-loading it; only `/name` works. For skills with side effects or a high cost of a false trigger. |
| `user-invocable` | No | `false` hides it from the slash menu. For background reference skills. |
| `context` | No | `fork` runs it in a separate context. For self-contained work that needs no mid-course input. |
| `agent` | No | Subagent type to use with `context: fork`. |
| `argument-hint` | No | Autocomplete hint when the skill takes `$ARGUMENTS`. |
| `model` | No | Model to use while the skill is active. |

## Subagents

Subagents live in `.claude/agents/<name>.md` (or the plugin's `agents/`):

```markdown
---
name: auditor
description: "Read-only reviewer that inspects code and reports findings. Use when a second opinion is needed without edits."
model: sonnet
color: cyan
disallowedTools: Write, Edit, NotebookEdit
---

What this agent is for, what it returns, and what it must not do, with reasons.
```

For a read-only agent, prefer `disallowedTools` over a `tools:` allowlist. An allowlist also cuts off every tool not named in it (MCP tools, deferred tools), and in some setups a `tools: [Read, Grep]` list was silently ignored.

## If it does not load

Check, in order: `name` matches the directory; the frontmatter is valid YAML between `---` lines; the description contains words the user actually said; the file is in a scanned location; `disable-model-invocation` is not hiding it from auto-load; the session was restarted after creating it.
