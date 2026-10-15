---
name: audit-skills
description: "Lint skills for structure, description cost, and rot; --arch for architecture dispositions. Use when auditing skills."
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Agent
argument-hint: "[--fix] [--json] [--skill <name>] [--no-sync] [--arch]"
---

# Skills Audit

Find skills that waste context, fire on the wrong prompts, or have rotted. Two layers: a deterministic lint (a script checks what code can verify) and an optional architecture pass (`--arch`, model judgment against a fixed rubric). The result is a findings report; nothing beyond trivial mechanical fixes is changed without the user reviewing it.

## The economics being audited

A skill costs context in three tiers:

1. **Description**: ships in every session, used or not. The fleet total is the scarcest budget: 4,000 chars (about 2% of context), target 120 or fewer per skill.
2. **Body (SKILL.md)**: loads once per invocation. Only what every invocation needs; cap 500 lines.
3. **Sub-files**: load on demand. Reference tables, edge cases, templates.

Always-true policy belongs in the repo's CLAUDE.md, not in a skill. Most findings are content sitting in the wrong tier.

## Layer 1: lint

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/audit_skills.py" $ARGUMENTS
```

If `$ARGUMENTS` arrives unsubstituted, pass through whatever followed the command in the user's message. Run `--help` for the flags: `--fix` (trivial fixes only), `--json`, `--skill <name>`, `--no-sync`, and the sync controls `--apply`, `--update-skills`, `--force-refresh`.

The script finds skills relative to the current directory: it audits `.claude/skills-global/` and `.claude/skills/` under cwd, plus orphan detection in `~/.claude/skills/`. It does not look in a plugin's `skills/` directory, so for this plugin's own skills, apply the rules below by reading the files directly. Exit code 1 means at least one FAIL.

The 21 rules, by group (the script docstrings carry the details):

- **Structure**: line count, frontmatter parses, name valid and matches the directory, sub-file links resolve, only known frontmatter fields, `argument-hint` present when `$ARGUMENTS` is used.
- **Descriptions**: trigger phrase present, length (target 120, warn over 200, hard cap 1024), no duplicate or near-duplicate trigger surfaces, fleet total within budget.
- **Classification**: infra skills carry `disable-model-invocation`, background reference skills carry `user-invocable: false`, fork skills carry `context: fork`.
- **Repo coupling (13, 21)**: written for deployments that override skills through per-repo context files before using that repo's CLIs. In any other repo these mostly pass vacuously; treat their findings as hints, not failures.
- **Rot and hygiene**: referenced paths resolve (missing own assets FAIL, other paths WARN), no tracked junk files, every sub-file is referenced, no husk directories (a directory without SKILL.md). `--fix` prunes husks that hold only build artifacts; husks with real files need a human delete-or-restore decision. User-level copies trace back to a repo source and have not diverged.

The best-practices sync (`scripts/sync_best_practices.py`, on by default) fetches Anthropic's skills docs and the upstream skill-creator into `references/` with a 7-day cache. Its diff and `--apply` target a `new-skill` template under `.claude/skills-global/` that only existed in the old Valor repo; elsewhere, use `--no-sync` or read the refreshed references directly.

## Layer 2: architecture pass (`--arch`)

For each skill: improvement suggestions, a disposition (keep, merge, split, workflow, subagent, script, retire), and a model tier, with every non-keep disposition sent to a fresh-context verifier that tries to refute it. Use the lenses, disposition criteria, findings schema, and verifier prompt in [references/rubric.md](references/rubric.md) rather than improvising criteria, so runs stay comparable.

## After the audit

`--fix` applies only mechanical corrections. Merges, splits, and description rewrites change when skills fire, so present them as recommendations for the user to accept, never apply them from the audit itself. For accepted moves or renames, note what else must follow: references in other skills (cross-references use `/yudame:<name>` or `/yudame-dev:<name>`, by the plugin that owns the skill) and any installed copies that would go stale.
