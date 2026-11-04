# Present: desktop decks by default, mobile carousel on request

Tom, 2026-11-04: a deck asked for in landscape came out oversize, as if made for a small screen. Default back to standard PowerPoint (landscape, desktop); portrait, social-carousel shape only when someone asks for mobile-friendly; even on mobile, no oversize fonts.

## What is wrong today (checked)

- `plugins/yudame/skills/present/SKILL.md`, PDF section, Deck rule: `@page { size: 254mm 142.9mm }` (10 in wide, not PowerPoint's 13.333 in), "Body at least 18pt, headlines at least 28pt": floors with no ceiling. 18pt on a 10 in slide reads as 24pt on a 13.333 in one, and "at least" invites ever-bigger type.
- Its "Vertical" variant (`108mm 192mm`, body at least 12pt, headlines at least 22pt) is phone-story shaped, again floor-only.
- The `pdfinfo` check says `720 x 405` for a deck, which is the 10 in size.
- Evidence from use: the recent landscape client deck (15 slides, 2026-11-04) printed at 544 x 306 pt (192 x 108 mm, 7.56 in wide, from an older cached copy of the skill), base type 18pt, headlines about 35pt (measured from the PDF's line boxes and the HTML's `3.3cqw` base). On a 13.333 in widescreen that is roughly 32pt body and 62pt headlines: the oversize Tom saw.

## What will be built

All in `plugins/yudame/skills/present/SKILL.md` unless named:

1. **Deck (default):** PowerPoint widescreen as PowerPoint makes it: `@page { size: 338.7mm 190.5mm; margin: 0 }` (13.333 x 7.5 in). Type as ranges with a ceiling: titles 32 to 40pt, body 16 to 24pt, captions, labels and table text 12 to 14pt; a cover or statement slide's single line may reach 54pt, nothing larger. Use the space like a desktop deck: a title plus content (two columns, a diagram beside its points, a table, a chart with its takeaway), not one big phrase per slide; statement slides are the deliberate exception. Keep the traditional layouts list.
2. **Mobile carousel (only when someone asks for mobile-friendly, a phone, or a carousel):** portrait 4:5 cards, `@page { size: 1080px 1350px; margin: 0 }`, one idea per card, type in px with a ceiling: headlines 56 to 72px, body 32 to 40px, captions 24 to 28px (on a phone this is ordinary reading size; phones are large now). Replaces the "Vertical" sentence.
3. **Check sizes:** `pdfinfo` line becomes `960 x 540` for a deck and `810 x 1012.5` for a carousel (Chrome prints CSS px at 96 per inch).
4. **Budgets (Deck section):** "over budget means split, never shrink" stays, joined by "never enlarge type to fill a slide; fill it with content or leave the space". Concept slide grows from about 40 to about 70 words of body; tables from 5 to 8 rows, since a 13.333 in slide at 16 to 24pt holds that. Statement slide stays at 12 words. Add one line for carousel budgets: about 30 words per card, 5 to 10 cards.
5. **Description and form table:** the frontmatter description and the Deck row name "a landscape desktop deck (a portrait carousel when asked for mobile)", so the right reading loads.
6. **house-style:** "on a landscape slide" becomes "on a desktop slide or a carousel card".
7. **Test:** `tests/check_present.py` (stdlib, no Chrome) asserts the documented invariant that each `@page` size SKILL.md gives for a deck and a carousel converts to the `pdfinfo` points it states, and that every type rule for decks and carousels is a range with an upper bound (no bare "at least Npt"). It fails on today's file (720 x 405 vs 254mm) and passes after. Add it to the README's test list next to the others.

## Samples (build stage, outside the repo)

Render a 3-slide sample of each from one self-contained HTML in `$TMPDIR` with the skill's own Chrome command and the house style: deck (title slide, two-column content slide with a diagram, table slide) and carousel (cover card, one-idea card, closing card). Check `pdfinfo` sizes, measure type from `pdftotext -bbox-layout` line heights against the ranges, render with `pdftoppm -r 100` and look at each page. Deliver `~/Desktop/Valor/present-sizes/deck-sample.pdf` and `~/Desktop/Valor/present-sizes/carousel-sample.pdf`; delete the HTML and PNGs afterwards. No sample or build file enters the repo.

## Out of scope

- The video template (`VIDEO.md`, `video/src/Root.tsx`): already 1920 x 1080 landscape; its type is for a screen recording, not a slide. Named in the delivery, not changed.
- Document and Page forms (A4/Letter): unchanged.
- Stale plugin caches on Valor's machines that still carry the 192mm rule: a product note in the delivery, not a change here.
- Valor's own persona text ("landscape 16:9 in PowerPoint-style layouts") lives outside this repo; nothing in yudame/skills says otherwise beyond the lines above.

## Tests that show it works

- `python3 tests/check_present.py`: deck 338.7 x 190.5 mm gives 960 x 540 pt within 1 pt; carousel 1080 x 1350 px gives 810 x 1012.5 pt; no floor-only type rule in the Deck or carousel rules; fails on the pre-change file (run it on `git show main:` content to show the failure).
- `python3 tests/check_skills.py`, `python3 tests/check_tts.py`, `python3 tests/check_ask.py`, `sh tests/check_install.sh`: still 0 failing.
- Sample renders: both PDFs at the stated sizes, measured title/body/caption heights inside the ranges, every page viewed; a desktop slide visibly uses its width (two columns or diagram plus text), the carousel cards read without oversize type.

## Governance

None added. The new test asserts documented behavior (sizes and type ranges the skill states); it is not a gate.

## Stakes

A wording change in one skill, reversible by revert; a mistake costs one more badly sized deck.
