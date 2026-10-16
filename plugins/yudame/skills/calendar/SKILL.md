---
name: calendar
description: "Read, create, update, or cancel Google Calendar events with the gws command-line tool. Use for 'what's on my calendar', 'am I free Thursday', 'book a meeting', or 'move that meeting'."
---

# Calendar

Goal: answer calendar questions and make calendar changes accurately, from the right account, without inviting or notifying anyone the user has not approved.

## The tool

**`gws calendar`** (Google's Workspace CLI, `npm install -g @googleworkspace/cli`). It needs a one-time human `gws auth login`, so an auth error means stop and tell the user to log in again, not retry.

**Whose calendar.** `gws` acts as the Google account it is logged in as, which may not be the person in the conversation. Before reading or changing anything, check which account that is; the `id` of the primary calendar is its address:

```bash
gws calendar calendarList get --params '{"calendarId": "primary"}'
```

Name that account when you report back. Someone else's calendar is reachable only if it is shared with this account: pass their address as `calendarId`.

## Reading

```bash
gws calendar +agenda --today            # also --tomorrow, --week, --days N; --format table
gws calendar events list --params '{"calendarId": "primary", "timeMin": "2026-10-20T00:00:00+07:00", "timeMax": "2026-10-21T00:00:00+07:00", "singleEvents": true, "orderBy": "startTime", "q": "standup"}'
gws calendar freebusy query --json '{"timeMin": "...", "timeMax": "...", "items": [{"id": "primary"}]}'
```

Times are RFC 3339 with an offset. `singleEvents: true` expands recurring events so each occurrence has its own id.

## Creating and changing

```bash
gws calendar +insert --summary 'Review' --start 2026-10-20T10:00:00+07:00 --end 2026-10-20T10:30:00+07:00 --attendee a@b.com --meet
gws calendar events patch  --params '{"calendarId": "primary", "eventId": "ID", "sendUpdates": "all"}' --json '{"start": {"dateTime": "..."}, "end": {"dateTime": "..."}}'
gws calendar events delete --params '{"calendarId": "primary", "eventId": "ID", "sendUpdates": "all"}'
```

- Find the event id with `events list` first. `patch` sends only the fields that change.
- `+insert` covers a simple timed event and sends no invitation emails. For an all-day or recurring event, or to email attendees, use `events insert --params '{"calendarId": "primary", "sendUpdates": "all"}' --json '{...}'`.
- `sendUpdates` decides who hears about it: `all` emails every attendee from the logged-in account, `none` (the default) emails no one, though the event still appears on their calendars.
- `--dry-run` on a `+` helper prints the request without sending it. `gws schema calendar.events.insert` (or any method) lists its parameters.

## Before you change anything

Show the user the event (title, time with timezone, attendees, whether they will be emailed) and wait for approval before creating, moving, or cancelling an event that has anyone else on it. An event only on the user's own calendar needs no confirmation when they asked for it directly.
