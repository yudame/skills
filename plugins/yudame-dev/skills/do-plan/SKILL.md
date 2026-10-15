---
name: do-plan
description: "Turn a request or issue into a grounded plan document a builder can execute. Use for 'make a plan', 'plan this', or scoping work."
allowed-tools: Read, Write, Edit, Glob, Bash, AskUserQuestion, ToolSearch, WebSearch, Agent
---

# Make a Plan (Shape Up)

Turn a request or GitHub issue into a plan document that a builder can execute without re-investigating: a narrowed problem, an appetite, a rough solution, the rabbit holes and boundaries, and machine-checkable verification. The plan lives at `docs/plans/{slug}.md` (snake_case slug), is linked to a tracking issue, and goes to `/yudame-dev:do-plan-critique` before `/yudame-dev:do-build`.

A good plan is grounded in the code as it is today, not as the issue described it weeks ago; it is sized by how much alignment the work needs, not by coding time; and every open question left in it is one only a human can answer.

If the repo documents its own planning conventions (required plan sections, frontmatter fields, an infra-docs directory), follow them over the defaults here. `gh` targets the current checkout's repo; if the work belongs to another repo, point `gh` at it (`GH_REPO` or `--repo`).

Supporting files:
- `PLAN_TEMPLATE.md`: the plan document structure. Copy it when writing.
- `SCOPING.md`: narrowing vague or grab-bag requests, fog-forward issues, appetite sizing, legitimate No-Gos.
- `DOMAIN_FRAMING.md`: domain rules to paste into tasks that need specialist framing (async, security, data, API integration, testing).

## 1. Ground the plan in current reality

Explore before writing. Plans built on stale or unverified premises are the main source of rework.

**Recon.** The source issue should carry evidence (a `## Recon Summary` or equivalent) that grounds its claims in the code. If it does not, verify the claims yourself before planning.

**Freshness.** Issues sit for days or weeks while code moves. Skip this only if the issue was filed within the last hour and nothing has landed on main since. Otherwise:
- Read every `file:line` the issue cites and confirm the code still matches. Record corrected locations; flag references whose code is gone (the problem may already be fixed).
- Check every cited issue or PR (`gh issue view N --json state,closedAt,title`, `gh pr view N --json state,mergedAt,title`). If one closed or merged since filing, read its resolution and whether it touched the same files.
- List commits on the relevant files since the issue was filed (`git log --oneline --since="$(gh issue view N --json createdAt -q .createdAt)" -- <files>`) and read the diffs. Classify each: irrelevant, partially addresses, changed the root cause, or already fixes.
- Look for active plans in `docs/plans/` touching the same area.
- For a bug, reproduce it on current main, or read the code path and confirm the defect is still present.

Record the result in the plan's `## Freshness Check` with a disposition:

| Disposition | Meaning | Action |
|---|---|---|
| Unchanged | Claims still hold | Proceed; record the baseline commit SHA |
| Minor drift | Lines moved, or a related PR merged without changing the root cause | Correct the references and proceed |
| Major drift | Root cause changed, or something already fixes it | Stop and ask whether to close, rescope, or proceed on a revised premise |
| Overlap | An active plan covers the same area | Surface it and ask whether to merge or coordinate |

A bug that no longer reproduces is a question for the user (close the issue?), not a plan.

**Understand the request.** Read the full issue body and comments. Carry the Problem, Desired Outcome, and acceptance criteria into the plan verbatim. If there is a Recon Summary, its Confirmed / Revised / Pre-requisites / Dropped buckets feed the Solution and No-Gos.

**Prior art.** Search closed issues and merged PRs for the same problem (`gh issue list --state closed --search "..." --json number,title,closedAt,url`, same for `gh pr list --state merged`). Fill Prior Art; if earlier fixes failed, work out why (wrong root cause, wrong layer, symptom-only, regressions) and fill Why Previous Fixes Failed. Skip for small greenfield work.

**Blast radius and data flow.** Map the files the change touches with `git grep` and Grep/Glob over the named symbols. Route what you find: files to modify go in Solution, dependents in Risks, tests in Test Impact and Success Criteria, docs in Documentation, tangential coupling in Rabbit Holes. When the change crosses components, trace the data flow from entry point to output so the fix lands at the right layer. If the repo keeps infrastructure docs (for example `docs/infra/`), check them for rate limits, quotas, and deploy constraints.

**Expected-failure tests (bug fixes).** Search for tests that document the bug as an expected failure: `grep -rn 'pytest.mark.xfail\|pytest.xfail(' tests/` in Python, or the equivalent skip/known-failure mechanism elsewhere. Each related one becomes a task to convert it into a hard assertion. Runtime `pytest.xfail()` calls inside a test body matter most: they short-circuit before the assertions, so they keep passing after the bug is fixed and pytest's XPASS detection never sees them.

**External research.** When the work involves external libraries, APIs, or ecosystem patterns, run one to three web searches for current docs, best practices, and known pitfalls or breaking changes. WebSearch may be a deferred tool; load it with `ToolSearch("select:WebSearch")`. Record queries, findings with URLs, and how each shapes the approach in `## Research`. Skip for purely internal work.

## 2. Shape the solution

- Narrow the problem (see `SCOPING.md`). A vague request gets a narrowing question; a grab-bag gets split into separate plans. A fog-forward issue (a `## Fog (Not Yet Specified)` section, or blue-sky mode) keeps its low resolution: do not narrow the fog away.
- Set appetite (Small / Medium / Large) by alignment and review overhead.
- Rough out the solution: key elements, a breadboard flow, and the technical direction, abstract enough to leave the builder room.
- If the solution involves async work, shared mutable state, or cross-process data, name each timing hazard: what state must exist before what reads it, and how the implementation guarantees that.

## 3. Resolve assumptions with spikes

List the assumptions an agent could verify (by reading code, researching, or prototyping) and resolve them before writing, so only genuine human-judgment questions reach Open Questions. Dispatch spikes as parallel subagents in one message: Explore for code reads, general-purpose for research, and a builder with `isolation: "worktree"` for prototypes so nothing lands in the repo. Each returns a finding with a confidence level and what changes in the plan if the assumption is false. Cap at 2 spikes for Small appetite, 4 for Medium, uncapped for Large. For a fog-forward issue, send survey spikes to a cheaper model and spend your own reasoning on the decision the fog hangs on. Record results in `## Spike Results`.

## 4. Write the plan

Copy `PLAN_TEMPLATE.md` to `docs/plans/{slug}.md`. Frontmatter must carry `status: Planning` and a `type:` of bug, feature, or chore.

Write incrementally: first a skeleton with every heading and one-line placeholders, commit it, then fill sections with Edit and commit every two or three sections. Large single writes have died mid-flight and left nothing; a committed skeleton lets a successor resume. The same applies to revision passes on large plans.

Before committing the finished draft, check that the task list agrees with the final Technical Approach and spike results. Task bullets written early often still name a library, function, or pattern a spike ruled out; fix them so the builder gets the final design.

If the plan adds dependencies, services, external API calls, or deployment changes and the repo keeps infrastructure docs, add one (current state, new requirements, rules and limits, rollback). Those docs persist after the plan ships.

## 5. Commit, push, and link the tracking issue

Plans are documentation: commit them on `main` and push. `/yudame-dev:do-build` creates the feature branch later. If you are on another branch, move to main without carrying unrelated changes, and stage the plan by path, never `git add -A`. If main is protected, use a `plan/{slug}` branch and PR. Do not leave a plan edit uncommitted while you wait on a subagent, critique, or human: other sessions may pull or rebase the same checkout, and an autostash conflict on a plan file has cost a full reconciliation before.

Tracking issue:
- If the plan came from an existing issue, use it: add the `plan` label and prepend `**Plan:** https://github.com/{owner}/{repo}/blob/main/docs/plans/{slug}.md` to its body.
- Otherwise create one with labels `plan` and the plan's type, a one-line header (`**Type:** … | **Appetite:** … | **Status:** Planning`), and the plan link. The plan document is the source of truth; the issue is for tracking and discussion.
- Set the plan's `tracking:` to the issue URL and commit.
- A plan commit or plan PR must never use a closing keyword (Closes, Fixes, Resolves) for the tracking issue. Only the implementation PR closes it.

Check the tracking issue for comments newer than the plan's `last_comment_id` (`gh api repos/{owner}/{repo}/issues/N/comments --jq '.[] | {id, author: .user.login, body}'`). Fold relevant feedback into the plan and update `last_comment_id`.

## 6. Hand off

Add questions that need human input to `## Open Questions`, then reply with the plan path, the tracking issue URL, the key assumptions you made, and a pointer to the Open Questions. The next step is `/yudame-dev:do-plan-critique`.

## 7. Finalize or revise

After answers come back, incorporate them, remove the Open Questions section, and set `status: Ready`.

On a revision pass after critique (NEEDS REVISION, MAJOR REWORK, or READY TO BUILD with concerns): apply the findings, embedding each concern's Implementation Note into the relevant plan text so the builder does not have to re-investigate. Then set `revision_applied: true` and `revision_applied_at: <ISO-8601 UTC>` in the same edit (the timestamp lets a pipeline router tell this revision from a later unrelated one), commit, and push. A plan revised after a "with concerns" verdict goes back through `/yudame-dev:do-plan-critique`, not straight to build.

Close by asking whether anything feels off (missed edge cases, wrong assumptions); this is the cheapest point to catch them.

## Status and lifecycle

Frontmatter `status:` moves through `Planning`, `Ready`, `In Progress`, `Complete`, or `Cancelled`. Keep the tracking issue in step when status changes. Issues close only when the implementation PR merges with `Closes #N`; do not close them by hand.
