# Manifesto

These skills exist because a capable model, left to its defaults, does work that looks finished before it is. It trusts what an issue said last month. It grades its own drafts. It reports success nobody can check, and it asks the user questions it could have answered by reading. Each skill is a correction to one of those habits, written down once so it holds in every repo.

## Start from what is true today

Read before you ask, and read before you write. Issues go stale, line numbers move, and fixes land while a plan waits in a queue, so `do-plan` runs a freshness check and `do-issue` tries to kill its own issue before filing it. A claim needs an artifact behind it: a log line, a failing test, a command's output. If the honest word is "could", it is a hypothesis. It goes to `do-investigation-issue` rather than being dressed up as a defect. Audits run the search that would prove them wrong.

## Done means someone else can check it

A verdict that exists only in the model's output does not count. Reviews get posted to the PR, plans carry verification rows a machine can run, and tests report which failures this branch caused. A deck counts as done when the PDF exists and the fonts actually loaded. Every skill names a done condition that a person or a script can inspect outside the conversation.

## The maker does not judge its own work

The author of a draft is its worst reader. Builders write the code and the build lead checks their diffs without touching the files. Critics in `do-plan-critique` work without seeing each other's reasoning, and `de-slop` reads cold, with no access to the conversation that produced the draft. The supervisor in `do-sdlc` never does stage work itself. Keeping these roles separate is how a model can catch its own mistakes.

## Gates refuse, and refusing is cheap

A refused merge costs one retry, while a bad merge can cost days. `do-merge` names the fact it could not confirm and stops. `do-patch` stops when the right fix is architectural. `do-test` and the audits only report what they find, and a human decides what to fix. Each skill owns one job and hands the rest to the skill that owns it. Repo addenda can make a gate stricter but never looser.

## Change only what needs changing

Recover the intent before fixing anything. A patch that makes the test pass but drifts from the plan is not a fix. `do-patch` and `do-docs` make the smallest edit that is correct, and they leave accurate work alone.

## The user's attention is the scarcest resource

Do everything that can be discovered or safely defaulted, and ask only what only the user can decide. When a question is needed, ask one at a time and include only the detail that changes the answer. Put the recommendation first so their job is to veto, not deliberate. Human checkpoints belong in front of irreversible or outward-facing actions such as sending, merging, deleting or spending money, and nowhere else.

## What reaches a reader has to earn it

A draft with nothing to say gets blocked, however polished it is. Interfaces should look like a person made them, not like the default output of a model. Decks open with the audience's problem before offering a solution. `de-slop` works by naming the defaults and steering away from them, and where a project has no style of its own, `house-style` gives every visual one consistent voice.

## Silence is not health

A routine that broke and a routine that found nothing look the same from outside. Advisory hooks log their own failures, and validators must actually block. Write a temp file to a unique path, because a fixed one gets clobbered by the next agent. Wherever a skill could fail quietly, it is set up so the failure shows.

## A skill teaches what the model would not otherwise know

Skills describe outcomes and give the reason for each constraint, so the model can handle the edge case nobody wrote down. They keep the hard-won specifics verbatim: the header that returns a 401, the save that loses data, the grep flag macOS lacks. They leave out steps a strong model would take anyway, because every description shares one context budget. The repo's own conventions always win over these defaults.
