# Plan: a general-purpose research skill and researcher agent in the public yudame plugin

## Request

Tom, 2026-11-01, #yudame-dev: Valor should have deep-research tools, owned by a purpose-built subagent so the caller never handles their complexity; reports are long, every claim sourced with a confidence, a short summary on top (correction, 12:26 UTC).

Revised by Tom, 16:45 UTC, after the first build (a runner over private Cuttlefish code with keys from Valor's vault): "I'm gonna bake in a more sophisticated and complete version into the Valor code base as its own dedicated researcher agent. For the skills repo, let's ship a pared down general purpose skill that anyone from the general public can use if their system knows where to find API keys. Ideally, it should work if only an OpenRouter API key is available ... a system that knows what keys it has can choose which keys are best. And this skill is more of a high-level guidance for how to think through a research topic rather than a very prescriptive flow." And 16:56 UTC: "even for people who only have Claude and don't have Open Router, it should still be a useful skill for them."

The Cuttlefish runner stays available to Tom at commit `6e67b1c` (`plugins/yudame/skills/research/run.py`, `keys.env`, `tests/check_research.py`) on branch `valor/870731e4`.

## What gets built

- **`plugins/yudame/skills/research/SKILL.md`**: guidance, not a pipeline. Quick vs deep; frame the question; split into sub-questions; gather from independent sources; cross-check every claim (confirmed, single-source, contested; independence counted by publisher); confidence per claim; rebut the weak load-bearing claims; the long report's eight sections. Three ways to gather, by what the system has: no keys (several web-search passes with different angles, by subagent where available); only `OPENROUTER_API_KEY` (Perplexity Sonar plus OpenAI, Gemini, Claude and Grok models with OpenRouter's web plugin, ids checked live since they change); other keys (each provider's own deep-research mode by its strength, OpenRouter for the gaps).
- **`plugins/yudame/skills/research/ask.py`**: optional, standard library only. One OpenRouter chat call with the web plugin and cost reporting; prints answer, cited URLs and cost; `--no-web`; `--list WORD` for current model ids. The skill stands without it.
- **`plugins/yudame/agents/researcher.md`**: follows the skill with whatever keys the system has, runs long calls in the background, writes the report to a file, returns the summary, path, failed sources and cost.
- **README**: the research line and needs reworded; the test line names `check_ask.py`.
- Removed: `run.py`, `keys.env`, `tests/check_research.py`, the `/research/` gitignore line. No private repo, 1Password reference or Yudame path remains.

## Tests

`tests/check_ask.py` (no network, no key): request carries the web plugin by default and cost reporting, none with `--no-web`; the answer, each cited URL once in order (annotations and citations), and the cost are read; missing cost is None; the call posts to OpenRouter with the bearer key; no key exits 2 naming it. `tests/check_skills.py` passes.

End to end: one short question run twice, once with only `OPENROUTER_API_KEY` in the environment (`env -i`), once with no keys (the agent's own web search through subagents), each to a long report with Method section; reports kept outside the repo.

## Stakes

A public skill any teammate's or stranger's agent may load; a wrong method yields overconfident reports. Reversible by a revert. Review rounds: 1.

No governance is added.
