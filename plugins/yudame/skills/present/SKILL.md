---
name: present
description: "Present in the form the occasion needs: a Slides deck, a one-page explainer, a spoken brief, or a narrated video. Use for 'present this'."
argument-hint: "<topic, notes or file; defaults to the current conversation> [deck|page|brief|video]"
---

# Present

The artifact tooling already builds pages and Slides decks. This skill fixes what must hold across runs, and supplies the two things artifacts cannot: a voice and a rendered video.

## Pick the form

Use the form the user names. Otherwise choose from the occasion, say which in one line, and build; don't ask.

| The occasion | Form |
|---|---|
| A room or a call, someone talking over slides; a proposal or decision session | **Deck**: a Slides artifact |
| One reader at a screen who needs to get one idea fast | **Page**: a single-page artifact |
| A busy listener who needs to decide or know something today, often away from a screen | **Brief**: a ~30-second audio file |
| Something watched later or by many: a mechanism that unfolds over time, a walkthrough to send round | **Video**: a narrated MP4 |

## What every form shares

- **Grounded.** Research the real source material (code, docs, the client's own words, recent commits and PRs) before outlining. Something built from general knowledge is not done.
- **One takeaway.** Before building, write the one sentence the audience must walk away with. Everything that doesn't serve it goes.
- **Headlines are conclusions.** Every slide title, page section and video scene title is a full sentence, under 15 words, stating its point. Read in order, they make the argument; if they read as a table of contents, rewrite them.
- **Look.** The project's own style guide or brand first, then the design system the artifact tooling offers, and only when neither exists, the house-style skill. One accent per view, spent on the value that matters.
- **Editorial pass.** Anything going to an audience beyond the user (deck, page, video script) goes through the de-slop skill in a fresh context given only the draft, medium and audience (a subagent, or else re-read only the draft file). Act on every flag; after two BLOCKs, show the user both diagnoses instead of shipping.
- **Done is checkable.** Report the artifact link or the file path, plus whatever proves it: the published artifact, or `ffprobe` duration for audio and video.

## Deck

Pick the deck's job first, because it decides the opening:

- **Educational or internal:** what it is in one plain sentence, the problem it solves, how it works (happy path, at most five steps), the clever part, how it fits the larger system.
- **Persuasion or decision** (proposals, client sessions, decision briefs): why, then how, then what. The first slides describe the audience's own situation and problem accurately before any solution appears; leading with the solution is how these decks fail. Each decision gets its own slide with a recommended default they can veto. The cover names who it is prepared for.
- **Informational** (architecture, audit findings, status): a one-line scope and method note, then the subject. Don't manufacture a problem the audience never raised.

Budgets: a statement slide holds at most 12 words, a concept slide about 40 words of body, a table 5 rows. Over budget means split the slide, never shrink the type. Diagrams show a relationship the text cannot, around seven nodes at most, every arrow labelled. Default when unstated: a general technical audience, 10 to 15 slides at about 30 seconds each.

If the user wants the deck narrated, write speaker notes for the ear (below) and make it a video: one scene per slide.

## Page

The page succeeds when a smart newcomer gets the idea faster from it than from a paragraph: a taught explanation, not the same prose in a nicer font. Start from what the reader knows, give a concrete example before the abstraction, and rank what matters instead of presenting five things as equal. Section headers read as an outline, and the page ends where the reader can act. Cut any section that neither teaches nor guides.

Lead with the shape of the idea: a process gets a numbered path or flow, a system a labelled diagram of parts, a comparison side-by-side columns with differences marked, a decision the question, options and the recommendation, events a timeline, one hard concept an analogy and then the mechanism, numbers a few stat tiles or one chart. Light throughout, and it prints the way it screens.

## Brief

A ~30-second spoken executive brief. The value is the construction, not the speech: the listener's attention is the scarce resource, so an item earns its seconds only if they must decide it, act on it, or know it before a meeting today. Things already being handled don't appear; calendars they already have don't get echoed back, only the anomaly.

Sort the material (the user's notes, or else recent commits, PRs and whatever context they point to) into decision, critical heads-up, FYI, already handled, and noise; drop the last two. Status-of-status ("I'm working on the migration") is never an item: either it shipped (FYI) or it's blocked on a decision. If most of the material drops out, tell the user the brief isn't worth sending rather than producing filler.

The shape:

1. **Top decision with your recommendation**, about 25 words. The first sentence is the ask, phrased default-and-confirm: "I'm pushing the vendor call to Thursday unless you want it sooner" beats "What should we do about the vendor?" Their job is to veto, not deliberate.
2. **A second decision or one critical heads-up**, about 20 words, only if there is one; silence beats padding.
3. **Batched FYIs**, about 20 words: "Three quick FYIs:" then one clause each.
4. **Close:** "I've got the rest."

Each decision needs its current default, its deadline, and the cost of being wrong; if one is missing and can't be found, ask the user one consolidated question or demote the item. Aim for 55 to 80 words: over 80, cut; under 55, drop the weakest FYI rather than pad. Synthesize it as `.m4a` (or `.ogg` when it's headed for a chat voice note) and report the path, the duration and the transcript. Sending it anywhere is Tom's step, not this skill's.

## Voice

Writing for the ear, for every voiced form:

- Contractions throughout; written prose sounds stiff aloud.
- No issue, PR, port or other multi-digit numbers. TTS reads "1195" as "one thousand one hundred ninety-five", which spends the listener's attention on nothing. Name the work by substance ("the continuation crash").
- Respell awkward proper nouns in plain dictionary style (`You-duh-may` for Yudame). Never IPA in slashes: the phonemizer reads `/.../` literally, garbling the word and doubling the clip length.
- Short sentences with one idea each; a listener can't re-read.

Synthesize with `tts.py` in this skill's directory, run through `uv` (it declares its own dependencies):

```bash
uv run <skill dir>/tts.py --text "..." --out brief.m4a            # one clip: .wav .m4a .mp3 .ogg
uv run <skill dir>/tts.py --scenes scenes.json --out-dir public/vo # one WAV per scene + manifest.json
```

The default engine is Kokoro, a local neural voice (Apache-2.0, free, offline) whose models live in `~/.cache/kokoro-onnx`; default voice `am_michael`, British alternatives `bm_george` and `bf_emma`. When Kokoro can't run, it falls back to macOS `say` with the `Daniel` voice and says so on stderr. The JSON it prints names the engine used: report a fallback to the user, because `say` sounds noticeably more robotic. Pass `--engine say --voice <name>` to choose a `say` voice deliberately. It speaks about 170 words a minute, so 70 words is roughly 25 seconds.

## Video

Read [VIDEO.md](VIDEO.md) before making one. It covers the Remotion template in `video/`, the exact commands, and the gotchas. The standard: one idea per scene, 5 to 15 seconds each, 60 to 120 seconds overall unless asked otherwise. The voice carries the sentences and the screen carries the headline, the key number or the diagram; on-screen text that duplicates the narration word for word splits the viewer's attention. Scene length comes from the narration's measured duration, never from a guess.
