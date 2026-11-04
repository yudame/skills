"""The present skill's deck and carousel rules hold together: each @page size
it gives prints to the pdfinfo points it says to check for (Chrome prints CSS
px at 96 per inch), and every type rule for decks and carousels is a range
with a ceiling, never a bare floor ("at least 18pt").

    python3 tests/check_present.py [path/to/SKILL.md]
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "plugins/yudame/skills/present/SKILL.md"
PT = {"mm": 72 / 25.4, "px": 72 / 96, "in": 72.0, "pt": 1.0}


def rule(text: str, label: str) -> str:
    m = re.search(rf"^- \*\*{label}\*\*.*$", text, re.M)
    return m.group(0) if m else ""


def points(size: str) -> tuple[float, float]:
    (w, wu), (h, hu) = re.findall(r"([\d.]+)(mm|px|in|pt)", size)
    return float(w) * PT[wu], float(h) * PT[hu]


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    check = re.search(r"`pdfinfo out\.pdf`[^\n]*", text)
    check = check.group(0) if check else ""
    wrong = []
    for label, name in (("Deck", "a deck"), ("Mobile carousel", "a carousel")):
        body = rule(text, label)
        if not body:
            wrong.append(f"no '- **{label}**' rule in the PDF section")
            continue
        size = re.search(r"@page \{ size: ([^;]+);", body)
        stated = re.search(rf"([\d.]+) x ([\d.]+) for {name}\b", check)
        if not size or not stated:
            wrong.append(f"{label}: @page size or the pdfinfo size for {name} is missing")
        else:
            got, want = points(size.group(1)), (float(stated.group(1)), float(stated.group(2)))
            if any(abs(g - w) > 1 for g, w in zip(got, want)):
                wrong.append(f"{label}: {size.group(1)} prints {got[0]:.1f} x {got[1]:.1f} pt, pdfinfo check says {want[0]} x {want[1]}")
        if re.search(r"at least \d+ ?(pt|px)", body):
            wrong.append(f"{label}: a type rule is a bare floor ('at least'); give a range with a ceiling")
        if not re.search(r"\d+ to \d+ ?(pt|px)", body):
            wrong.append(f"{label}: no type range (N to M pt/px)")
    for w in wrong:
        print(w)
    print(f"2 rules, {len(wrong)} failing")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
