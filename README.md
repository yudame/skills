# Yudame skills

Agent skills from Yudame, as two plugins in one marketplace. They follow the [Agent Skills](https://agentskills.io) standard and work the same in Claude Code, OpenAI Codex CLI and Pi:

| Plugin | For | Needs |
|---|---|---|
| `yudame` | Everyone | Nothing beyond the agent; `officecli` and `calendar` need the `officecli` and `gws` command-line tools |
| `yudame-dev` | Developers | git, and GitHub for the pipeline skills |

Invoke a skill as `/yudame:present` in Claude Code, as `$present` in Codex, or as `/skill:present` in Pi. Inside a skill, other skills are named in plain words ("run the de-slop skill"), so each harness resolves them its own way.

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

### Codex and Pi

Both read skills from `~/.agents/skills`. Clone the repo and run its installer:

```
git clone https://github.com/yudame/skills.git
cd skills && ./install.sh
```

It links each `plugins/*/skills/<name>` into `~/.agents/skills/<name>`, pointing at this clone. It is safe to re-run: it replaces only links into a clone of this repo, removes its own links to skills that were deleted, and skips anything else at a skill's name with a one-line notice. After `git pull`, run it again to pick up new or removed skills. Skills that only make sense on demand ship `agents/openai.yaml` so Codex, like Claude Code, loads them only when you call them.

Pi has no subagents, so the skills that fan out (`do-build`, `do-sdlc`, the critics and reviewers) run their steps in sequence there; each skill says how. Pi also reads `~/.pi/agent/skills`, but `~/.agents/skills` covers it.

### Google sign-in for `gws`

`email` and `calendar` use `gws`, Google's Workspace CLI. At Yudame it signs in through the Yudame Workspace OAuth client, which only yuda.me accounts can use. Once per machine:

```
npm install -g @googleworkspace/cli
mkdir -p ~/.config/gws
op read --out-file ~/.config/gws/client_secret.json 'op://Yudame Secrets/Google Oauth Client Valor Desktop Client/client_secret_json'
gws auth login --scopes https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/tasks,https://www.googleapis.com/auth/contacts,https://www.googleapis.com/auth/chat.messages,https://www.googleapis.com/auth/chat.spaces,https://www.googleapis.com/auth/forms.body,https://www.googleapis.com/auth/forms.responses.readonly,https://www.googleapis.com/auth/meetings.space.created,https://www.googleapis.com/auth/meetings.space.readonly,openid,https://www.googleapis.com/auth/userinfo.email
```

Approve it in the browser as your yuda.me account. Never `--full` or the default scopes: they add Cloud scopes, and Yudame's Cloud session control then asks for the sign-in again. Outside Yudame, `gws auth setup` makes your own client.

## Who "the user" is

Skills are written for whoever is in the conversation: "the user" gets the questions, drafts and approvals. A skill never names the person who wrote it. An autonomous deployment can sit behind the same skills: where a skill asks the user a question or waits for a checkpoint, that deployment answers through its own channel. A repo can change a skill's behavior by shipping a context file the skill probes for (for example `.claude/skill-context/<skill>.md` or `docs/sdlc/<skill>.md`), and no file means the generic behavior in the skill.

## Sync

The plugins have no `version`, so each commit on `main` is a new version. `claude plugin marketplace update yudame` then `claude plugin update yudame@yudame` pulls the latest; Claude Code also refreshes marketplaces on its own.

## Layout

`plugins/<plugin>/skills/<name>/SKILL.md`, plus any files the skill reads. Adding a directory there adds the skill. `yudame` is self-contained. `do-design-audit` in `yudame-dev` falls back to the `house-style` skill, so developers should install both. `audit-hooks` and `cowork` are about Claude Code itself and say so in `compatibility`.

`python3 tests/check_skills.py` checks that every skill loads in all three harnesses; `sh tests/check_install.sh` checks the installer; `python3 tests/check_tts.py` checks that the present skill's `tts.py` says the names in its lexicon as listed.

## Origin

Imported from the `.claude/skills-global/` directory of an earlier agent system. Some skills still mention that system's per-repo context files (`docs/sdlc/`, `.claude/skill-context/`) and tools; they are reviewed one by one.
