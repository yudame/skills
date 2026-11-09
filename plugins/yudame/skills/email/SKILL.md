---
name: email
description: "Read, search, draft, or send the user's email: drafted in full, edited against the email guide, then de-slopped. Use for 'check my inbox', 'reply to that', or 'send an email'."
allowed-tools: Bash
user-invocable: true
---

# Email

Goal: get the mail task done with the lightest tool that can reach the mailbox, and never let a message leave that the user has not approved or that reads like machine filler.

## Picking a tool

Use the first of these that is present and authenticated. A tool that is installed but fails auth counts as absent: move on rather than stall on it.

1. **A repo-provided mail CLI**, if the current repo's AGENTS.md or CLAUDE.md documents one.
2. **`gws gmail`** (Google's Workspace CLI, `npm install -g @googleworkspace/cli`). It needs a one-time human sign-in (this repo's README, "Google sign-in for `gws`"), so an auth error means fall through, not retry.
   ```bash
   gws gmail users messages list --params '{"userId": "me", "q": "from:a@b.com is:unread", "maxResults": 5}'
   gws gmail users messages get  --params '{"userId": "me", "id": "MSG_ID"}'
   ```
3. **The Gmail connector** (`mcp__claude_ai_Gmail__*`: `search_threads`, `get_thread`, `create_draft`, `reply`), available in interactive sessions. On most desktop setups this is the working path.
4. **Browser automation on the webmail UI**, only when nothing above can reach the mailbox at all. It is slow and fragile; for an ordinary read or send, go back up the list.

## Drafting

Tom's guide, [references/writing-emails-that-work.md](references/writing-emails-that-work.md), is for editing an email, not for writing one. Trying to write a short, rule-following email in one go from the raw context and goal works badly: "I would have written a shorter email, if I had more time." Take the time, in this order:

1. **Write the full draft first.** Write it from the context and the goal, as long as it needs to be to say everything, without trying to follow the guide. The guide is never used to write the first draft.
2. **Then edit it against the guide, at least once.** Read the guide, rewrite the whole draft against its six rules, then go through its checklist line by line. Do this yourself, with the sources at hand: the pass needs to know who agreed each promise and where each fact came from. Every email gets at least one pass, a one-line reply included.
3. **More passes when the stakes are high.** An email to a client, about money or terms, answering a complaint, or anything hard to take back gets at least two passes, each one rewriting the last pass's result.
4. **Then de-slop it,** as under Sending below.

## Sending

- Draft first. "Write a reply" means a draft the user reviews; send only when told to send.
- Before any email to an external recipient leaves (a send, or a draft the user will send as-is), run the de-slop skill on the draft text alone in a fresh context (without subagents, re-read only the draft), so the review sees only what the recipient will see. On BLOCK, revise per its diagnosis and rerun; after two BLOCKs, show the user the draft and the diagnosis instead of sending. Trivial logistics ("confirmed, see you at 3") can skip the gate.
