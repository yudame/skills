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

Steering (Tom, 2026-11-01 12:36 UTC), the first real question and two additions:
"a critical review and redesign of what it would be the best prioritization system for
our product persona and product table that lives in Google sheets. I made references to
books and concepts that were important to me and those should be looked at more deeply
and also identify and work in other latest best practices of product owners that I
didn't consider. We expect those deep research tasks to take 25-45 minutes to complete
end to end. And if using the Cuttlefish infra, it can even be published on the Yudame
Research Podcast." So: a run is sized for 25-45 minutes; the caller's document (here a
Google Sheet and the role it serves) goes in as context; and drafting a Yudame Research
Podcast episode from the report is an option, prepared but never published until Tom
has read the report.

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
field `API_KEY`). Nothing to ask Tom for. Found in build: the item `GEMINI_API_KEY` is a
free-tier key that Gemini deep research refuses (429, limit 0); the item
`GOOGLE_API_KEY` is paid and was accepted, so `keys.env` points Gemini at it.

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
  2. Each tool's response read with that tool module's own `extract_metadata` where it
     has one (cost and citations), as `services/research.py` does.
  3. The five tools in parallel threads, each with Cuttlefish's own timeout parameters
     passed explicitly, not wrapped: Gemini `poll_interval=60, max_attempts=30`
     (30 min), Perplexity `timeout=600, max_retries=2` (its sync call retries a
     timeout, so up to 20 min; Cuttlefish's default 3 allows 30, too long ahead of
     the targeted round for Tom's 25-45 minute run), Grok `timeout=300`, the rest their defaults.
     A tool that errors, returns nothing, or times out is recorded as skipped with the
     reason (`no result within 30 min`, the error line) in the method section; the
     others carry on.
  3. Each result goes through Cuttlefish's own per-tool cleanup, as its
     `services/research.py` wrappers do: `safety.filter_research_output(text,
     source=<tool>)` then `research._guard_content_length(text, <label>)` (a result
     under 500 characters becomes a skipped tool with that reason). Its request
     screen (`check_research_request`) is not called: it is a refusal, and adding a
     refusal here is governance with no grant.
  4. The analysis, all from the per-step pure modules (`services/<name>.py`), never
     the `episode_id` wrappers of the same names in `services/analysis.py`, which
     need the database. In the wrappers' order and with their arguments:
     - `digest_research(text, question)` per result, formatted with
       `analysis._format_research_digest` (the text the wrapper stores).
     - `classify_question_resolution(question_discovery=<QuestionDiscovery
       .model_dump()>, research_texts, question)`, its unresolved and partially
       addressed lists formatted as the wrapper does (`## Unresolved Questions`,
       `## Partially Addressed Questions`) into `question_gaps`. Skipped with no
       question discovery.
     - `source_tier.build_source_tiers(<one SimpleNamespace(title, metadata) per
       source>, key_fn=lambda s: s.title)`: the tools' metadata carries no tier, as
       in Cuttlefish, so they are GENERIC; the caller's `--context` file, when given,
       enters the corpus as source `caller-context` with
       `credibility_tier: "ground_truth"`, as Cuttlefish treats a subscriber's own
       material. No tiering logic is copied.
     - `cross_validate(research_texts, question, question_gaps=question_gaps,
       source_tiers=tiers)`.
     - `refute_claims._select_load_bearing_weak_claims(cv.model_dump())` (a dict), and
       when it selects anything, `refute_claims(selected, research_texts, question,
       source_tiers=tiers)` inside a catch-all that records the rebuttal as skipped
       with the error, and dispositions outside refuted/weakened/survives coerced to
       survives, as the wrapper does.
     - `write_briefing(cross_validation=analysis._format_cross_validation(cv),
       research_digests, episode_title=question, question_gaps=question_gaps,
       style_guide=<decision-maker reader>, refutation_dispositions=<only refuted and
       weakened entries, each {claim, disposition, contradicting_evidence}>)`, so a
       refuted claim changes the findings instead of standing in them.
- **Runs detached.** The outer command starts the inner run in the background with
  its output going to `run.log`, writes `status.json` (`{"state": "running" |
  "done" | "failed", "step": "<current step>", "started": ..., "report": <path>,
  "error": <line>}`) and returns at once with the run directory. The inner run
  updates `status.json` at each step. A full run takes 25-45 minutes, longer than
  one shell call may last, so nothing waits on it in one call.
- **Leaves the caller's session settings behind.** The inner run drops
  `ANTHROPIC_BASE_URL`: a calling agent's session may point it at a local proxy with
  its own rate limit (found in build: the first real run failed on a 429 from it),
  and Cuttlefish calls the Anthropic API itself.
- **Writes** `report.md` and `raw.json` (every tool's text, meta and the structured
  outputs) to `--out` (default `./research/<YYYY-MM-DD>-<slug>/`), and prints the
  report path and the summary.
- Fewer than two tools returning means no cross-validation: the report says so, and
  every claim is single-source at its stated confidence.

The rendering is the only code that is ours: structured Cuttlefish output to markdown.

### 2. Report shape (`report.md`)

1. **Summary**: the cross-validation's own summary, then up to 7 claims that carry
   it (confirmed claims, highest confidence first, refuted ones left out), each with
   its confidence and sources. Enough to act on. No model call of ours writes it.
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
limit) until `done` or `failed`, for up to 60 minutes. On `done`, read `report.md`,
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

### 5. The podcast option: `run.py episode RUN_DIR [--podcast yudame-research]`

Drafts an episode with Cuttlefish's own operator commands, `manage.py episode create
--podcast-slug <podcast> --title <title> --defer-setup --json` then `episode attach
<slug> --file report.md --require --json`, and writes `episode.json`. It never runs
`setup` or `publish`: setting up, producing and publishing wait for a person who has
read the report. It needs `CUTTLEFISH_DIR` pointing at a checkout configured for
production; without it, it says so and stops. For the first run the episode is
prepared, not created: creating a row in Cuttlefish's production database is an effect
this task cannot request, so the delivery names the command.

### 6. README

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

- Five private Cuttlefish names are called: `_select_load_bearing_weak_claims`,
  `_guard_content_length`, `_format_cross_validation`, `_format_research_digest`,
  `_format_question_discovery`.
  Calling them pays the debt of re-implementing claim selection, the truncation rule
  and the formats here; a rename in Cuttlefish fails the run with the import error
  named.
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
- Cuttlefish's glue, with fake functions: `write_briefing` receives
  `refutation_dispositions` holding only refuted and weakened entries;
  `cross_validate` and `refute_claims` receive `source_tiers` (with `caller-context`
  as ground truth when context is given); `cross_validate` and `write_briefing`
  receive the same `question_gaps`; `_select_load_bearing_weak_claims` is given a
  dict; a failing `refute_claims` leaves the run going with the rebuttal recorded as
  skipped.
- Cuttlefish location: `$CUTTLEFISH_DIR` wins; otherwise the managed path; the runner
  never runs `git pull` in a directory it did not clone.
- Episode: with fake commands, `create --defer-setup` then `attach --require` with the
  report on the named podcast, nothing else (no setup, no publish); no report or no
  `CUTTLEFISH_DIR` stops with the reason.
- `tests/check_skills.py` passes with the new skill; the agent file has `name`,
  `description`, `tools`.

End to end, in build: Tom's question above, with the product-owner role and the Sheet's
columns and scoring formulas as context (no backlog rows, which are client work),
all six tools, started by the researcher agent and polled to completion (a real run
of over 10 minutes is expected with Gemini; its wall time is in the method section),
the report and its PDF kept in the task workspace for the delivery, not
committed. Its method section shows which tools ran and the cost.
