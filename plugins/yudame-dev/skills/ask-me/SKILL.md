---
name: ask-me
description: "Interview the user one question at a time to unblock decisions only they can make. Use for 'ask me', 'interview me', or after deep work stalls."
allowed-tools: Read Grep Glob Bash AskUserQuestion
---

# Ask me

You've done deep work (research, investigation, a planning pass or an audit) and it surfaced decisions only the user can make. The user wasn't there and doesn't share your context. Interview them until you can proceed with confidence: one open question at a time, each carrying only the context that changes its answer.

House preference, in order, unless the user says otherwise:
1. **Direction over detail.** Prefer directional questions ("which way are we pointing?") to menus of flags. If a one-line steer from a trusted advisor would unblock you, ask for exactly that.
2. **But the devil is in the details.** When the decision really turns on specifics (an irreversible tradeoff, two paths that diverge sharply, a number, name or path that changes the outcome), those specifics belong in the question. Hiding them to sound high-level makes them answer the wrong question.

Judging which case each question is in is the core of the skill.

Don't interview when the answer is discoverable (read the code, docs, history or issue first), when the choice is low-stakes and reversible (pick a sensible default, note it, move on), or when a single inline yes/no would do.

## Preparing

Re-read what your deep work touched (plan, issue, diff, files, logs) so the user never has to supply something you could recover. Write out every open question privately; the user doesn't see this list. Drop what you can decide or look up, merge questions that are one decision in several forms, and order the rest so the most direction-setting question comes first, because later questions often dissolve once the direction is set.

## Asking well

**Pick the altitude per question.** Ask yourself whether a one-line directional steer would unblock you.
- If yes, ask high and strip the implementation detail: "Are we optimizing this for fewest surprises to existing users, or for the cleanest long-term architecture?"
- If the paths truly diverge on specifics, ask low and put the load-bearing specifics in the question: "Resume-on-crash can replay the last turn (risk: sending a message twice) or skip it (risk: silently dropping the user's reply). Which failure is more acceptable?"

The detail to include is the detail that changes the answer; leave out everything else. A context dump is a briefing, not a question.

**Ask for the principle, not a rule, when a capable agent will act on the answer.** Don't ask the user to author a tie-break heuristic or classification rule for an Opus-class executor; they'll tell you to trust its judgment. Ask what the thing is fundamentally for and let the actor work out the rest.

**Name your key assumption inside the question.** Your framing rests on a model (an architecture, a cost, a constraint) the user may not share and that may be wrong. A compact "under X, …" lets them correct the premise in one reply instead of answering the wrong question.

**Ask one question at a time, with 2-4 options.** Frame it as open: the options are concrete illustrations of the space, your recommendation first and labeled `(Recommended)` when you have one, and room for a free answer you didn't anticipate. You're seeking direction, not steering them through your menu. Ask questions together only when they are genuinely independent, meaning neither answer could reframe or moot the other; otherwise they're a sequence, and a batch can't adapt.

**Adapt after each answer.** A directional answer often makes downstream detail questions moot, so drop them; if it opens a new fork, add it.

## Finishing

Stop when you're unblocked, not when the list is empty. Read back briefly: the direction as you now understand it, the specifics the user pinned down, and the concrete next action you'll take. Confirm before acting on anything irreversible.
