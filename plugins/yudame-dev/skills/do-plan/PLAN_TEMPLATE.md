---
status: Planning
type: [bug | feature | chore]
appetite: [Small | Medium | Large]
owner: [Name]
created: [YYYY-MM-DD]
tracking: [GitHub issue URL]
last_comment_id: [ID of the latest issue comment incorporated into this plan]
---

<!-- Bracketed text is guidance: replace it. Sections marked CONDITIONAL are deleted
     when they don't apply. Any other section that doesn't apply stays, with a
     one-line statement of why (e.g. "No race conditions: all operations are
     synchronous"), so reviewers can tell "considered and empty" from "forgotten".
     If the repo mandates its own sections, add them. -->

# [Feature Name]

## Problem

[A real scenario showing the pain, from the user's side. Specific, not vague.]

**Current behavior:** [What happens now]

**Desired outcome:** [What success looks like]

## Freshness Check

**Baseline commit:** [`git rev-parse HEAD` at plan time]
**Issue filed at:** [`gh issue view N --json createdAt`]
**Disposition:** [Unchanged | Minor drift | Major drift | Overlap]

**File:line references re-verified:**
- `path/to/file.py:NNN`: [what the issue claimed] → [still holds | moved to line MMM | gone]

**Cited issues/PRs re-checked:**
- #NNN: [still open | closed on DATE: resolution]

**Commits since the issue was filed (touching referenced files):**
- `abc1234` [title]: [irrelevant | partially addresses | changed root cause | already fixes]

**Overlapping active plans:** [none | slugs and how they overlap]

## Prior Art

[Related closed issues and merged PRs: what each attempted and whether it worked. If none: "No prior issues found related to this work."]

- **#N** [Title]: [what it did, outcome, relevance]

## Research

[CONDITIONAL: delete for purely internal work.]

**Queries:** [search queries used]

**Findings:**
- [Finding, source URL, how it shapes the approach]

## Spike Results

[CONDITIONAL: delete if no spikes ran.]

### spike-1: [What was verified]
- **Assumption**: "[What was tested]"
- **Method**: [code-read | web-research | prototype]
- **Finding**: [What was found]
- **Confidence**: [high | medium | low]
- **Impact on plan**: [How it shaped the solution]

## Data Flow

[For changes that cross components: trace from entry point (user action, API call, event) through each component, transformation, and storage layer to the output. This is what keeps a fix from landing at the wrong layer.]

1. **Entry point**: [...]
2. **[Component]**: [...]
3. **Output**: [...]

## Why Previous Fixes Failed

[CONDITIONAL: only when Prior Art found earlier attempts at the same problem.]

| Prior fix | What it did | Why it failed or was incomplete |
|-----------|-------------|--------------------------------|
| PR #N | [...] | [wrong root cause, wrong layer, symptom only, ...] |

**Root cause pattern:** [What connects the repeated failures]

## Architectural Impact

- **New dependencies**: [libraries, services]
- **Interface changes**: [APIs, signatures, contracts]
- **Coupling**: [increases or decreases, between what]
- **Data ownership**: [does ownership of any data move?]
- **Reachability**: [How new functionality is wired into its callers: the entry point, CLI, tool, or MCP surface that invokes it, and the test proving it is invoked. New code nothing calls is a common miss.]
- **Reversibility**: [How hard to undo]

## Appetite

**Size:** [Small | Medium | Large]

**Team:** [e.g. "Solo dev" or "Solo dev, PM, reviewer"]

**Interactions:** PM check-ins [0 | 1-2 | 2-3]; review rounds [0 | 1 | 2+]

## Prerequisites

[Environment requirements, each with a command that checks it. If none: "No prerequisites."]

| Requirement | Check command | Purpose |
|-------------|---------------|---------|
| `EXAMPLE_API_KEY` set | `test -n "$EXAMPLE_API_KEY"` | Service access |

## Solution

### Key Elements

- **[Component]**: [what it does, not how]

### Flow

[Breadboard: **Starting place** → [affordance] → **Next place** → ... → **End state**.
Example: Settings → Click "Enable 2FA" → Setup screen → Enter code → Confirmation → Settings (2FA on)]

### Technical Approach

[Direction and key decisions, abstract enough to leave the builder room. Include corrected file:line references from the Freshness Check.]

## Failure Path Test Strategy

[Silent failures are their own bug class: exceptions swallowed without logging, empty outputs that loop, error states that render wrong. Cover each:]

- **Exception handling:** [Each `except Exception: pass` (or equivalent) in touched code gets a test asserting observable behavior: a log, metric, or state change. Or: "No exception handlers in scope."]
- **Empty and invalid input:** [Behavior on empty strings, None, whitespace; tests for each new or modified function. If processing agent output, confirm empty output can't cause a silent loop.]
- **Error rendering:** [For user-visible output, test the failure path and confirm errors reach the user.]

## Test Impact

[Existing tests that will break or change, each with a disposition:]

- [ ] `tests/unit/test_example.py::test_old_behavior`: UPDATE, [what changes]
- [ ] `tests/integration/test_flow.py::test_end_to_end`: REPLACE, [why]
- [ ] `tests/unit/test_legacy.py::test_removed_path`: DELETE, [why]

[Or: "No existing tests affected: [justification]."]

## Rabbit Holes

- [Tempting avenue that would swallow the appetite]

## Risks

### Risk 1: [Description]
**Impact:** [What breaks]
**Mitigation:** [How it's handled]

## Race Conditions

[For each timing hazard. Or: "No race conditions: [justification]."]

### Race 1: [Description]
**Location:** [file and lines]
**Trigger:** [Sequence of events that causes it]
**Prerequisite:** [Data or state that must exist before the dependent operation]
**Mitigation:** [await, lock, re-read, idempotency, ...]

## No-Gos (Out of Scope)

[Every entry carries a tag; see SCOPING.md. If the work could be finished in this plan, do it instead of deferring. For a No-Go describing a forbidden code-level outcome, add an inverse row to Verification that detects it.]

- [EXTERNAL] [Needs a human or outside-system action: why]
- [ORDERED] [Waits on a human-gated event: name it]
- [DESTRUCTIVE] [Irreversible one-shot reviewed before execution]
- [SEPARATE-SLUG #NNN] [Different feature, already filed]

[Or: "Nothing deferred: every relevant item is in scope."]

## Rollout

[If this code is deployed or propagated to other environments or machines: changes to the deploy or update process, new dependencies or config to propagate, migration steps for existing installs. Or: "No rollout changes: [why]."]

## Documentation

- [ ] [Feature doc to create or update, and the docs index entry, in the repo's docs location]
- [ ] [External docs site pages, if the repo has one; confirm it builds]
- [ ] [Docstrings for changed public APIs; comments on non-obvious logic]

[Or: "No documentation changes: [why]."]

## Success Criteria

[Measurable outcomes tied to the appetite.]

- [ ] [Criterion]
- [ ] Tests pass (the do-test skill)
- [ ] Documentation updated (the do-docs skill)
- [ ] [If Reachability names a caller: grep confirms the caller references the new code]
- [ ] [Bug fix: related xfail tests converted to hard assertions]

## Team Orchestration

The lead agent executing this plan coordinates and does not build directly. Name each team member so tasks can reference them; the usual pattern is a builder and validator pair per major component.

- **[unique-name, e.g. api-builder]**: role [single responsibility], type [builder]
- **[api-validator]**: role [what it verifies], type [validator]

Roles: `builder` (implementation, the default), `validator` (read-only verification), `code-reviewer`, `test-engineer`, `documentarian`. For broad reconnaissance use the built-in Explore or general-purpose agents. For domain-heavy work, tag the task `Domain: <tag>` and paste the rules from `DOMAIN_FRAMING.md` into its assignment.

## Step by Step Tasks

[Each task becomes one task for the builder. Build tasks may run in parallel; a validator waits for its builder.]

### 1. [Build task]
- **Task ID**: build-[component]
- **Depends On**: none
- **Validates**: [tests that must pass, e.g. tests/unit/test_component.py, tests/integration/test_bar.py (create)]
- **Informed By**: [spike IDs and findings]
- **Assigned To**: [team member]
- **Agent Type**: builder
- **Parallel**: true
- [Specific action]

### 2. [Validation task]
- **Task ID**: validate-[component]
- **Depends On**: build-[component]
- **Assigned To**: [team member]
- **Agent Type**: validator
- **Parallel**: false
- [Verify against criteria; run the checks; report pass/fail]

### N-1. Documentation
- **Task ID**: document-feature
- **Depends On**: [final build/validate IDs]
- **Agent Type**: documentarian
- **Parallel**: false
- [Docs listed in the Documentation section]

### N. Final validation
- **Task ID**: validate-all
- **Depends On**: [all previous IDs]
- **Agent Type**: validator
- **Parallel**: false
- [Run every Verification check; confirm every Success Criterion; report]

## Verification

[Checks the do-build skill runs automatically after the build. A check table is identified by a `Command` column within its first three columns; a Verification section with table rows but no `Command` column fails the gate rather than passing on zero checks. Any other table here (a summary, a recap) is skipped as a non-check table.

Expected-result grammar:
- `exit code N`: passes when the exit code equals N (`exit code 1` for "grep found nothing").
- `exit code != N`: passes when it does not.
- `output > N`: stdout parsed as an integer is greater than N.
- `output contains X`: X appears in stdout.
- `output does not contain X`: X is absent and stdout is non-empty (an empty stdout usually means the command errored).
- `match count == 0`: every non-blank stdout line is `0` or ends in `:0` (fits `grep -c`, `grep -rc`, `... | wc -l`), and stdout is non-empty.

Inverse rows (anti-criteria) assert a No-Go outcome is absent. Add one only when a command can detect the violation mechanically, and show it failing against a deliberately violating input first; put that output in the PR description.]

| Check | Command | Expected |
|-------|---------|----------|
| Tests pass | `[repo test command]` | exit code 0 |
| Lint clean | `[repo lint command]` | exit code 0 |
| No stale xfails | `grep -rn 'xfail' tests/ \| grep -v '# open bug'` | exit code 1 |
| [Anti-criterion] | `grep -c "forbidden_pattern" path/to/file.py` | match count == 0 |
| [Feature check] | `[command]` | [expected] |

## Critique Results

[Filled by the do-plan-critique skill.]

| Severity | Critic | Finding | Addressed By | Implementation Note |
|----------|--------|---------|--------------|---------------------|

---

## Open Questions

[Only questions a human must answer: scope, priorities, tradeoffs. Removed when the plan is finalized.]

1. [Question]
