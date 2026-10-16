---
name: build-agent
description: "Stage, launch, grade, and schedule a Claude Managed Agent in a client's account from a build-sheet. Use for 'build the agent'."
allowed-tools: Read Write Edit Glob Grep Bash AskUserQuestion
argument-hint: "[path/to/build-sheet.json or agent-slug]"
---

# Build Agent

**Goal:** a live Claude Managed Agent in the client's Anthropic account, scoped to their repo, that has passed a graded run against its rubric and, if it repeats, is scheduled and test-fired. The client leaves with the agent running in their Console, a resumable launch script, saved eval cases, and a clear list of what comes next.

The input is a **build-sheet** (`./<slug>/build-sheet.json`), written by the imagine-agent skill after a non-technical client interview, or by this skill itself. Its schema and validation checklist are in [references/build-sheet.md](references/build-sheet.md). The CMA API (headers, endpoints, payload shapes, launch order, limits) is in [references/cma-primitives.md](references/cma-primitives.md). Read it before the first curl: two footguns have each cost a debugging loop. Auth is `x-api-key`, not `Authorization: Bearer` (Bearer returns a 401 on a valid key), and every live-events POST body is wrapped as `{"events": [...]}`.

## Before building

- **Right account.** Every CMA lives in one Anthropic account, always the client's (`meta.ownership == "client_account"`; Yudame is just another client). The agent, its sessions, and its bill land wherever the key points, so confirm the key belongs to `meta.workspace` before creating anything. Read the key from a `.env` in the working folder (chmod 600), not chat. If an exported `ANTHROPIC_API_KEY` belongs to the right workspace, reuse it; otherwise ask once, with a small table of step, where, and what to do.
- **Smoke test.** Both must return 200:
  ```bash
  curl -s -o /dev/null -w "auth %{http_code}\n" https://api.anthropic.com/v1/models \
    -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01"
  curl -s -o /dev/null -w "cma  %{http_code}\n" https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01"
  ```
  A 401 is almost always the header or a dead key. A 403 on `/v1/agents` means the account lacks the managed-agents beta; stop and tell the human.
- **Build-sheet.** Read the one `$ARGUMENTS` points to (a path, or a slug meaning `./<slug>/build-sheet.json`; if empty or literal, use what followed the skill name in the message) and validate it. With none, run a short technical interview (model, tools, rubric, schedule, connectors; one question with 2-4 options for enumerable choices) to write one. This is the fast path for a technical operator.

## Build

Narrate each API call in a sentence and post a checkpoint line with the Console link as each object comes up (`platform.claude.com/workspaces/<workspace>/agents/<id>`), e.g. `✅ 🤖 agent agent_… (v1, <model>)`.

1. **Stage** (no key needed). Project the build-sheet into `agent.json`, `environment.json`, `outcome.md`, `first_prompt.txt`, `kickoff.json`, `deployment.json` if scheduled, and `evals/`; check every JSON parses. Write `LAUNCH.md` as a resumable sequence, one API call per step, each reading `IDS.env` first and skipping objects that already exist. Write a `.gitignore` with `.env` and `*.txt`, because the key and the client's raw inputs must never be committed.
2. **Launch** in the order in cma-primitives: resolve `PICKED-AT-LAUNCH` from `GET /v1/models` to the newest Opus-class slug (Sonnet if the sheet prioritizes speed or cost), then environment, agent (pinned slug), vault if there are connectors, session with the repo as a resource, and the `user.define_outcome` kickoff with `max_iterations: 3`. Save every ID to `IDS.env` as it is created. When polling the session, run the first poll in the foreground and confirm it parses before backgrounding it; a poller that fails silently wastes the whole wait.
3. **Grade and iterate.** When the run idles, read the grader's verdict (`outcome_evaluations[].result` and explanation), then fetch the outputs (`GET /v1/files?scope_id=$SESSION_ID`) and grade them yourself against `outcome.md` and the known-good answer, in a table of criterion, verdict, evidence. The grader can be wrong; read the output. Change one thing per iteration: a sharper rubric means a new session; instructions, tools, or skills mean an agent update (same ID, new version); a tighter task means editing `first_prompt.txt` and re-kicking. Once a version passes, run the held-back eval cases (`evals/run-evals.sh`, one session per case, pinned agent version) into `evals/results-v<N>.json`. With no golden set yet, save the verified winning output as `evals/case-01/expected`.
4. **Schedule**, only if it repeats on a clock. A deployment replays the same `initial_events` every run, so first strip any literal date from the kickoff. Create the deployment (cron, timezone, kickoff), then `POST /v1/deployments/:id/run` to test-fire before trusting cron, and read back `upcoming_runs_at`. Event-driven: put the single session-plus-kickoff curl their backend needs into `NEXT-DIRECTIONS.md`. On demand: `LAUNCH.md` is the interface; confirm it reruns from a clean terminal.
5. **Close out.** Regenerate `agent-overview.html` with live IDs and status Launched. Finish `NEXT-DIRECTIONS.md` with every deferred item as what, why, how, slotted into v1, v2, including "re-run evals before promoting a new agent version to a deployment." Sweep: key only in `.env`, no literal dates in any deployment, case-01 saved, no raw client inputs committed.

## When a step keeps failing

After two failures on the same step, drop one rung and tell the human in a sentence: recheck the call against cma-primitives and the live docs and retry once; do the step in the Console UI; fall back to the closest known-good config; and if CMA itself is unreachable, build the same design as a local agent workflow with an `AGENTS.md` or `CLAUDE.md` so the client still leaves with a working assistant, making the CMA launch v1.

## Working folder

```
./<agent-slug>/
├── build-sheet.json        # source of truth
├── agent.json  environment.json  outcome.md  first_prompt.txt  kickoff.json
├── deployment.json         # if scheduled
├── evals/{case-01/{input,expected}, run-evals.sh, results-v<N>.json}
├── agent-overview.html  NEXT-DIRECTIONS.md  LAUNCH.md
├── IDS.env                 # every created object's ID (resumable launch)
├── .env                    # chmod 600, client's API key, never committed
└── .gitignore              # .env, *.txt
```
