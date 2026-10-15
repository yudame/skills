---
name: email
description: "Read, search, draft, or send the user's email, drafts first and de-slopped. Use for 'check my inbox', 'reply to that', or 'send an email'."
allowed-tools: Bash
user-invocable: true
---

# Email

Goal: get the mail task done with the lightest tool that can reach the mailbox, and never let a message leave that the user has not approved or that reads like machine filler.

## Picking a tool

Use the first of these that is present and authenticated. A tool that is installed but fails auth counts as absent: move on rather than stall on it.

1. **A repo-provided mail CLI**, if the current repo's CLAUDE.md documents one.
2. **`gws gmail`** (Google's Workspace CLI, `npm install -g @googleworkspace/cli`). It needs a one-time human `gws auth setup` / `gws auth login`, so an auth error means fall through, not retry.
   ```bash
   gws gmail users messages list --params '{"userId": "me", "q": "from:a@b.com is:unread", "maxResults": 5}'
   gws gmail users messages get  --params '{"userId": "me", "id": "MSG_ID"}'
   ```
3. **The Gmail connector** (`mcp__claude_ai_Gmail__*`: `search_threads`, `get_thread`, `create_draft`, `reply`), available in interactive sessions. On most desktop setups this is the working path.
4. **Browser automation on the webmail UI**, only when nothing above can reach the mailbox at all. It is slow and fragile; if you catch yourself opening a browser for an ordinary read or send, go back up the list.

## Sending

- Draft first. "Write a reply" means a draft the user reviews; send only when told to send.
- Before any email to an external recipient leaves (a send, or a draft the user will send as-is), run `/yudame:de-slop` on the draft text alone in a fresh context, not on the drafting conversation, so the review sees only what the recipient will see. On BLOCK, revise per its diagnosis and rerun; after two BLOCKs, show the user the draft and the diagnosis instead of sending. Trivial logistics ("confirmed, see you at 3") can skip the gate.
