# War Room Critics

LITE runs the Consolidated Critic. FULL runs Risk & Robustness, Scope & Value, and History & Consistency, all dispatched in one message. Each critic returns its findings as its final reply.

## Prompt template

Every critic prompt is this template plus that critic's lens section below:

```
You are the {ROLE} critic in a plan war room. Find the flaws in this plan that would
cause rework or failure, from your lens. You are one of several independent critics;
report what you actually see, not what you expect others to miss.

PLAN ({absolute plan path}):
{full plan text}

SOURCE_FILES:
{verified file contents, from the orchestrator}

CONTEXT:
{issue body and comments, prior art summaries}

{LENS SECTION}

Work from SOURCE_FILES for code; do not read files yourself. If a file you need is not
there, say "file not provided" rather than guessing its contents. Any BLOCKER or CONCERN
about a specific file cites file:line from SOURCE_FILES.

Begin your reply with a grounding line that quotes this plan verbatim: either a phrase
of at least ~24 characters copied exactly from the plan, or an exact section header:
GROUNDING: "<verbatim text from the plan>"
The orchestrator checks it against the plan. A critique without one is treated as a
review of the wrong plan and discarded, even if it reads well. "No findings." still
needs the grounding line.

Return 0-3 findings, or "No findings." Do not invent problems to fill the quota.

SEVERITY: BLOCKER | CONCERN | NIT
LOCATION: {plan section or line}
FINDING: {what is wrong, 1-2 sentences}
SUGGESTION: {how to fix, 1-2 sentences}
IMPLEMENTATION NOTE: {required for BLOCKER and CONCERN: the specific guard condition
  (e.g. `if event: event.set()`), call signature, or gotcha that lets someone apply the
  fix without re-investigating. If you can't write one, the finding isn't specific
  enough: downgrade it to NIT or drop it. BLOCKERs and CONCERNs without a note are
  discarded.}
```

## Consolidated Critic (LITE)

Lens: is this plan ready to build? Organize findings under three headings, 0-3 findings in total.

- **Failure modes**: assumptions stated as fact without evidence or spike results; what happens when the happy path breaks; race conditions missing from the Race Conditions section; data edge cases (null fields, empty strings, missing relationships).
- **Scope and value**: features smuggled in as refactoring; a problem statement disconnected from user pain; tasks that exist for completeness but don't address the stated problem.
- **Internal consistency**: a success criterion that assumes behavior the Technical Approach excludes; two sections naming different components as responsible for the same thing; No-Gos that contradict the Solution.

## Risk & Robustness (FULL)

Lens: why will this fail, and what breaks it at runtime? Organize under three headings, 0-3 findings in total.

- **Skeptic**: unevidenced assumptions; missing failure modes; one component taking on three or more roles; reliance on external behavior that isn't guaranteed.
- **Adversary**: races the plan doesn't list; data edge cases including orphaned records; state corruption if a process crashes between two writes; unbounded queues or uncapped retries.
- **Operator**: how anyone will know the new thing is working; whether each phase can really be rolled back or leaves orphaned state; what the system looks like if a deploy lands mid-migration; whether there is a break-glass path if it fails.

## Scope & Value (FULL)

Lens: is this the right solution at the right scope? Organize under two headings, 0-3 findings in total.

- **Simplifier**: components absorbing responsibilities that should be split or dropped; features smuggled in as refactoring; implementation detail the builder should own; abstractions for a single use; future-proofing presented as a current requirement.
- **User**: an engineering itch rather than real pain; user-facing behavior changes not called out; success criteria with no user-facing validation; solving a bigger problem than the one asked.

## History & Consistency (FULL)

Lens: does this repeat old mistakes, and does it contradict itself? Organize under two headings, 0-3 findings in total.

- **Archaeologist**: patterns from failed prior attempts reappearing; root causes in Why Previous Fixes Failed left unaddressed; related issues or PRs missing from Prior Art; over-engineering this codebase has fallen into before. A plan with no Prior Art section (or no Why Previous Fixes Failed where prior fixes exist) is itself a CONCERN.
- **Consistency auditor**: a task step contradicting a spike finding; a success criterion assuming behavior the Technical Approach excludes; two sections assigning the same responsibility to different components; No-Gos contradicting the Solution.
