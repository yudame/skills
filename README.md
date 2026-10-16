# Yudame skills

Claude Code skills from Yudame, as two plugins in one marketplace:

| Plugin | For | Needs |
|---|---|---|
| `yudame` | Everyone | Nothing beyond Claude Code; `officecli` and `calendar` need the `officecli` and `gws` command-line tools |
| `yudame-dev` | Developers | git, and GitHub for the pipeline skills |

Skills load namespaced: `/yudame:present`, `/yudame-dev:do-plan`.

Why these skills exist, in principles: [MANIFESTO.md](MANIFESTO.md).

## What's here

**`yudame`**
- Presenting: `present` (deck, page, spoken brief, narrated video; voice via `tts.py`, video via a Remotion template), `house-style` (the fallback look), `de-slop` (the editorial gate), `email`.
- Office and calendar: `officecli` (Word, Excel and PowerPoint files), `calendar` (Google Calendar through `gws`).

**`yudame-dev`**
- Work pipeline: `do-issue`, `do-plan`, `do-plan-critique`, `do-build`, `do-test`, `do-patch`, `do-pr-review`, `do-docs`, `do-merge`, with `do-sdlc` to run them in order, and `do-investigation-issue` for unconfirmed findings.
- Audits: `audit-skills`, `audit-hooks`, `audit-models`, `do-integration-audit`, `do-discover-paths`, `new-audit-skill`.
- Building agents and skills: `imagine-agent`, `build-agent`, `cowork`, `new-skill`, `do-deploy-example`.
- Context and review: `ask-me`, `ontologies`, `zoom-out`, `weekly-review`, `do-design-audit`.

Whatever an Artifact can build (pages, decks, diagrams, design systems, dashboards), a skill here only sets the standard the build follows, so results stay consistent across runs.

## Install

In Claude Code:

```
/plugin marketplace add yudame/skills
/plugin install yudame@yudame
/plugin install yudame-dev@yudame
```

Developers install both; everyone else installs `yudame` only. From a shell:

```
claude plugin marketplace add yudame/skills
claude plugin install yudame@yudame
```

The repo is public, so no GitHub account is needed to install.

## Who "the user" is

Skills are written for whoever is in the conversation: "the user" gets the questions, drafts and approvals. A skill never names the person who wrote it. An autonomous deployment can sit behind the same skills: where a skill asks the user a question or waits for a checkpoint, that deployment answers through its own channel. A repo can change a skill's behavior by shipping a context file the skill probes for (for example `.claude/skill-context/<skill>.md` or `docs/sdlc/<skill>.md`), and no file means the generic behavior in the skill.

## Sync

The plugins have no `version`, so each commit on `main` is a new version. `claude plugin marketplace update yudame` then `claude plugin update yudame@yudame` pulls the latest; Claude Code also refreshes marketplaces on its own.

## Layout

`plugins/<plugin>/skills/<name>/SKILL.md`, plus any files the skill reads. Adding a directory there adds the skill. `yudame` is self-contained. `do-design-audit` in `yudame-dev` falls back to `/yudame:house-style`, so developers should install both.

## Origin

Imported from the `.claude/skills-global/` directory of an earlier agent system. Some skills still mention that system's per-repo context files (`docs/sdlc/`, `.claude/skill-context/`) and tools; they are reviewed one by one.
