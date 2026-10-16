---
name: do-investigation-issue
description: "File a GitHub investigation issue for an unconfirmed finding or anomaly, as a hypothesis rather than a defect."
allowed-tools: Bash Read
argument-hint: "<component> — <brief finding>"
---

# Post Investigation Issue

Capture an unconfirmed finding as a GitHub issue that a future investigator can pick up and start on immediately. The issue doesn't claim a defect; it asks for root-cause analysis before anyone acts. Fits: an audit surfaced something suspicious, research (a post-mortem, a blog post, docs) describes a failure that may apply here, or a behavior happened once and was never diagnosed.

This is the counterpart to the do-issue skill, which files confirmed, planner-ready work. Here the bar is lower on purpose: if unsure, file. An unneeded investigation issue is cheap; a missed gap is not. Don't file when an open issue already tracks it (`gh issue list --search "<keywords>"`), when prior investigation ruled it out, or when it's an aspirational feature with no evidence of a current gap.

## Title and label

Title by kind of finding:
- `Reliability risk: {component} — {one-line description}` for reliability concerns
- `Integration failure: {component} — {description}` for observed (not hypothetical) integration outages
- `Gap: {component} — {description}` for missing capabilities surfaced by research or audits

The component is the system area affected. Label `investigation` only; `bug` or `feature` gets added later by whoever confirms it. Create the label if the repo lacks it (`gh label create investigation`).

## Body

Fill every section of `TEMPLATE.md`. Evidence goes in verbatim: error strings, log lines, quotes from sources, code references. If a section genuinely has nothing, write one sentence saying why ("None — proactive investigation, no remediation attempted yet."). Next steps should be concrete enough to start on: specific files or functions to inspect, experiments to run, behaviors to confirm or rule out.

Write the body to a unique temp file and publish from it. A fixed path like `/tmp/issue_body.md` has been clobbered by concurrent agents before, publishing the wrong body. Use a quoted heredoc so `${...}` and backticks in evidence stay literal.

```bash
DRAFT=$(mktemp "${TMPDIR:-/tmp}/investigation_body.XXXXXX")
cat > "$DRAFT" << 'BODY'
...filled-in TEMPLATE.md...
BODY
gh issue create --title "Reliability risk: <component> — <description>" --label investigation --body-file "$DRAFT"
rm -f "$DRAFT"
```

`gh` targets the current directory's repo; pass `--repo owner/name` otherwise. Report the issue number, title, and URL.
