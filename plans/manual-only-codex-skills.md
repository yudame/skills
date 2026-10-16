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

1. Extend the existing `problems()` path only for skills whose parsed frontmatter sets `disable-model-invocation: true`. Require a readable `agents/openai.yaml` with `allow_implicit_invocation: false` under `policy`. Report a clear per-skill failure for a missing file or absent/incorrect policy, rather than crashing or accepting mere file existence. Preserve existing CLI and JUnit behavior.
2. Keep implementation compact, stdlib-only and tailored to the simple block-style policy files this repository ships. Use a small indentation-aware scan or equivalent narrow matching; do not implement general YAML. A comment, a quoted string containing the setting, or the setting in another mapping must not satisfy the requirement. Accept ordinary whitespace and inline comments around the actual setting.
3. Re-scan the real skills during implementation. Add the two-line policy file to any qualifying skill missing it; preserve other existing config fields. Current inspection requires no skill-file changes. Do not add a file to new-audit-skill merely because its body mentions the flag.
4. Add focused stdlib `unittest` regression coverage in `tests/test_check_skills.py`, using temporary skill directories and replacing the module's `ROOT` for each fixture. Reuse the existing parser and reporting rather than introducing a separate validation framework. Update the checker's introductory documentation to name this invariant.

## Verification

Fixture cases:

- Frontmatter true plus correct policy passes.
- Frontmatter true plus missing file, empty file, missing key, or true value fails with a useful skill-local diagnostic.
- Comment-only false, false under another mapping, and false embedded in text do not pass.
- Normal indentation, whitespace and inline comments in the policy pass.
- Absent or false frontmatter flag imposes no Codex-file requirement; body/template mentions alone impose none.
- Multiple skills remain independently reported, so one valid config cannot satisfy another skill.
- Exercise CLI exit status and generated JUnit for a failing fixture, preserving the current reporting contract.

Run `python3 -m unittest discover -s tests -p 'test_*.py'`, `python3 tests/check_skills.py` (also with a temporary JUnit output path), and `sh tests/check_install.sh`. Confirm the real skills remain at zero failures and all imports are stdlib. No live Codex invocation is claimed by these tests.

## Boundaries and debt

No general YAML dependency/parser, installer changes, new invocation restrictions, frontmatter redesign, CI hooks, approval steps or unrelated skill edits. This is a test assertion of the documented cross-harness invariant explicitly requested by Tom, not a new governance layer. No technical debt additions; the focused tests pay the missing regression coverage. Existing portable-skills work is historical context, not scope to reopen. No open product questions.
