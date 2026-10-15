---
name: audit-SUBJECT
description: "Audit SUBJECT for PROBLEMS. Use when reviewing SUBJECT health, after SUBJECT changes, or on 'check the SUBJECT', 'validate SUBJECT', 'what's wrong with SUBJECT'."
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---

# SUBJECT Audit

**Goal:** WHAT_GETS_AUDITED, WHY_IT_MATTERS, and what the user gets: a severity-grouped report of every SUBJECT item in TARGET_LOCATION. DISPOSITION: one of "report only, a human decides" | "auto-fixes trivial issues and reports the rest" | "applies corrections and leaves them for review".

SCOPE_NOTES: what to include, what to skip and why. If script-backed: `python scripts/audit.py $ARGUMENTS` (relative to this skill's directory) runs the deterministic checks; the checks below marked (judgment) are done by reading.

## Checks

**FAIL**
- `CHECK_NAME`: what it catches, why that matters, how to decide pass or fail.

**WARN**
- `CHECK_NAME`: ...

**INFO**
- `CHECK_NAME`: ...

## Report

```
## SUBJECT Audit Report

#### FAIL
- [check-name] RealisticItem: expected X, found Y
#### WARN
- [check-name] RealisticItem: expected X, found Y
#### INFO
- [check-name] RealisticItem: observation

Summary: PASS N | WARN N | FAIL N
```

## After the audit

DISPOSITION_DETAILS: what happens to the findings, who acts on them, and what, if anything, this skill changes itself.
