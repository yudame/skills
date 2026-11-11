# Present video: "read-only" said "reed", and a title thumbnail

Tom, 2026-11-11: in a narrated video "read-only" comes out "red-only", and the
video's thumbnail is its first frame, which is blank. Two bug fixes, each a
commit with a test.

## What is wrong (checked)

- **Read.** I ran Kokoro's own phonemizer (en-us, the one `tts.py` uses) to see how each phrase is said:
  `read access`, `read it`, `to read the file`, `Read the docs`, `read-write`,
  `read replicas` and `read-only mode` already come out `ɹˈiːd`.
  `It is read-only`, `The disk was read-only` and `The file is read only`
  come out `ɹˈɛd`: espeak treats "read" after "is" or "was" as past tense,
  so in "read-only" (hyphen or space) it says "red". Past tense is right as
  it is (`I have read the file` gives `ɹˈɛd`).
- **Thumbnail.** In `video/src/Explainer.tsx`, `enter = spring({frame, ...})`
  is 0 at frame 0. Every scene, the first one included, starts with an
  invisible title and a zero-width rule, so frame 0 is an empty cream page.

## What will be built

1. **`tts.py`:** add one `LEXICON` entry, `"read-only": "ɹˈiːdˈoʊnli"`, on
   the existing splice path. The hyphenated form is always the adjective.
   The spaced "read only" is spliced only after a form of be (is, are, was,
   were, be, been, being, plus `'s`/`'re` contractions), because
   "I read only the summary" is genuine past tense and must stay "red". In
   `NAMES` this is one more alternative: `\b(?:is|are|was|were|be|been|being)\s+`
   matched as plain text, then `read only` spliced as `ɹˈiːd ˈoʊnli`. Names
   stay matchable inside a word (as in `valorengels`); the read alternatives
   take `\b` on both sides, so `spread only` and `bread-only` stay untouched. Update the comment
   above `LEXICON` to say it holds words espeak says wrong, names and these
   phrases. Add no other rule: inspection shows the other "read" phrases are
   already right.
2. **`Explainer.tsx`:** the first scene is drawn fully at frame 0
   (`enter = index === 0 ? 1 : spring(...)`): title and rule visible, no
   fade from blank. Its points still appear in step with the narration.
   Later scenes keep their spring.
3. **Docs:** SKILL.md Voice bullet: the lexicon also holds "read-only".
   VIDEO.md "How the template works": the first scene is drawn fully at
   frame 0, so the file's thumbnail is the title. VIDEO.md Done: also look at
   frame 0 (`ffmpeg -ss 0 ...`).

## Tests

- `tests/check_tts.py` new cases (stand-in phonemizer, no model):
  `It is read-only.`, `The file is read only.` and `They were read only`
  give the lexicon sound; `I read only the summary.` and `She read only two
  chapters.` give None (past tense left alone);
  `Read-Only mode` matches regardless of case; `spread only` and
  `bread-only` give None; `I read it yesterday.`, `read access` and
  `read-write` give None (left to the engine); a sentence that has both
  Engels and "read-only" splices both.
- Build-stage checks outside the repo, results in the delivery:
  - Real Kokoro: synthesize `The disk is read-only, so the job can read it
    but not write.` and transcribe it back with a local Whisper run through
    `uv`, as SKILL.md says. Whisper's language model may spell "red" as
    "read", so the main evidence is the phoneme string Kokoro receives
    (`ɹˈiːd`), which it speaks as given.
  - Re-run the phonemizer probe on whole sentences (read access, read it,
    to read, read-write, past-tense read) and put its output in the
    delivery as evidence that the engine already gets those right.
  - Thumbnail: copy `video/` to `$TMPDIR` with the sample `scenes.json`, run
    TTS and `npm install`, then `npx remotion still Explainer --frame=0`
    and `npx remotion render`. The evidence comes from the encoded MP4, whose
    first frame is the thumbnail: frame 0 pulled with ffmpeg shows ink pixels
    under `signalstats`, and I look at the frame myself, which shows the
    first title. Both results go in the delivery. Frame 0 of the second scene, captured as a still,
    is still blank, which shows only the first scene changed.
- Suite: `python3 tests/check_skills.py`, `tests/check_tts.py`,
  `tests/check_present.py`, `sh tests/check_install.sh`; all pass.

## After merge

Update the installed plugin on each Mac (the Cowboy here, and the Pirate,
Captain and Bald over ssh) the way the researcher rollout did:
`claude plugin marketplace update yudame` then
`claude plugin update yudame@yudame`. Confirm on each that the cached
plugin's `tts.py` has the `read-only` entry.

## Out of scope

- A homograph model or a general "read" rule: the probe shows nothing else
  that needs one.
- `read/write` is said "read slash write": a different word, not changed;
  named in the delivery.
- A poster or thumbnail step separate from the composition.
