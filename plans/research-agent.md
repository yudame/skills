# Plan: a deep-research agent in the yudame plugin, run on Cuttlefish's research tools

Request (Tom, 2026-11-01): Valor should have the latest deep-research tools that
Cuttlefish runs, as they are and as they improve, and those tools are complex enough to
belong to purpose-built subagents so the caller never deals with them. Correction
(Tom, 2026-11-01 12:26 UTC), delivered into the plan-stage session of this task as a
steering message while the plan was being written, verbatim: "Not a short brief. I
expected to be quite a long one." with the instruction: "The research agents return a
long, full report, not a short brief: the depth Cuttlefish's master briefing reaches,
with every claim sourced and a confidence per claim. Keep a short summary at the top so
the caller (Valor) can act on it without reading the whole thing, but the full report
is the product, delivered as a document (an A4/Letter PDF when it goes to a person)."
It supersedes the request's "short brief": the product is a long, full report at the depth of
Cuttlefish's master briefing, every claim sourced with a confidence, a short summary on
top so the caller can act without reading all of it, and an A4/Letter PDF when it goes
to a person.

The GitHub issue step of the pipeline is this file: this task can push a branch but not
open issues, and the repository is public, so the plan carries the request in plain
terms.

## What exists today (read 2026-11-01)

Cuttlefish (`yudame/cuttlefish`, private) productized `yudame/research`; the research
repo now holds outputs and methodology only, the tools live in Cuttlefish.

**Six deep-research tools**, `apps/podcast/tools/*_deep_research.py`. Each is a
Django-free module with one function `run_<x>_research(prompt, ...) -> (text | None, meta)`,
where `meta` carries citations and a `cost` blob; each reads one key from the
environment:

| Tool | Function | Key | Typical time |
|---|---|---|---|
| Perplexity `sonar-deep-research` (academic, peer-reviewed) | `run_perplexity_research` | `PERPLEXITY_API_KEY` | 0.5-2 min |
| Gemini Deep Research (policy, regulation) | `run_gemini_research` (submit + poll; defaults `poll_interval=120`, `max_attempts=30`, up to 60 min) | `GEMINI_API_KEY` | 3-10 min, up to 60 |
| OpenAI Responses API with web search | `run_chatgpt_research` | `OPENAI_API_KEY` | 1-5 min |
| xAI Grok | `run_grok_research` | `GROK_API_KEY` | 1-5 min |
| Claude with server-side web search | `run_claude_research` | `ANTHROPIC_API_KEY` | 1-5 min |
| Llama via OpenRouter `:online` (third perspective) | `run_together_research` | `OPENROUTER_API_KEY` | 1-3 min |

**The analysis steps are Named AI Tools** in `apps/podcast/services/`, pure functions
over text with their prompts in `services/prompts/*.md`, running on Claude through
PydanticAI with `ANTHROPIC_API_KEY`:
`craft_research_prompt(brief, title, research_type)` (types perplexity, gpt, gemini,
together; Cuttlefish uses it for Perplexity only), `discover_questions(digest, topic)`,
`craft_targeted_prompts(brief, question_discovery, title) -> TargetedResearchPrompts`
(one call returning `gpt_prompt`, `gemini_prompt`, `together_prompt`, `claude_prompt`,
`grok_prompt`), `digest_research(text, topic)`,
`cross_validate(research_texts, topic) -> CrossValidation` (verified claims from 2+
sources, single-source claims, conflicts, each claim with `confidence`
high/medium/low and its `sources`; source quality; coverage map),
`refute_claims(selected, research_texts, topic)` with
`_select_load_bearing_weak_claims(cv)` (adversarial pass on the weak, load-bearing
claims), and `write_briefing(cross_validation, digests, title, style_guide=...)
-> MasterBriefing` (findings by topic with evidence, quality and sample size;
depth per topic; practical steps; counterpoints; gaps; tiered source inventory).

The episode-bound layer (`services/research.py`, `services/analysis.py`, the
`research-workflow` skill) wraps these in `Episode`/`EpisodeArtifact` rows on the
production database; we do not use that layer. There is no HTTP API or MCP server for
research (`apps/ai/mcp` holds `creative_juices` and `cto_tools` only).

Checked on this Mac: a fresh clone, `uv sync`, then `django.setup()` with
`DJANGO_SETTINGS_MODULE=settings` and no other environment imports all of the above
cleanly, with no database. All six keys are in 1Password vault `m-valor` and each
authenticated on 2026-11-01 (`credential` field; Grok is item `Grok x.ai API Key`,
field `API_KEY`). Nothing to ask Tom for.

## What gets built

All in the `yudame` plugin. The repository is public: nothing below names a client or
carries a key; it names env var names and the Yudame 1Password item references only,
as the README already does for `gws`.

### 1. `plugins/yudame/skills/research/run.py`, the thin runner (about 250 lines)

One command: `run.py "<question>" [--out DIR] [--context FILE]`. It holds no research
logic of its own; every step is a Cuttlefish function.

- **Finds Cuttlefish.** `$CUTTLEFISH_DIR` if set, else a managed clone at
  `~/.cache/yudame/cuttlefish` (`gh repo clone yudame/cuttlefish` the first time,
  `git pull --ff-only` and `uv sync` each run). It never touches a developer's own
  checkout. If the clone or pull fails (no access, offline), it exits non-zero with
  one plain line saying so; the caller falls back to the web agent.
- **Gets keys.** From the environment; any of the six missing is read with `op read`
  from the item references in `keys.env` beside the runner (`m-valor` items). A key
  still missing skips that tool and is named in the report's method section.
- **Re-executes itself inside Cuttlefish's environment** (`uv run --project
  <cuttlefish> python run.py --inner ...`), calls `django.setup()`, and runs:
  1. In Cuttlefish's own order: `craft_research_prompt(..., "perplexity")` with the
     question (and `--context`) as the brief, `run_perplexity_research`,
     `digest_research` on it, `discover_questions` on the digest, then
     `craft_targeted_prompts` for the other five tools (ChatGPT takes `gpt_prompt`,
     Claude `claude_prompt`, Grok `grok_prompt`, Gemini `gemini_prompt`, OpenRouter
     `together_prompt`). No prompt text lives here. If Perplexity is unavailable, the
     targeted prompts are crafted with an empty question discovery.
  2. The five tools in parallel threads, each with Cuttlefish's own timeout parameters
     passed explicitly, not wrapped: Gemini `poll_interval=60, max_attempts=25`
     (25 min), Perplexity `timeout=600`, Grok `timeout=300`, the rest their defaults.
     A tool that errors, returns nothing, or times out is recorded as skipped with the
     reason (`timed out after 25 min`, the error line) in the method section; the
     others carry on.
  3. `digest_research` per result, `cross_validate` across them,
     `_select_load_bearing_weak_claims` + `refute_claims`, then `write_briefing` with a
     style guide that sets the reader as a decision-maker rather than a podcast
     audience (the function's own `style_guide` hook, no prompt copied).
- **Runs detached.** The outer command starts the inner run in the background with
  its output going to `run.log`, writes `status.json` (`{"state": "running" |
  "done" | "failed", "step": "<current step>", "started": ..., "report": <path>,
  "error": <line>}`) and returns at once with the run directory. The inner run
  updates `status.json` at each step. A full run takes 10-35 minutes, longer than
  one shell call may last, so nothing waits on it in one call.
- **Writes** `report.md` and `raw.json` (every tool's text, meta and the structured
  outputs) to `--out` (default `./research/<YYYY-MM-DD>-<slug>/`), and prints the
  report path and the summary.
- Fewer than two tools returning means no cross-validation: the report says so, and
  every claim is single-source at its stated confidence.

The rendering is the only code that is ours: structured Cuttlefish output to markdown.

### 2. Report shape (`report.md`)

1. **Summary**: the answer in a few sentences, then the 3-7 claims that carry it,
   each with its confidence and source links. Enough to act on.
2. **Findings by topic**: from the master briefing, each finding with its evidence,
   source, study quality and sample size.
3. **Every claim**: confirmed by several sources, single-source, and contested (each
   position with its sources); each with high/medium/low confidence, and the outcome
   of the rebuttal pass where one ran.
4. **Where the evidence is thin**: depth per topic, gaps, what is preliminary or
   unknown.
5. **Practical steps** and **counterpoints**, when the briefing has them.
6. **Sources**: tiered inventory with links.
7. **Method**: which tools ran, which were skipped and why, time per step, and cost
   in dollars in two lines that add to a total: the research tools (each tool's own
   `meta["cost"]["total"]`) and the analysis steps (Claude usage of every Cuttlefish
   Named AI Tool, captured with Cuttlefish's `track_usage_to_buffer()` around each
   call, summing its entries' `cost_usd`). A tool that gives no cost figure is named
   as uncounted, so the total is never silently low.

### 3. `plugins/yudame/agents/researcher.md`, the subagent

Frontmatter `name: researcher`, a description that says when to start it (a question
that needs depth, several sources, and a confidence per claim; quick lookups go to the
web agent), `tools: Bash, Read, Write`. Body: start the runner with the question (it
returns at once with the run directory), then check `status.json` every couple of
minutes with a short sleep in each call (each call well under the shell's per-call
limit) until `done` or `failed`, for up to 45 minutes. On `done`, read `report.md`,
check every summary claim appears with a source in the body, and return the summary,
the report path, and what was skipped. It never pastes the full report back. On
`failed` or no Cuttlefish access, it returns the error line and does not research by
hand; the caller falls back to its own web search, or the web agent where the harness
has one.

### 4. `plugins/yudame/skills/research/SKILL.md`

Agent Skills frontmatter (`name: research`, a description with triggers: "research
this", "deep research", "what does the evidence say"). Body: deep path versus quick lookups
(the harness's own web search, or the web agent where one exists) and the rough cost of a deep run; start the researcher subagent
where the harness has subagents, else run the runner directly (Codex, Pi); what the
report contains; when it goes to a person, print it as an A4/Letter PDF by the present
skill's print recipe, run the de-slop skill first; setup (Cuttlefish access, `uv`,
`op`, the six keys). `keys.env` lists the six `op://` references.

### 5. README

The `yudame` row's "Needs" names the research skill's needs (read access to Cuttlefish,
`uv`, the keys); "What's here" lists `research` and the `researcher` agent.

## How it improves as Cuttlefish improves

The runner imports Cuttlefish's functions and prompts from a clone it fast-forwards on
every run. A better prompt, a new model, a fixed tool in Cuttlefish reaches the next
run with no change here. What would need a change here: a renamed or re-signatured
function among the nine we call, or a seventh tool (which the runner picks up only once
added to its tool list). A renamed function fails the run with the import error named,
never silently.

## Out of scope

- The Cuttlefish episode workflow, its database, NotebookLM audio, the
  `research-dossier` person/company path.
- Changing anything in Cuttlefish. If the briefing prompt's podcast wording proves too
  strong for the style-guide hook, that goes to Cuttlefish as its own change.
- The `web` agent: unchanged, still the light path for quick lookups.
- Caching or a hosted service; this runs on the caller's machine.

## Stakes

A plugin every teammate's agent loads, spending a few dollars of shared API credit per
run and putting its claims in front of Tom as evidence, so a wrong confidence or a
silent tool failure costs trust; all of it is reversible by a revert.

Critique rounds: 1. Review rounds: 1.

## Tech debt

- `_select_load_bearing_weak_claims` is private in Cuttlefish; calling it pays the debt
  of re-implementing claim selection here, and costs a break if Cuttlefish renames it
  (named in the error).
- The managed clone in `~/.cache` pays the debt of touching a developer's working
  checkout; it costs one extra clone per machine.

## Tests

`tests/check_research.py` (stdlib, under a second, no network, no Cuttlefish):

- Rendering from a fixture of Cuttlefish-shaped outputs: summary first; every claim in
  the fixture (verified, single-source, both positions of a conflict) appears in the
  body with its confidence and at least one source; refuted claims show the rebuttal
  outcome; the method section names skipped tools with their reason and the total cost.
- Fewer than two tool results: the report states no cross-validation and lists claims
  as single-source.
- A tool returning `None` or raising is recorded as skipped, the others still render.
- Key resolution: environment wins over `op`; a key absent from both skips only its
  tool; `keys.env` holds only `op://` references (no literal key).
- Prompt routing: each of the five targeted tools is handed its own field of a
  `TargetedResearchPrompts` fixture (Claude gets `claude_prompt`, Grok `grok_prompt`,
  ChatGPT `gpt_prompt`, ...), with fake tool functions.
- Timeouts: a fake tool that returns `None` after its attempts is listed as skipped
  with its timeout reason; the Gemini call receives `poll_interval=60,
  max_attempts=25`.
- Cost: the method section shows the research-tools line, the analysis-steps line
  summed from fixture usage entries, and their total; a tool with no cost blob is
  named as uncounted.
- Detached run: the outer command returns within seconds while a fake inner run
  sleeps, `status.json` reads `running` then `done` with the report path; a fake
  inner run that raises leaves `failed` with the error line.
- Cuttlefish location: `$CUTTLEFISH_DIR` wins; otherwise the managed path; the runner
  never runs `git pull` in a directory it did not clone.
- `tests/check_skills.py` passes with the new skill; the agent file has `name`,
  `description`, `tools`.

End to end, in build: one real question (one useful to Yudame, not about any client),
all six tools, started by the researcher agent and polled to completion (a real run
of over 10 minutes is expected with Gemini; its wall time is in the method section),
the report and its PDF kept in the task workspace for the delivery, not
committed. Its method section shows which tools ran and the cost.
