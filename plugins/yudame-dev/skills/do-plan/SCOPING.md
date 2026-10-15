# Scoping (Shape Up)

How to narrow, size, and bound a plan before writing it.

## Narrow the problem

A plan solves one specific pain. "Improve the API" is not plannable; "API responses take 3+ seconds when fetching users with nested relationships" is. Ask what pain, who is blocked, and where it breaks down.

How to respond to the three common request shapes:

- **Vague** ("make the auth better"): ask a narrowing question with concrete options. Is login failing for some users, is the flow too complicated, is there a security concern, is it slow? Or offer the story shape: "Users with [situation] can't [action] because [breakdown]."
- **Grab-bag** ("redesign settings: dark mode, notification preferences, profile editing, export"): several unrelated features are several plans. Name them and ask which is most urgent, or whether one pain drives them all.
- **Good** ("users can't reschedule a meeting while the original attendee is offline"): proceed, and state the appetite you are starting from.

### Fog-forward issues

When the issue has a `## Fog (Not Yet Specified)` section or records blue-sky mode, the goal is a direction whose specifics are genuinely unknown. Narrowing it would fabricate certainty. Instead:

- Resolve what can be resolved now (spikes, reading code) and carry the rest as a **Not Yet Specified** list. Items graduate into tasks as they clear.
- When the work spans several interdependent decisions across sessions, chart a decision map: one parent issue holding the destination, decisions made, and open fog, plus one child issue per decision. Resolve one decision at a time, record it on the map, re-plan.
- One unknown direction is fog: chart it. Several known, unrelated features are a grab-bag: split them.

## Set appetite first

Appetite is a communication budget. Solo coding is fast; alignment and review are the real cost. Fixed interactions with variable scope ships; fixed scope with variable interactions does not.

- **Small**: solo, no review. Ship it.
- **Medium**: solo plus PM. One or two check-ins on scope, one review round.
- **Large**: solo, PM, and reviewers. Two or three check-ins, two or more review rounds.

Good is relative to appetite. Do not pursue polish beyond the budget, and do not add nice-to-haves beyond it.

## Walk the use cases

Where does the user start, what do they do, where do they end up, what can go wrong? Show the flow as a breadboard (Place → Affordance → Place) rather than mockups or implementation detail.

## Rabbit holes and risks

Rabbit holes are tempting avenues that would swallow the appetite ("don't support every auth provider, just Google and GitHub"; "offline sync would triple the scope"). Risks are things that could fail (rate limits, a migration on a large table, browser unknowns). Name both so the builder avoids the first and watches the second.

## Boundaries and No-Gos

Default to doing it now. If a "follow-up" touches only files already in this change set, fold it in: splitting it across PRs costs more coordination than the work. An audit of old plans found most "operator step" and "follow-up issue" deferrals were avoidable.

A No-Go is legitimate only with one of these tags:

- `[EXTERNAL]`: a human or outside system must act (rotate a secret, click a third-party UI, run on a machine the agent can't reach).
- `[ORDERED]`: must wait for a human-gated event elsewhere (a separate deploy, a release window, a downstream merge).
- `[DESTRUCTIVE]`: an irreversible one-shot where review before execution is the safety mechanism (data deletion, a migration on a hot table).
- `[SEPARATE-SLUG #NNN]`: a genuinely different feature, already filed as issue NNN. File the issue first.

An untagged "later" is not a No-Go. If nothing is out of scope, say so.

## Anti-patterns

Over-specifying implementation, starting from "how long will this take?" instead of "how many people need to weigh in?", designing for every edge case, skipping technical unknowns, and leaving "done" undefined. Make tradeoffs explicit: "we're choosing speed over completeness here."
