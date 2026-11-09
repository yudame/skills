# Email: a long draft first, then editorial passes against the email guide

Tom, 2026-11-09: his guide "Writing Emails That Work" goes into the email skill as an editorial pass after a full draft, never as a recipe for writing an email in one go ("I would have written a shorter email, if I had more time"). At least one pass on every email, more when the stakes are high. An email drafted with only "Draft first" and de-slop ran long (2026-11-01).

## What is true today (checked)

- `plugins/yudame/skills/email/SKILL.md` says "Draft first", then de-slop before an external email leaves, with a skip for trivial logistics. No references directory. It does not cover chat.
- `de-slop` reads the draft cold and keeps facts and commitments verbatim, adding nothing. The guide needs the drafting context (who agreed a promise, where a fact came from) and deletes promises and adds answers, so it cannot live in de-slop: it is the author's rewrite before de-slop's cold copy edit. de-slop is unchanged.

## What will be built

1. `plugins/yudame/skills/email/references/writing-emails-that-work.md`: the guide byte for byte.
2. `email/SKILL.md`: a Drafting section before Sending: the full draft first, without the guide (the guide is never used to write it); then at least one pass rewriting the whole draft against the guide and its checklist, by the author with sources at hand, with no skip; at least two passes for a client, money, terms, a complaint or anything hard to take back; then de-slop as before, its trivial-logistics skip kept. The description names the order.
3. `tests/check_email.py` (stdlib): the guide's sha256, the link, the "never used to write the first draft" line, the order, two passes for high stakes, no skip in Drafting, de-slop's skip still under Sending. Fails on today's file. Added to the README's test line.

## Out of scope

Chat replies; de-slop; any new check or approval step.
