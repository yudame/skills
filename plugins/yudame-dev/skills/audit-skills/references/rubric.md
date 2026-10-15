# Architecture Rubric (the `--arch` pass)

The lint checks what code can verify. This rubric is the judgment layer: applied per skill by a model, against fixed criteria, with adversarial verification of every non-keep disposition. The grounding: skills hold information needed some of the time; subagents exist for two reasons only; primitives beat custom tooling.

## Running it

1. Run the lint first (`--json --no-sync`). Its findings are inputs, not conclusions.
2. For a fleet-wide pass, cluster skills by domain (about 7 skills or 3,500 lines per analyst) and run one analyst subagent per cluster in parallel. Give each analyst this rubric and its cluster's files and no seed conclusions, so dispositions come from the criteria rather than from the orchestrator's hunches.
3. Send every non-keep disposition to a fresh-context verifier prompted to refute it (prompt below). The analyst who proposed a merge never confirms it.
4. Synthesize one report with a row per skill. Check coverage: every skill audited has a row.

## The five lenses

**1. Context economy.** Descriptions ship in every session, bodies per invocation, sub-files on demand. Look for content in the wrong tier: always-true repo policy in a body (belongs in CLAUDE.md), rarely needed reference tables in a body (belongs in a sub-file), implementation detail in a description (belongs in the body).

**2. Primitive fit.** Is this the right shape?
- *Skill*: task guidance one context window applies end to end.
- *Workflow*: multi-stage work with independent stages, fan-out, or deterministic control flow. A workflow recommendation must name the stage boundaries and the handoff schema, because breakdown between orchestrator and stages is the usual way decomposition fails.
- *Subagent*: only for (a) parallelism or (b) fresh-mind isolation (the agent that wrote something should not review it). Name which. Everything else folds back into the main agent; current models handle far more context than the one-subagent-per-concern era assumed.
- *Script*: the body is mostly deterministic procedure. Extract it to code the skill invokes; a model should not do what code can verify.

**3. Consolidation.** Overlapping trigger surfaces, shared skeletons, thin wrappers. A merge recommendation names the surviving skill, includes the merged description text, and argues that trigger precision survives. A merged description that fires less reliably than the originals is a net loss even if it saves lines.

**4. Model tier.** Recommend by task property:
- **sonnet**: mechanical work, such as running scripts, formatting output, moving messages.
- **opus**: standard multi-step reasoning, such as building, test triage, docs, review legwork.
- **fable**: frontier judgment where a wrong call is expensive, such as plan critique, architecture decisions, adversarial verification, client-facing design.

Record it as a proposed `model:` frontmatter value; keep the tier-to-model mapping in one place so a model release updates one table.

**5. Efficiency.** Estimate tokens pulled in per invocation (body plus eagerly loaded sub-files; lines times about 10 is enough to rank). Flag bodies that tell the model to read every sub-file unconditionally, which defeats progressive disclosure, and descriptions over 200 chars doing documentation work.

## Dispositions

| Disposition | Criteria |
|---|---|
| **keep** | Right size, right primitive, distinct trigger surface |
| **merge → {survivor}** | Overlapping domain or trigger with a named sibling; merged description included |
| **split** | Two unrelated jobs sharing one trigger surface |
| **workflow** | Independent stages with structured handoffs beat one long context |
| **subagent** | Parallelism or fresh-mind isolation; cite which |
| **script** | Deterministic procedure written as prose |
| **retire** | Superseded, orphaned, or unused; check references and invocation history first |

## Findings schema (per skill)

```json
{
  "skill": "", "dir": "global|project|user|plugin", "lines": 0, "files": 0,
  "findings": ["..."],
  "disposition": {"action": "keep|merge|split|workflow|subagent|script|retire",
                   "target": "", "rationale": ""},
  "model": {"tier": "sonnet|opus|fable", "rationale": ""},
  "est_tokens": 0
}
```

## Verifier prompt (fresh context, one per non-keep disposition)

> A skills audit proposes: {disposition} for skill {name} ({rationale}). Read the skill and try to refute this. Grounds for refutation: (1) a merge would blunt trigger precision, because the originals fire on distinct phrasings a merged description cannot cover; (2) a subagent or workflow conversion cites neither parallelism nor fresh-mind isolation, or the stages share so much context that handoffs cost more than they isolate; (3) a retire target is actually load-bearing (check references and invocation history); (4) a script extraction would freeze judgment that genuinely varies per invocation. When uncertain, default to refuted. Return: {"refuted": bool, "grounds": "..."}.

Downgrade any disposition with a sustained refutation to **keep + note**.

## After the pass

Dispositions are recommendations; nothing is executed from the audit. Each accepted merge, split, or conversion becomes its own tracked change, including updating every cross-reference to the moved skill and cleaning up stale installed copies.
