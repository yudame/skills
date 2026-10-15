---
name: de-slop
description: "Pre-publish editorial gate for external-audience writing: removes AI-writing tells and blocks drafts with nothing to say. Use on a finished draft of a document, deck, email, post or web copy, on 'de-slop this', 'editorial pass', 'humanize this', 'remove the AI tells', or when another skill (email, present) gates its output through it."
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: "[draft-file-path]"
user-invocable: true
---

# De-slop

An editorial pass that runs after a first draft exists and before it reaches its audience. It does two jobs:

1. **Substance.** A draft with nothing in it doesn't ship, however clean. The pass can block it and send it back with a diagnosis.
2. **Style.** Remove the characteristic signs of AI writing (slop vocabulary, formulaic structure, inflated significance, formatting tics) while keeping the draft's meaning, facts and voice, then make sure the result reads with ease rather than overcorrected punch.

Drafting skills don't carry these style rules; they hand finished drafts here, the way a reporter files and a copy editor works afterwards. The scope is external-audience artifacts: email, documents, presentations, posts, web copy. Conversational replies are dialogue, not drafts, and aren't gated.

## Read cold

The author of a draft is its worst judge: same model, same context, full commitment to what it meant to say. When another skill gates through this one, run the review in a fresh context (a subagent or forked context) that receives only the draft, the medium and the audience, never the drafting conversation, and judge it as a first-time reader would. When a user invokes `/yudame:de-slop` directly it may run inline, but if this context wrote the draft, spawn the fresh review anyway.

## Input and output

- A file path: read it and edit in place.
- Pasted text: return the edited draft in the reply.
- Called by another skill: edit the given path in place and return the verdict and change log so the caller can proceed.

If the repo or user has declared house style (tells to ignore, such as "em dashes are part of my voice", extra tells, spelling conventions), honor it. Look for it in the project's CLAUDE.md or a style note the caller passes in.

## Reference files

- [references/SIGNS.md](references/SIGNS.md): the full catalog of tells with before-and-after examples. Read it for anything longer than a short message, or when a call is borderline.
- [references/PROSE.md](references/PROSE.md): the reader's-ear principles (register, rhythm, warmth, grounding) for the prose pass. Read it for anything longer than a short message.

For a message of a few sentences, the condensed catalog below is usually enough.

## The pass

1. **Read the whole draft first.** Note the medium (message, document, deck, web copy), the audience and the author's voice. The target is that voice minus the slop, not a neutral house rewrite.
2. **Check substance before polishing.** If every tell were stripped, would a piece remain? The draft needs at least one concrete specific the reader didn't already have (a fact, number, name, example or decision) and a discernible point (something the reader should do, decide or newly understand). Missing both means BLOCK with a diagnosis. Polished emptiness sent to a real audience is worse than a rough draft.
3. **Sweep for tells.** Collect findings with location and category. Judge as a competent human editor would: one "robust" is fine, while a cluster of tells in one paragraph or the same construction three times in a page is the signal. A finding is a pattern, never a banned-word hit.
4. **Rewrite with the smallest edit that removes each tell:** delete the filler clause, use the plain word, break the triad, turn the bullet wall into prose. Your replacements come from the same kind of model that produced the tells, so re-scan your own edits afterwards.
5. **Prose pass.** Re-read the result, especially your edits, against PROSE.md for the overcorrection failure: prose gone staccato, knowing, too clever, or jargon dressed in metaphor. Tell removal gets a draft to not-suspicious; this pass gets it to pleasant to read, with one held register, sentences that breathe, abstractions replaced by plain facts (never by new metaphors), and warmth over wit. This pass rewrites; it doesn't block.
6. **Report** the verdict and change log below, including anything you flagged but deliberately kept, and why.

## What the pass leaves alone

- **Substance.** Facts, numbers, names, quotes, commitments and hedges that carry real uncertainty survive verbatim. If a claim looks wrong, flag it in the report rather than fixing it; facts belong to the author.
- **Voice.** A tell used once with evident intent is not a finding. Removing slop should make the piece sound more like its author.
- **Structure the medium needs.** Decks need bullets, runbooks need numbered steps, a README needs headings.
- **Nothing gets added.** No new claims, examples or enthusiasm; the pass removes and rewords.
- **No overcorrection into punchiness.** Staccato fragments and a punchline per paragraph are their own slop. Fragments are seasoning, about once a page; three consecutive sentences under ten words means merge two; connective tissue ("even so", "which is why") stays.

## Condensed catalog

- **Slop vocabulary:** delve, tapestry, testament, underscore, pivotal, crucial, robust, seamless, leverage, boasts, foster, elevate, landscape, realm, journey, vibrant, comprehensive, "it's worth noting", "in today's fast-paced world". Use the plain word or delete.
- **Negative parallelism:** "not just X, but Y", "it's not about X, it's about Y". Say the true thing directly.
- **Rule of three:** compulsive triads of adjectives, clauses or examples. Keep the strongest, or use two or four.
- **Copula avoidance:** "serves as", "functions as", "stands as", "features" where "is" or "has" is meant.
- **Trailing significance clauses:** ", highlighting the importance of…", ", ensuring…". Delete; if the point matters, give it a real sentence.
- **Inflated significance:** "marks a pivotal moment", "plays a vital role". State the concrete stake or cut.
- **Grand metaphor on technical material:** "a symphony of microservices", "the beating heart of the pipeline". Replace with the plain fact or number, never another metaphor.
- **Weasel attribution:** "experts agree", "many believe". Name the source or own the claim.
- **Formulaic scaffolding:** intros previewing the sections, conclusions restating them, "In conclusion", "Challenges and Future Prospects" sections.
- **Formatting tics:** mechanical bold, `**Header:** description` bullet walls that should be prose, emoji as bullets or dividers, title case where sentence case is house style, gratuitous horizontal rules, em dashes doing the work of commas and periods.
- **Message boilerplate:** "I hope this email finds you well", "Great question!", reflexive "Let me know if you have any questions!", restating the question back.
- **Hedge-hype mix:** "could potentially", "truly unique", stacked intensifiers.
- **Uniform rhythm:** every sentence the same length and shape, every paragraph three sentences.
- **Artifacts, always bugs:** citation markers (`oaicite`, `contentReference`, `turn0search`, `[cite: 1]`), placeholder text ("This section would explore…"), knowledge-cutoff disclaimers.

## Medium notes

- **Messages and email:** boilerplate openers and closers, three paragraphs for a one-line answer, headers and bold in a short message.
- **Documents:** scaffolding, bold overuse, section summaries, title-case headings, bullet walls.
- **Presentations:** bullets are fine; watch for rule-of-three slides, inflated titles, identical rhythm on every slide.
- **Web and marketing copy:** promotional adjective stacks ("vibrant", "seamless", "nestled"), hedge-hype, negative parallelism in headlines.

## Verdict

```
DE-SLOP: PASS (edited, 14 changes)   # or PASS (clean), or BLOCK

  vocabulary (5)      "leverage" → "use", "pivotal" → cut, ...
  parallelism (2)     "not just a tool, but a partner" → "a tool that ..."
  scaffolding (1)     cut closing paragraph restating the three sections
  boilerplate (2)     cut "I hope this finds you well", "Great question!"
  artifacts (1)       removed stray "[cite: 3]"
  register (2)        "symphony of retries" → "each retry waits twice as long"
  rhythm (1)          merged a staccato run of four fragments in §3

  KEPT: two em dashes in §2, doing real appositive work
  FLAGGED (not fixed): "$40k saved", verify before sending
```

```
DE-SLOP: BLOCK

  DIAGNOSIS: [what is hollow, e.g. "three sections of scaffolding around zero
  specifics; no number, example, or decision a reader could act on"]

  TO UNBLOCK: [the real material that would fill it, drawn from what the draft
  gestures at, e.g. "the migration date, the metric that motivated this, or
  the decision you're asking the client to make"]
```

What the caller does with it: on PASS, proceed to send, export or publish. On BLOCK, return the draft to the drafter with the diagnosis as revision instructions and rerun this pass, in a fresh context again, on the revision. After two BLOCKs, stop and show the human the draft and both diagnoses rather than shipping or looping; a draft that can't find one concrete specific in three tries has a sourcing problem, not a writing problem.

For social posts, a stricter substance check (a metric, a constraint, an opinion) is worth running after this pass if one is available; for everything else this pass is the pre-publish gate.
