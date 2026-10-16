# Manual-only skills stay manual in Codex

Task: c077ae6e3914. Appetite: small. Critique rounds: 0. Review rounds: 0.

## Stakes

A small, reversible test change prevents manual-only skills from silently becoming implicitly invocable in Codex; it changes no runtime or installed state.

## Grounding

Inspected `tests/check_skills.py`, README.md, existing Codex policy files and all skill frontmatter at baseline `c56327e`.

- The checker uses a small stdlib-only frontmatter reader and returns per-skill failures, with CLI status and optional JUnit output.
- Baseline: `python3 tests/check_skills.py` reports 33 skills, 0 failing.
- Six skills actually set `disable-model-invocation: true` in frontmatter: audit-hooks, audit-models, audit-skills, do-deploy-example, do-integration-audit and new-skill. All six already have the correct `agents/openai.yaml`:

  ```yaml
  policy:
    allow_implicit_invocation: false
  ```

- new-audit-skill mentions the flag in prose and a template, not its own frontmatter. It must not acquire a manual-only requirement from those mentions.

## Build

1. Extend the existing `problems()` path only for skills whose parsed frontmatter sets `disable-model-invocation: true` (case-insensitive, including `True` and `TRUE`). Require a readable `agents/openai.yaml` with `allow_implicit_invocation: false` under `policy`. Report a clear per-skill failure for a missing file or absent/incorrect policy, rather than crashing or accepting mere file existence. Preserve existing CLI and JUnit behavior.
2. Keep the addition roughly 10–15 lines, stdlib-only and tailored to the block-style policy files this repository ships: scan for a top-level `policy:` then an indented `allow_implicit_invocation: false` within that block, stripping trailing `# comment` text. Do not implement general YAML.
3. Re-scan the real skills during implementation. Add the two-line policy file to any qualifying skill missing it; preserve other existing config fields. Current inspection requires no skill-file changes. Do not add a file to new-audit-skill merely because its body mentions the flag.
4. Update the checker's introductory documentation to name this invariant. Do not add a second test mechanism or new test file.

## Verification

Use a throwaway fixture under `/tmp`, replacing the imported module's `ROOT`. Exercise correct policy, missing file, wrong or absent value, no flag, and case-insensitive `True`/`TRUE` flags. Also verify body-only mentions impose no requirement, inline policy comments work, and settings outside the top-level policy block do not pass. Keep CLI/JUnit reporting unchanged; no new CLI or JUnit fixture tests.

Run `python3 tests/check_skills.py` and `sh tests/check_install.sh`. Confirm the real skills remain at zero failures and all imports are stdlib. No live Codex invocation is claimed by these tests.

## Critique applied

Dropped the proposed unittest suite and unchanged reporting tests; fixtures run only in temporary storage. Narrowed the policy scan to the existing block format and made the frontmatter comparison case-insensitive. No new test file means README's existing test commands remain accurate.

## Boundaries and debt

No general YAML dependency/parser, installer changes, new invocation restrictions, frontmatter redesign, CI hooks, approval steps or unrelated skill edits. This is a test assertion of the documented cross-harness invariant explicitly requested by Tom, not a new governance layer. No technical debt additions; the extended checker covers the missing invariant. Existing portable-skills work is historical context, not scope to reopen. No open product questions.
