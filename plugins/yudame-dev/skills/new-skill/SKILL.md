---
name: new-skill
description: "Create a skill or subagent, or capture this session's process as one. Use for 'new skill', 'skillify', or 'save this workflow'."
allowed-tools: Read Write Edit Glob Grep Bash
argument-hint: "<skill-name>"
disable-model-invocation: true
---

# New Skill

**Goal:** a skill (or subagent) that loads when it should, and tells a capable model the outcome, what good looks like, and the real constraints with their reasons. Write one for knowledge the model lacks (exact commands, file formats, edge cases that bit before, standing preferences), not to script steps it would take anyway.

Pick the starting point:
- A reference or how-to skill: the skeleton in [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md).
- A repeatable multi-step workflow: [WORKFLOW_TEMPLATE.md](WORKFLOW_TEMPLATE.md).
- Capturing what was just done in this session ("skillify"): follow [SESSION_CAPTURE.md](SESSION_CAPTURE.md).
- A Claude Code subagent: see "Subagents" below.
- Current field specs or a canonical example (agentskills.io is the shared standard): the bundled references in the audit-skills skill (`../audit-skills/references/anthropic-skills-docs.txt`, `../audit-skills/references/anthropic-skill-creator.md`).

## Where it goes

Claude Code, Codex and Pi all read the Agent Skills format; they differ in where they look and how a user calls a skill.

| Scope | Claude Code | Codex and Pi |
|---|---|---|
| This repo only | `.claude/skills/<name>/` | `.agents/skills/<name>/` |
| Personal | `~/.claude/skills/<name>/` | `~/.agents/skills/<name>/` (Pi also `~/.pi/agent/skills/`) |
| Shared plugin | `plugins/<plugin>/skills/<name>/` in the skills repo | the same directory, linked into `~/.agents/skills` by its `install.sh` |

Claude invokes `/<name>` (`/<plugin>:<name>` from a plugin), Codex `$<name>`, Pi `/skill:<name>`. So in a skill body, call a sibling by name in plain words ("run the do-test skill"), never by one harness's syntax, and name the action rather than a Claude tool ("ask the user one question with 2-4 options"). Where a step uses a subagent, add one sentence for a harness without subagents (Pi): do it yourself in sequence, and for a fresh-context review re-read only the artifact. Say "this skill's directory", not a Claude path variable. Default to the plugin for anything wanted in more than one repo. The directory name must equal `name` (lowercase, hyphenated). Test in a fresh session.

## Writing the description

The description is all the model sees when deciding to load the skill, and every installed description shares one context budget. Say what the skill does, then when to use it, with the phrases a user would type and their synonyms ("check", "review", not only "audit"). Aim under 200 characters; 1024 is the limit.

- Good: `Cherry-pick a merged PR onto a release branch. Use on 'cherry-pick to release', 'CP this PR', 'hotfix'.`
- Bad: `A tool for making skills.` (no trigger), `I help you create skills.` (first person, no trigger)

## Writing the body

- Lead with the goal and the done condition; steps only where order matters.
- Give the reason with each constraint: a model that knows why handles the edge cases. One calm statement beats ALL CAPS.
- Keep hard-won specifics verbatim: commands, schemas, error strings, gotchas.
- Put human checkpoints only before irreversible or outward-facing actions; otherwise let it run.
- Keep SKILL.md under about 500 lines. Move large references and templates to sibling files linked with a line on when to read each; put deterministic work in `scripts/`. Use relative links so the skill works in any scope.

## Field constraints

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Must match directory name. Lowercase, hyphenated. |
| `description` | Yes | Max 1024 chars. What it does, then when to use it, with trigger phrases. |
| `allowed-tools` | No | Space-separated tools Claude may use without a prompt, such as `Read Bash(git:*)`; no spaces inside a pattern. Only what it needs. |
| `compatibility` | No | Set to the harness (`Claude Code`) when the skill only makes sense there. |
| `disable-model-invocation` | No | Claude only: `true` stops auto-loading; for side effects or a costly false trigger. Codex ignores it, so also add `agents/openai.yaml` with `policy:` / `allow_implicit_invocation: false`. |
| `user-invocable`, `context`, `agent`, `model`, `hooks` | No | Claude only: hide from the slash menu, `fork` into a separate context (with that subagent type), pick the model, scope hooks. Others ignore them. |
| `argument-hint` | No | Claude autocomplete hint for `$ARGUMENTS`. A body that reads `$ARGUMENTS` says: if empty or literal, use what followed the skill name in the message. |

## Subagents

Claude Code subagents live in `.claude/agents/<name>.md` (or the plugin's `agents/`):

```markdown
---
name: auditor
description: "Read-only reviewer that inspects code and reports findings. Use when a second opinion is needed without edits."
model: sonnet
color: cyan
disallowedTools: Write, Edit, NotebookEdit
---

What it is for, what it returns, and what it must not do, with reasons.
```

For a read-only agent, prefer `disallowedTools` over a `tools:` allowlist, which also cuts off every unnamed tool (MCP, deferred).

## If it does not load

Check, in order: `name` matches the directory; the frontmatter is valid YAML; the description has the user's words; the file is in a location that harness scans; `disable-model-invocation` or `agents/openai.yaml` is not hiding it from auto-load; the session was restarted.
