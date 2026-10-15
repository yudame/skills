---
name: ontologies
description: "Build or update a project's domain vocabulary in ONTOLOGIES.md. Use for 'name things', 'what do we call X', or competing terms."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Ontologies

Maintain `ONTOLOGIES.md` at the repo root (next to CLAUDE.md): the canonical vocabulary of the domain, so people and agents use one name per concept, know what each name does not mean, and notice when a single name is covering two concepts.

Reach for it when a new concept has arrived under several names, when a review or plan turns on what "X" means versus "Y", before naming a new module, class or API field, or when the user asks.

## Doing it

**Read before asking.** Read the existing `ONTOLOGIES.md`, any decision records (`docs/adr/` or similar) that defined terms, and grep the code and docs for how the term is actually used. Don't ask the user anything the repo already answers. If no term was named, ask which one to work on.

**Pin the definition down by interview,** one question at a time, revising a working definition after each answer and stopping once it holds still. The questions that do the most work: what the concept is in the domain (not in code), a real example of it, what it is not and what a confused person would mistake it for, and whether it means different things in different parts of the system.

**Treat a split meaning as a boundary.** When one term means two things in two modules, that is a bounded-context boundary; record both meanings and say they must not be merged:

```
Note: "Order" in checkout/ means a customer's cart at purchase time.
      "Order" in fulfillment/ means a warehouse shipping instruction.
      These are distinct concepts and should not be merged.
```

**Write the entry.** Group terms under domain areas. Definitions are one precise sentence in plain language, describing domain concepts rather than code identifiers or schema columns (this is not a data dictionary). For any term that gets confused with another, the "Contrast with" line is the most valuable part of the entry, so fill it in.

```markdown
# Ontologies — <Repo Name>

> Canonical domain vocabulary for this repo. Terms are domain concepts, not code identifiers.

## <Domain Area>

### <Term>
**Definition:** One precise sentence.
**Usage example:** "When a user cancels an Order, the…"
**Contrast with:** terms this is commonly confused with
```

**Decide whether it needs a decision record.** A naming decision that changes a public API or message format, or renames a concept that appears across many files (roughly more than ten), deserves an ADR alongside the glossary entry, in the repo's existing ADR location. A new internal concept with no external surface doesn't.

Commit the change with a message like `docs(ontologies): add <term> to domain vocabulary`, staging only the files you changed.
