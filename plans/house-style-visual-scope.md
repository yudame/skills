# House-style: visual work, not prose

## Problem and evidence

A Codex turn used house-style to rewrite a sentence. At baseline
`c56327e57a1116633015ba30407ec0e189a3b8fb`, its description mentions visual
direction but does not explicitly exclude prose or name de-slop. Its opening
reference to a project's “style guide” could also mean an editorial guide.
The de-slop skill already covers prose editing, including short pasted text.

## Change

Edit only `plugins/yudame/skills/house-style/SKILL.md` during the build:

- Replace the description with: “Fallback visual style for decks, web pages,
  and document appearance: fonts, colors, layout. Use only for visual design,
  not prose editing; run the de-slop skill for wording.”
- Make the first body paragraph explicitly refer to the project's visual
  style guide, design system, or brand, preserving its precedence over the
  fallback. Briefly distinguish appearance from prose and point wording
  edits to the de-slop skill if needed to keep the opening unambiguous.
- Leave the actual visual recipe unchanged. Keep the description and opening
  to one short paragraph each, with a plain-word cross-skill reference.

No other skill, README, test, invocation policy, or runtime behavior changes.
No added governance, dependencies, or technical debt.

## Verification

- Run `python3 tests/check_skills.py` after editing; baseline is 33 skills,
  0 failing. It validates skill metadata and portable invocation syntax,
  not semantic routing.
- Read the description alone and then the opening against these cases:
  deck typography, web-page colors/layout, and document appearance belong
  here; sentence rewrites, email wording, and prose-only document/deck edits
  point to de-slop. An existing project visual guide still wins. A mixed
  request uses house-style only for its visual component.
- Inspect the diff to confirm the visual recipe and unrelated files remain
  unchanged. No new wording-matching tests or model-run routing claims.

## Stakes and rounds

A mistaken description can misroute editing requests, but this small text
change is local and easily reversible. Critique rounds: 0. Review rounds: 0.
