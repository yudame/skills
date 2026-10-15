---
name: cowork
description: "Design, review, and maintain Claude Code Routines (scheduled cloud agents). Use for 'set up a routine' or moving a local job to one."
---

# Routines (formerly "Cowork tasks")

A Claude Code Routine is Anthropic's cloud scheduled agent (reference: [code.claude.com/docs/en/routines](https://code.claude.com/docs/en/routines)). Older setups called these "Cowork tasks"; this is not the Claude Cowork desktop app.

A routine has four parts: a **prompt**, one or more **repos** cloned fresh into a cloud sandbox each run, **connectors** (Anthropic-hosted MCP such as GitHub, Slack, Linear), and a **trigger** (schedule, API call, or GitHub event). Each run is an independent Claude Code session that runs even when the user's machine is off. Nothing persists between runs except what the run commits back (by default only to `claude/`-prefixed branches) or writes to an outside system.

The goal of this skill is a routine that runs unattended, does the right thing, and whose failures a human will notice.

## Is it a routine at all?

A routine fits a task that reads a cloud API, applies judgment, and writes to a cloud API. It does not fit a task that needs live local state: a database only this machine can reach, a local process to signal, files outside the repo, or a secret that cannot be handed to a connector or a routine-scoped secret. Those stay on local scheduling. If the repo documents its own rule for this, use it.

## Creating one

Routines are created through the built-in `/schedule` skill or at `claude.ai/code/routines` (needs a Claude Pro or higher account). Whoever creates it, prepare everything needed to make it in minutes, and record it as a committed **routine-spec file** in the repo (for example `docs/infra/<routine-name>.md`) so the cloud object can be audited and rebuilt from git:

- **Prompt.** If a committed skill or recipe already does the judgment, the prompt invokes it and nothing more ("Run `/my-skill --flag` and follow its output"). Restating that logic in the routine prompt creates a second copy that drifts the moment either changes.
- **Repo, connectors, trigger.** Connectors are least-privilege: only what the run uses.
- **Auth.** A routine cannot read local `.env` files or vaults. Prefer a native connector when the catalog covers the service. Otherwise provision a routine-scoped secret at creation; record which secret maps to which env var in the spec, never the value. API-triggered runs need the beta header `experimental-cc-routine-2026-04-01` as of writing; check the docs for the current value.
- **Notification.** A routine has no local relay, so its own output is the signal: a filed GitHub issue, a Slack post. Decide what an actionable run produces and how a human will learn of it.

## Quiet versus broken

A routine that fails (expired auth, connector error, quota) files nothing, and a routine that ran and found nothing also files nothing. From outside they look identical. So "no output" is not evidence of health: maintaining a routine means periodically reading its run history at `claude.ai/code/routines`, looking for expired OAuth or secrets, connector errors in unattended runs (early connectors failed intermittently this way), and drift between the prompt and the recipe it calls (renamed skill, changed flags).

## Migrating a local scheduled job

Keep the local schedule until the routine has completed at least one real, verified run; then remove the local one promptly. Overlap means duplicate side effects such as duplicate issues.

## Review checklist

Before creation and on every change: the prompt delegates rather than re-implements; connectors and secrets are minimal; the notification is explicit; and the committed spec matches the live routine (prompt text, cadence, connectors, secret names). Change the spec in the same commit as any change to the routine, and treat any mismatch as a bug.

Connector-specific setup lives in each connector's own docs. Routines are edited by a human or `/schedule`; the spec file is a record, not something synced automatically.
