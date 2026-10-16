---
name: officecli
description: "Create, read, and edit Word, Excel, and PowerPoint files (.docx, .xlsx, .pptx) with the officecli command-line tool. Use for 'make a deck', 'fill in this spreadsheet', 'edit the Word doc', or any task that reads or writes an Office file."
---

# officecli

Goal: build or change an Office file from the shell without guessing at its format, and hand over a file that opens cleanly.

`officecli` is a single binary for .docx, .xlsx and .pptx; no Office install is needed. If `officecli --version` fails, tell the user it is not installed (installer: `curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash`) rather than falling back to another library.

## Before you start

- **Look up, don't guess.** `officecli help docx paragraph` (or `xlsx`, `pptx`, and any element) lists every property, its format and an example; `officecli help docx set` lists what `set` can change. One lookup beats a guess-fail-retry loop.
- **Load the format guide** for anything you will hand over: `officecli load_skill` lists the tool's own guides (`word`, `excel`, `pptx`, `pitch-deck`, `financial-model`, `morph-ppt`, …). Load the one most specific to the artifact, once, and follow its rules. These carry the layout and design rules this skill leaves out.
- Prefer the highest layer that can do the job: read (`view`, `get`, `query`), then edit (`add`, `set`, `remove`, `move`, `batch`), and raw XML (`raw`, `raw-set`) only when nothing else can express it. Add `--json` for structured output.

## Quick start

```bash
officecli create report.docx
officecli add report.docx /body --type paragraph --prop text="Summary" --prop style=Heading1

officecli create data.xlsx
officecli set data.xlsx /Sheet1/A1 --prop value=Name --prop bold=true

officecli create deck.pptx
officecli add deck.pptx / --type slide --prop title="Q4 Report"
officecli add deck.pptx '/slide[1]' --type shape --prop text="Revenue grew 25%" --prop x=2cm --prop y=5cm --prop size=24
```

## Reading

```bash
officecli view deck.pptx outline        # also: text, stats, issues, annotated, html, screenshot, pdf
officecli get report.docx '/body/p[1]' --json
officecli query report.docx paragraph   # CSS-like selectors
```

## Many edits at once

`batch` applies a JSON array in one open/save cycle; it continues past a failed item unless given `--stop-on-error`.

```bash
echo '[{"command":"set","path":"/Sheet1/A2","props":{"value":"Alice"}},
       {"command":"set","path":"/Sheet1/B1","props":{"value":"Score"}}]' | officecli batch data.xlsx
```

`officecli import data.xlsx /Sheet1 rows.csv` loads a CSV; `officecli merge template.docx out.docx --data data.json` fills `{{key}}` placeholders.

## Finishing

- officecli keeps each file open in memory between commands. Its own reads see every edit, but another program sees the file on disk only after `officecli save <file>` or `officecli close <file>`. Close each file before handing it over.
- Run `officecli validate <file>` and `officecli view <file> issues` after editing. Exit code 0 means done, 1 failed, 2 ran with warnings (read them).

## Pitfalls

- Quote paths with brackets: `'/slide[1]'`, or the shell expands them.
- Every attribute goes through `--prop key=value`, never its own flag.
- Single-quote text containing `$`: `--prop text='$15M'`.
- Paths are 1-based (`/body/p[3]` is the third paragraph); `--index` is 0-based, except Excel row and column inserts.
- Close the file in Word or PowerPoint before editing it.
