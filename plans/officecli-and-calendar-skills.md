# Plan: officecli and calendar skills in the yudame plugin

## What gets built

Two new skills, each one short `SKILL.md` (roughly 40 to 70 lines), in Agent Skills
format, worded in plain words so Claude Code, Codex and Pi all read them the same way.

### 1. `plugins/yudame/skills/officecli/SKILL.md`

Create, read and edit .docx, .xlsx and .pptx with the `officecli` binary on the machine.

Source: the old Valor skill. The ref named in the brief
(`backup/pre-sync-main-2026-10-15`) no longer exists on `tomcounsell/ai`; the same file
lives at commit `815e04d4ca7ae1ba71fd2419826f9533fb8a6640` (the parent of `e9562b2`,
"Archive .claude/ ahead of the bulk move"). That directory holds only `SKILL.md`, no
siblings.

Checked against the installed binary (`officecli --version` = 1.0.157, `officecli --help`):
- `help`, `dump`, `load_skill` exist now, so the old skill's version-check section
  (pinned v1.0.29 lacking them, the fleet `/update` pin, the curl installer) is dropped:
  it describes a fleet this repo does not have.
- `officecli load_skill` lists the tool's own bundled guides (pptx, word, excel, morph-ppt,
  …). The skill points there for format-specific design rules instead of copying them,
  which is what keeps it short.

Keeps from the old skill: the read → edit → raw XML order; `--json`; `help <format>
<element>` instead of guessing property names; one quick-start line set per format;
`view`, `get`, `query`, `set`, `add`, `remove`, `batch`, `raw`/`raw-set`; resident mode
and the flush rule (run `close` before another program reads the file); `validate` and
`view issues` after edits; the pitfalls (quote `[N]` paths, `--prop` for every attribute,
single quotes around `$`, 1-based paths vs 0-based `--index`); exit codes 0/1/2.

Drops: the "Specialized Skills" table (replaced by one line pointing at `load_skill`),
MCP mention, `argument-hint`, and anything naming Claude tools.

Frontmatter: `name: officecli`, a `description` with triggers (Word, Excel, PowerPoint,
.docx/.xlsx/.pptx, deck, spreadsheet), no `allowed-tools`.

### 2. `plugins/yudame/skills/calendar/SKILL.md`

Read, create and update Google Calendar events with `gws calendar`, written the way the
email skill documents `gws` (what it is, install line, one-time human `gws auth login`,
an auth error means stop and say so, short command blocks).

Content:
- **Whose calendar.** `gws` acts as the Google account it is logged in as, not as the
  user in the conversation. Check which account that is before acting
  (`gws calendar calendarList get --params '{"calendarId": "primary"}'`, whose `id` is the
  address), and say it when reporting. Another person's calendar is reachable only if it
  is shared with that account; pass its address as `calendarId`.
- **Read.** `gws calendar +agenda --today|--tomorrow|--week|--days N`;
  `gws calendar events list` with `timeMin`, `timeMax`, `singleEvents: true`,
  `orderBy: startTime`, `q`; `events get` by id. Free/busy via `freebusy query`.
- **Create.** `gws calendar +insert --summary --start --end [--attendee] [--meet]`, times in
  RFC 3339 with an offset; `events insert --json` for anything the helper lacks
  (all-day, recurrence).
- **Update.** `events patch` with only the changed fields; `events delete`. Find the event
  id with `events list` first.
- **Others are notified.** An event with attendees sends invitations from the logged-in
  account. Draft the event and confirm with the user before creating, moving or
  cancelling one that has other people on it; `sendUpdates` (`all` / `none`) decides
  whether they hear about a change. `--dry-run` shows the request without sending.
- `gws schema calendar.events.<method>` for any other parameter.

Frontmatter: `name: calendar`, a description with triggers ("what's on my calendar",
"book", "move that meeting"), no `allowed-tools`.

### 3. `README.md`

Add both skills to the `yudame` list, and note in the table that `officecli` and
`calendar` need their command-line tools installed.

## Out of scope

- Changing the email skill (it still carries `allowed-tools: Bash` and a Claude connector
  name; noted for the delivery, not fixed here).
- Installing or upgrading `officecli` or `gws`, or any skill for Drive, Docs or Sheets.
- Copying officecli's bundled format guides into this repo.

## Tests

- `python3 tests/check_skills.py` passes, now counting both new skills (names match
  directories, descriptions set and under 1024 characters, no duplicate names).
- Every command in both skills run against the real binaries before commit:
  - officecli: in a temp directory, `create` a .docx, .xlsx and .pptx; each quick-start
    `add`/`set`; `view <file> outline`, `get --json`, `query`, `batch` from stdin,
    `validate`, `close`; `help docx paragraph`; `load_skill` lists guides. Exit codes read.
  - gws: `+agenda --today`, `events list` with the documented params, `calendarList get
    primary` returning the account address, and `+insert`, `events patch`,
    `events delete` with `--dry-run` only, so no event is created and no one is invited.
- A grep over both files for Claude tool names (`Bash`, `Read`, `Write`, `Edit`,
  `mcp__`, `Skill`, `allowed-tools`) returns nothing.

## Rounds

Critique 0: two documentation files in a reversible repo. Review 1: the calendar skill
tells an agent when invitations leave under someone's name, which is worth one look.
