# Plan: every skill works the same in Claude Code, Codex and Pi

Task 488fa856bef9. Branch `valor/488fa856`.

## Stakes

Text edits to 31 skills plus a small installer that writes symlinks into
`~/.agents/skills`; all reversible, but the edits are broad and the installer
touches the user's home, so a missed reference or an over-eager replace is the
real risk.

## What gets built

### A. Skill text, across `plugins/*/skills/**` (SKILL.md and every file a skill reads)

1. **Skill calls by name.** Every `/yudame:<x>` and `/yudame-dev:<x>` becomes
   plain words: "run the do-test skill", "the house-style skill". This covers
   descriptions too (do-sdlc, imagine-agent), sub-files (do-plan/PLAN_TEMPLATE.md,
   DOMAIN_FRAMING.md, do-issue/ISSUE_TEMPLATE.md, do-test/baseline-verification.md,
   do-pr-review/sub-skills/*), and comments in present/tts.py and
   present/video/src/Explainer.tsx. README.md keeps the Claude form, since it
   documents the per-harness invocation.
2. **Subagents.** Each place a skill dispatches a subagent (do-build, do-sdlc,
   do-plan, do-plan-critique, do-pr-review, do-test, do-patch, do-issue,
   do-docs, do-merge, do-integration-audit, audit-skills, imagine-agent,
   build-agent, new-skill, new-audit-skill, de-slop, email, present; confirm
   each hit is a real dispatch, not the word "agent" meaning a managed agent)
   gets one sentence: without subagents, do the step yourself in sequence; for
   a fresh-context review, re-read only the artifact (the plan, the diff, the
   draft) before judging. Where several skills share the case, the sentence is
   the same words.
   - **do-build sequential mode:** a short section: with no subagents, run the
     plan's tasks in dependency order in the one worktree yourself, commit
     after each, then the same verification and PR steps.
   - **do-sdlc sequential mode:** a short section: with no subagents, run each
     stage skill in this session in the same order, and before each stage
     re-read only that stage's inputs (issue, plan file, PR diff) rather than
     relying on what earlier stages left in context. The `model:` column
     becomes a Claude Code note.
3. **Actions, not Claude tools.** `AskUserQuestion` → "ask the user one
   question with 2-4 options" (ask-me, imagine-agent, build-agent, do-plan,
   new-skill/SESSION_CAPTURE.md). `WebSearch`/`ToolSearch`/`WebFetch` →
   "search the web if you can" (do-plan). `run_in_background`, `isolation`,
   `name` and `model:` dispatch parameters stay only as sentences marked as
   Claude Code notes (do-build, do-sdlc, do-plan, do-plan-critique,
   do-pr-review, do-test).
4. **`$ARGUMENTS` fallback.** Every skill that reads `$ARGUMENTS`
   (do-plan-critique, do-discover-paths, do-deploy-example, do-build,
   build-agent, imagine-agent (SKILL.md:32, "the repo in `$ARGUMENTS`"),
   audit-skills, do-test, do-patch, and the new-skill /
   new-audit-skill templates) carries: "if it is empty or the literal
   `$ARGUMENTS`, use what followed the skill name in the message." Existing
   wordings are kept where they already say this; do-plan-critique's bash
   `ARG="$ARGUMENTS"` gets the sentence above it.
5. **Paths and repo instructions.** `${CLAUDE_SKILL_DIR}` (audit-skills) →
   "this skill's directory". Every place a skill looks for repo instructions in
   `CLAUDE.md` says "AGENTS.md or CLAUDE.md" (audit-models, audit-hooks,
   ontologies, imagine-agent, build-agent and references/build-sheet.md,
   audit-skills and references/rubric.md, do-test, do-plan/DOMAIN_FRAMING.md,
   de-slop, email). Where CLAUDE.md is the subject (audit-hooks auditing
   Claude Code hooks), it stays.
6. **Frontmatter.**
   - Claude-only fields (`disable-model-invocation`, `context`, `argument-hint`,
     `model`, `user-invocable`) stay.
   - `allowed-tools` becomes a space-separated string in all 14 skills that set
     it, and in the new-skill and new-audit-skill templates. Its entries keep
     their Claude tool names (`Agent`, `AskUserQuestion`, `WebSearch`,
     `ToolSearch`): the field is a Claude Code pre-approval list that other
     harnesses ignore, so dropping them would only cost Claude Code users
     prompts. No pattern may contain a space, since a space now separates
     entries: new-skill/SKILL.md:51's example `Bash(git log:*)` becomes
     `Bash(git:*)`, and new-skill/WORKFLOW_TEMPLATE.md:9-10 changes from a
     YAML list with `Bash(gh pr:*)` to a single space-separated string such
     as `allowed-tools: {{space-separated patterns, e.g. Bash(gh:*) Read}}`.
     Before converting, confirm
     against the Claude Code skills docs that a space-separated string is
     parsed; if it is not, stop and record that in the delivery rather than
     ship a form Claude Code ignores.
   - `agents/openai.yaml` with `policy:\n  allow_implicit_invocation: false`
     in each skill that sets `disable-model-invocation: true`: audit-hooks,
     audit-models, audit-skills, do-deploy-example, do-integration-audit,
     new-skill. new-audit-skill's AUDIT_TEMPLATE.md sets the flag, so its
     SKILL.md tells the author to add the same file.
7. **Compatibility and audit-skills.** `compatibility: Claude Code` on
   audit-hooks and cowork. new-skill is rewritten to describe all three
   harnesses instead (where skills live for each, how each invokes, that Codex
   needs agents/openai.yaml for manual-only, that `compatibility` names a
   harness-specific skill); if that cannot fit in its current length, it gets
   `compatibility: Claude Code` instead and the delivery says so. build-agent
   (Managed Agents via the API) is harness-neutral and gets none.
   audit-skills/scripts/audit_skills.py adds `.agents/skills` (project) and
   `~/.agents/skills` (user) to the roots it scans, next to `.claude/skills`;
   symlinked skill directories are followed and a skill reached twice by
   resolved path is audited once. Its KNOWN_FIELDS (audit_skills.py:79-91)
   gains the Agent Skills spec fields `compatibility`, `license` and
   `metadata`, so the field this plan adds, and spec-only skills found in
   `.agents/skills`, are not reported as unknown keys. SKILL.md's description of what is scanned
   is updated.
8. **do-sdlc namespace.** `skill "tom:{skill-name}"` becomes "run the
   {skill-name} skill (in Claude Code, the Skill tool with
   `yudame-dev:{skill-name}`)", inside the subagent prompt.

### B. `install.sh` at the repo root

POSIX sh. Resolves the repo from its own location, not the cwd. For each
`plugins/*/skills/<name>`, makes `~/.agents/skills/<name>` a symlink to the
absolute path of that directory. Rules:
- missing → create the link;
- a live symlink whose target is `<repo>/plugins/<plugin>/skills/<name>`
  where `<repo>/.claude-plugin/marketplace.json` has `"name": "yudame"`
  (this clone or another clone of this repo) → replace it. The
  `plugins/*/skills/*` shape alone is not enough: it is the standard Claude
  marketplace layout, and another marketplace's `email` or `present` link
  must survive;
- anything else (a real directory, a file, a link to another marketplace or
  elsewhere) → leave it, print one line saying it was skipped and why;
- a dangling symlink in `~/.agents/skills` → remove it only if its target
  path starts with this clone's absolute path, or it is listed in
  `~/.agents/skills/.yudame-installed`, a manifest the installer writes
  with every link it made (a skill that was deleted or renamed, or a clone
  that moved). The manifest is rewritten on each run; entries the run
  did not keep are dropped;
- running twice changes nothing; prints what it linked, replaced, skipped.

README.md gets a "Codex and Pi" install section: clone, `./install.sh`,
re-run after `git pull`; invocation as `$name` (Codex) and `/skill:name`
(Pi); Pi also reads `~/.pi/agent/skills` but `~/.agents/skills` covers both;
Pi has no subagents, so the pipeline skills run their sequential mode. The
"Skills load namespaced" line and the `/yudame:house-style` mention in
Layout are reworded to cover all three.

### C. `tests/check_skills.py`

Two new failures per skill:
- any `/yudame:` or `/yudame-dev:` in any text file under the skill's
  directory (SKILL.md and every sub-file, scripts and templates included).
  A text file is any file that decodes as UTF-8; files that fail to decode
  are skipped, and any path under a `node_modules` directory is skipped;
- an `allowed-tools` value containing a comma. The checker's frontmatter
  parser reads only the line `allowed-tools:` itself, so it also fails an
  `allowed-tools:` with an empty value followed by indented list lines (the
  YAML-list form): the spec makes the field a space-separated string, and
  the list form is not meant to pass. The template fenced inside
  WORKFLOW_TEMPLATE.md is not frontmatter and is not parsed.

Existing checks unchanged; still one testcase per skill.

### D. Length

No SKILL.md grows. Each added sentence is paid for by trimming in the same
file. Measured against `276ba62` by both line count and word count per
SKILL.md; a file over on either is trimmed until it is not.

## Out of scope

- Rewriting skill logic, rubrics, or the Claude Code-specific rules inside
  audit_skills.py (for example "infra skills must set
  disable-model-invocation"); only its scan roots and the three spec
  fields added to KNOWN_FIELDS change.
- Pi-specific install into `~/.pi/agent/skills` (Pi reads `~/.agents/skills`).
- Converting plugin packaging (`.claude-plugin`) or adding a Codex/Pi
  marketplace manifest.
- Testing each skill end to end inside Codex or Pi; verification is static
  plus the installer and a load listing where the binaries are present.
- No new check, hook, or gate beyond the two test assertions Tom asked for,
  which assert documented behavior.

## Tech-debt additions

None.

## Tests and verification

1. `python3 tests/check_skills.py` passes on the result.
2. The new assertions fail where they should: on a scratch copy, insert
   `/yudame-dev:do-test` into one sub-file and `allowed-tools: Read, Bash`
   into one SKILL.md; each produces exactly one failure for that skill.
   Also fail: a YAML-list `allowed-tools` in a SKILL.md. Do not fail: a
   space-separated `allowed-tools`, a `Bash(gh:*)` pattern, a mention of the
   word "yudame" without the slash form, a non-UTF-8 file containing the
   bytes `/yudame:`, and a `node_modules/x.js` containing `/yudame:`.
3. `tests/check_install.sh` (new, small, runs install.sh with `HOME` set to a
   temp dir):
   - fresh home: one link per skill, each resolving to the right directory;
   - second run: no changes, same link set;
   - a pre-existing real directory and a link to an unrelated path under a
     skill's name survive untouched and are reported as skipped;
   - a link to the same skill in another clone of this repo (its
     marketplace.json named `yudame`) is replaced;
   - a link to `<other-repo>/plugins/x/skills/<name>`, where other-repo's
     marketplace.json names another marketplace, is skipped and reported;
   - a dangling link into this clone's `plugins/*/skills/x` is removed; a
     dangling link listed in the manifest is removed; a dangling link
     elsewhere, not in the manifest, is left;
   - run from another cwd gives the same result.
4. Static sweep after edits, expecting zero hits outside README.md and
   explicit "Claude Code note" sentences: `/yudame(-dev)?:`, `tom:`,
   `CLAUDE_SKILL_DIR`, `AskUserQuestion`, `WebSearch`, `ToolSearch`,
   `run_in_background`, `isolation:`. The sweep covers skill bodies and
   sub-files, not frontmatter: Claude tool names in `allowed-tools` stay
   (A6). Separately, no `allowed-tools` value contains a space inside
   parentheses.
5. Every `disable-model-invocation: true` skill has `agents/openai.yaml` that
   parses as YAML with `policy.allow_implicit_invocation` the boolean false.
6. Length table: lines and words per SKILL.md, before and after; none
   higher.
7. audit-skills: run `audit_skills.py` in a temp repo containing
   `.agents/skills/<x>/SKILL.md`; the skill appears in the report. Run it in
   this repo; it still reports the plugin skills, and with a populated
   `~/.agents/skills` symlink set no skill is reported twice. audit-hooks
   and cowork (now carrying `compatibility`) raise no unknown-field
   finding.
8. Where `codex` or `pi` is installed on this machine, list skills after
   install and confirm all 31 load with no parse warning; where not, the
   delivery names that as unverified.
9. Each subagent edit reread in place: the fallback sentence sits next to the
   dispatch it covers, and do-build/do-sdlc sequential modes read as complete
   procedures.

## Loops

critique_rounds 1, review_rounds 1: broad text change plus a script that
writes in the user's home, reversible but easy to get subtly wrong.
