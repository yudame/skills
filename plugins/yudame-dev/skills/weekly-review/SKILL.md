---
name: weekly-review
description: "Summarize recent commits into a plain-text context handoff for another agent or person. Use for a weekly, sprint, or 'last N days' review."
allowed-tools: Bash, Read, Write
argument-hint: "[days]"
---

# Weekly Review

Turn a period of git history into a plain-text handoff: what changed, why, and what is still in flight, so another agent (or a person) can pick up the work with the right context and no repo archaeology. The reader is usually a fresh agent session, so precision beats polish. It is purely git- and gh-based and works in any repo.

`[days]` defaults to 7 (14 for bi-weekly, 30 for monthly).

## Gather

```bash
git fetch && git merge --ff-only @{upstream} 2>/dev/null; git branch --show-current
git log --since="<DAYS> days ago" --no-merges --format='%h %ad %an %s' --date=short
git log --since="<DAYS> days ago" --no-merges --stat | head -500
gh pr list --state all --search "updated:>=<YYYY-MM-DD>" --limit 50
```

The refresh uses fetch plus a fast-forward rather than `git pull` because `.git/FETCH_HEAD` is shared across worktrees and a concurrent fetch can retarget a bare pull. It may fail (no upstream, or diverged); the review is read-only either way. Say which branch the review covers.

## Write

Group the work by goal, letting the groups come from the actual commits, ordered by impact. For each group: what changed and why, in a sentence or two, with the anchors a reader needs to follow up (PR and issue numbers, the key files or modules, commit SHAs for anything notable). Then a section for what is unfinished: open PRs, half-landed work, reverts, known breakage, decisions still pending. End with the period, commit count, and who did the work.

Plain text, no markdown styling or emojis: it gets pasted into another agent's prompt. Keep the analysis out; the output is only the handoff.

## Save

Show it in the reply and save it as `/tmp/review_<repo>_<from>_<to>.txt` (dates as YYYY-MM-DD). When it goes to someone else, send the text itself, not the path.
