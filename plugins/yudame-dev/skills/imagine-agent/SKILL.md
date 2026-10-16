---
name: imagine-agent
description: "Interview a client about the agent they want and turn it into a build-sheet for the build-agent skill. Use for 'scope an agent'."
allowed-tools: Read Write Edit Glob Grep Bash AskUserQuestion Agent
argument-hint: "[repo path or url] [client name]"
---

# Imagine Agent

**Goal:** a validated `./<agent-slug>/build-sheet.json` that the build-agent skill can launch from, built so that the client only ever talked about the experience they want. The client approves outcomes in their own words; every technical decision is derived from research into their repo, not asked of them.

This is the client-facing half of a pair. The build-sheet is the only contract between the two skills; its schema and validation checklist are in [../build-agent/references/build-sheet.md](../build-agent/references/build-sheet.md).

## The core move

The build-agent skill's own interview asks semi-technical questions (which sources, what schedule, which connector). This skill answers them from the repo. "My users should get a summary every morning" quietly becomes a model choice, a binary rubric, a cron deployment, the Slack connector the repo already has wired, and a dedup memory store. Only what is genuinely theirs to decide, such as where to receive it, goes back to the client.

## 1. Interview the client about outcomes

Keep it warm and short; where answers are enumerable, ask one question with 2-4 options. Ask only:

- Who is this for?
- What should happen for them?
- What does great look like? (becomes the rubric)
- How often, or when? (becomes the schedule)
- Where do they already work? (becomes the delivery connector)

Record their answers verbatim in the `outcome.*` fields; paraphrase loses what they meant. Words like model, tokens, tools, MCP, rubric, cron, vault, or API never reach the client: if you are about to type one, translate it from research instead. If they volunteer a mechanism, note it and return to the outcome. Raise a limitation only when it constrains their goal, and pair it with the upgrade path ("we can start with X and add Y next").

## 2. Research the repo

Without it you are guessing at what is possible and will over-promise. Point it at the repo in `$ARGUMENTS` (if empty or literal, what followed the skill name in the message; else ask) and record findings in `repo_findings`. For a large repo, run parallel read-only subagents, one per question below, and combine their answers; without subagents, or for a small repo, take the questions yourself in turn.

| Find | Why | Look in |
|---|---|---|
| Capability ceiling | Bounds what can be promised | frameworks, services, data sources, README, package manifests |
| Wired connectors and auth patterns | Decides what ships in v0 versus v1 behind a credential | API clients, MCP config, how secrets load |
| House standards | The agent follows the repo's existing style | `AGENTS.md` or `CLAUDE.md`, `ONTOLOGIES.md`, design system, conventions docs |
| Reusable skills and tools | Reuse rather than rebuild | `.agents/skills`, `.claude/skills*`, package scripts, `tools/` |

## 3. Translate goals into the build-sheet

Justify each technical field with a finding:

- `outcome.cadence` → `schedule` (cron and timezone), or `null` for one-off or event-driven.
- `outcome.delivery` → a `connectors[]` entry: `status: "wired"` if the repo already has it, otherwise `"mock"` for v0 with the real connector as v1 and its credential gate named.
- `outcome.success_looks_like` → three to six binary `rubric.criteria`. The grader is a separate model checking pass or fail, so each criterion must be checkable, not a vibe.
- `outcome.goal` plus capabilities → `agent.system` (the job, what it must never do, "write outputs to /mnt/session/outputs/", relative dates such as "today", because a scheduled run replays the same text every time), `agent.tools` (default to the prebuilt toolset), `agent.skills` (reuse what step 2 found), and `environment` (packages, networking).
- Leave `agent.model` as `"PICKED-AT-LAUNCH"`; the builder resolves it.
- Anything v0 cannot do → `versions.v1`/`v2` with what, why, how, and the gate (not possible, needs a credential, scheduled for later). CMA cannot do real-time, phone, or sub-second behavior, so reshape such goals and offer the upgrade path rather than promise them. Be honest about the ceiling, not underselling.

## 4. Read back, write, hand off

Read the plan back to the client as outcomes: what their users will get, how often, where, and what arrives in v1 and v2. Get approval with one question (looks right, or tweak something); the translation stays invisible. Then write `./<agent-slug>/build-sheet.json` with `meta.ownership = "client_account"`, the client's Anthropic `meta.workspace`, and `meta.repo_url`. Run the validation checklist and hand off by invoking the build-agent skill with the path.
