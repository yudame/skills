---
name: audit-models
description: "Audit a repo's data models (Popoto/Redis or other ORM) for relationship gaps, missing fields, and naming drift."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash
---

# Model Audit

Surface structural weaknesses in the data-model layer: relationship gaps, missing fields, naming drift, implicit coupling. The output is a findings report for the user and whoever owns the architecture. Do not change any model; which findings are real problems and which are deliberate is a human call.

## Scope and conventions

Models usually live in `models/*.py` (skip `__init__.py`); if not, find them by searching for the ORM's base class. Read every model and extract its class name, fields, field types, and key kinds (for Popoto: `KeyField`, `Field`, `SortedField` and so on; adapt to whatever ORM the repo uses). Build a cross-model field matrix and run the checks against it.

Before judging, look for the repo's own model conventions in AGENTS.md or CLAUDE.md, a models README, or the docs: which fields are universal, which models are exempt, which field names are deprecated. Declared conventions override the defaults below.

## Checks

1. **Missing universal fields.** Fields every model should carry, unless exempt. With no declared list, treat a field present on about 75% or more of models as a candidate and flag the models missing it for discussion, not as failures.
2. **Orphan models.** No field referencing another model's key, and no other model referencing its key.
3. **Naming drift.** The same concept under different names across models (`session_id` vs `agent_session_id`), deprecated terms the repo has declared, and bare names like `id` that are ambiguous outside their model.
4. **Implicit proxy relationships.** Two models share a key field (both have `chat_id`) but one carries a field the other lacks (`project_key`), which suggests the second uses the shared key as a stand-in for the missing field.
5. **Cardinality.** For each related pair, state the expected cardinality (1:1, 1:N, N:M) and flag pairs where it is unclear or undocumented.
6. **Key type consistency.** A field name shared across models should have the same type and key kind everywhere (`chat_id` should not be a `KeyField` in one model and a plain `Field` in another).

## Report

Group findings by severity: **CRITICAL** for orphan models and universal fields missing from core models; **WARNING** for naming drift, implicit proxies, and type inconsistencies; **INFO** for cardinality gaps.

```
## Model Audit Report

### Models Scanned
- ModelName (N fields, keys: [list])

### Findings

#### CRITICAL
- [missing-universal] TelegramMessage: missing `project_key`
- [orphan] DeadLetter: no references to or from other models

#### WARNING
- [naming-drift] AgentSession.agent_session_id vs convention: should be `id`
- [implicit-proxy] Link uses `chat_id` as proxy for missing `project_key`

#### INFO
- [cardinality] AgentSession -> BridgeEvent: expected 1:N, no reference exists
```

End by suggesting next steps without taking them: an issue for the actionable findings, and a written exemption in the repo's conventions for any finding that is deliberate, so the next audit does not raise it again.
