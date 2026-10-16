---
name: do-issue
description: "Create a self-contained GitHub issue after verifying the problem is real and current. Use for 'file an issue' or 'track this'."
allowed-tools: Read Write Edit Glob Grep Bash Agent
argument-hint: "<title or description>"
---

# Create Issue

Write a GitHub issue that a stranger could act on: someone with general engineering experience and no knowledge of this codebase. The do-plan skill reads the issue as its primary input, so every undefined term and stale assumption here turns into a vague or wrong plan later.

A good issue:
- describes a problem that was observed, not reasoned into existence;
- has a scope that matches what the code actually looks like today (nothing already done, nothing that depends on code that doesn't exist);
- defines every project-specific term in one sentence with a link to its source;
- states the problem before any solution, with checkable acceptance criteria.

`gh` targets the current directory's repo; pass `--repo owner/name` or set `GH_REPO` when filing elsewhere. If the repo documents its own issue conventions (labels, a plan-doc path, required sections), follow them over the defaults here.

## Choose the mode

Default to **well-scoped**. Use **blue-sky** only when the requester signals exploration and writing verifiable acceptance criteria would mean inventing specifics they never gave. Premature crispness fabricates certainty nobody has; blue-sky keeps the direction at low resolution and says plainly what is unknown:

- Recon grounds the direction; fan out only on cheap concerns.
- Terms the exploration exists to pin down go in a `## Fog (Not Yet Specified)` section, each with the decision that hangs on it, instead of the Definitions table.
- Acceptance criteria become signals that the fog cleared: still checkable, but naming what will be known or decided rather than a finished feature.

Record the mode in the issue body. Don't stop to ask which mode; pick one.

## Reconnaissance

Before writing, find out what the affected area really looks like; an issue built on a stale premise wastes a full planning and build cycle. Skip recon only for trivial issues (typo, config value, single-file bug with an obvious fix), and run it whenever the area changed in the last week or two, since recent changes are the main source of stale assumptions.

1. **Prior work.** `gh issue list --state all --search "<keywords>"` and `gh pr list --state merged --search "<keywords>"`; `git grep -l` the key terms in docs. Don't file what's already tracked in an open issue.
2. **Broad scan.** One read-only subagent (or you) maps the area: source files, tests, recent PRs, docs describing intended architecture.
3. **Concerns.** From the scan, list 3 to 8 specific, answerable questions. Typical kinds: already done (code or tests exist for a proposed deliverable), conflicting (code contradicts docs, or two systems do the same thing differently), stale (dead imports, "legacy" code), conflated (two independent systems treated as one), missing infrastructure (the request assumes code that is stubbed or absent), architectural mismatch.
4. **Fan out.** One read-only subagent per concern, all in parallel; without subagents, answer them yourself in turn. Give each the question, the file paths from the scan so it doesn't search from scratch, and ask for findings plus a recommendation: include as-is, modify, split out, fix first, or drop. Narrow questions ("is the retry logic in X called in production?") return signal; broad ones return noise.
5. **Synthesize** into four buckets: Confirmed, Revised (scope adjusted), Pre-requisites (must happen first; call out as blockers or split into their own issue), Dropped (already done or wrong assumption). Disagreements between agents are worth surfacing; they usually mark genuine ambiguity.

If recon changed the scope materially and the user is present, show them the four-bucket summary and get agreement on scope before writing. If it confirmed the request as given, carry on.

## Try to kill the issue

Recon asks what the area looks like; this asks whether the problem is real. A wrong issue that reads well costs the next person a full investigation, so try to disprove it yourself first:

- **Observed, not inferred.** Name the artifact that shows it: command output, a log line, a failing test. If the central claim reads "could", "would", or "may", it's a hypothesis: reproduce it or don't file. In blue-sky mode this applies to the pain motivating the direction, not to the specifics still in fog.
- **Counter-cases checked.** A claim of a pattern ("systemic", "always") needs the instances that could have falsified it. Three similar cases that behave correctly make it a one-off.
- **Reachable.** The bad state happens in a supported configuration, not one the code deliberately prevents or heals.
- **Not already decided.** `git grep` for a test, comment, or doc encoding the opposite intent. If one exists, you are proposing to change a decision; argue against that reasoning explicitly, or drop it.

Second-hand findings (from a subagent, a review, another task) need this most: a report is a claim, not a fact. If a check fails, the right output is no issue. Say so where the finding came up and move on.

## Write and publish

Use `ISSUE_TEMPLATE.md` as the skeleton. Notes on the parts that go wrong:

- **Context blockquote** orients the reader; omit it only for self-evident issues.
- **Definitions** for any term that isn't common engineering knowledge. "Redis" and "CI" need no definition; "Observer Agent" or "steering queue" do.
- **Links** for every file, PR, issue, or doc mentioned. No "see the docs" without a URL.
- **Solution sketch** gives direction and constraints, not implementation. When the root cause of an architectural problem is still uncertain, write open questions instead of an approach: the planner will execute a concrete sketch rather than challenge it.
- **Recon Summary** with the four buckets, or `## Recon: Skipped` with the reason.
- **Downstream** says the issue feeds the do-plan skill, plus any constraints the planner must respect.
- Test it: if the do-plan skill would have to ask "what does X mean?", define X.

Write the body to a unique temp file and publish from it. Never use a fixed path such as `/tmp/issue_body.md`: agents sharing a machine have published each other's drafts that way.

```bash
DRAFT=$(mktemp "${TMPDIR:-/tmp}/issue_body.XXXXXX")
cat > "$DRAFT" << 'BODY'
...issue body...
BODY
gh issue create --title "Brief, specific title" --label bug --body-file "$DRAFT"
rm -f "$DRAFT"
```

Label with `bug`, `feature`, or `chore` when the repo has those labels (`gh label list`); `gh issue create` fails on a label that doesn't exist. Report the issue number, title, and URL, and note that it is ready for the do-plan skill.
