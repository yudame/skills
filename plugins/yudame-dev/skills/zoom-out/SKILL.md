---
name: zoom-out
description: "Step back mid-session, check the work against the real goal, and recommend the next focus. Use for 'zoom out' or 'am I on track'."
allowed-tools: Read Bash
---

# Zoom out

Pull back from the current task and reorient toward the actual goal. The usual triggers are a third fix attempt on the same issue that still fails, a session going in circles, work that has drifted from what was asked, or the user asking whether this is the right thing to be doing. It is for course correction, not routine check-ins, and not for stalling: if you already know the next step, take it.

## Gather context cheaply

Reconstruct where things stand from what already exists rather than re-reading everything:
- The conversation itself: the original request and what has been tried.
- `git log --oneline -10` and `git status` for what has actually changed.
- Any plan doc, progress file or issue the work is tracking.
- `gh issue list --state open --limit 10` when the repo uses GitHub issues, to see what else is in flight, blocked or long-open.
- Any memory or notes tool the session has, for corrections and patterns that apply here.

## The summary

Keep it short enough to read on a phone, under about 300 words:

- **What we set out to do:** the original goal.
- **What we've actually done:** the last few actions or commits.
- **Where we're stuck:** the current blocker, if any.
- **Recommended next focus:** the highest-leverage action. Without this the summary is only a status report.
- **What can wait:** two or three things to deprioritize.

End with one question: does this match the user's mental model, or is something missing?
