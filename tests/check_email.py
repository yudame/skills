"""The email skill writes the full draft first, then edits it against Tom's
guide (Tom, 2026-11-09): the guide is copied verbatim, SKILL.md links it,
says it is never used to write the first draft, orders draft, editorial pass,
de-slop, gives high stakes at least two passes, and lets no email skip the
guide pass (de-slop's own skip for trivial logistics stays under Sending).

    python3 tests/check_email.py [path/to/SKILL.md]
"""

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "plugins/yudame/skills/email/SKILL.md"
GUIDE = SKILL.parent / "references/writing-emails-that-work.md"
SHA256 = "be4f4822ca384f8466de77fbab622a5049b249dc23ab2cf8d7d06348466343b9"


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    wrong = []
    if not GUIDE.is_file() or hashlib.sha256(GUIDE.read_bytes()).hexdigest() != SHA256:
        wrong.append(f"{GUIDE.name} is missing or not the guide verbatim")
    if "(references/writing-emails-that-work.md)" not in text:
        wrong.append("SKILL.md does not link the guide")
    if "## Drafting" not in text or "## Sending" not in text:
        wrong.append("no Drafting section before Sending")
        drafting = ""
    else:
        drafting = text.split("## Drafting", 1)[1].split("## Sending", 1)[0]
    if "The guide is never used to write the first draft." not in " ".join(drafting.split()):
        wrong.append("SKILL.md does not say the guide is never used for the first draft")
    order = ["Write the full draft first", "edit it against the guide, at least once", "Then de-slop it"]
    at = [drafting.find(step) for step in order]
    if -1 in at or at != sorted(at):
        wrong.append(f"Drafting does not order {order}")
    if "Every email gets at least one pass" not in drafting:
        wrong.append("Drafting does not say every email gets a pass")
    if "without trying to follow the guide" not in " ".join(drafting.split()):
        wrong.append("the full draft is not written without the guide")
    stakes = "An email to a client, about money or terms, answering a complaint, or anything hard to take back gets at least two passes"
    if stakes not in " ".join(drafting.split()):
        wrong.append("Drafting does not give high stakes at least two passes")
    for exemption in ("skip", "exempt", "trivial", "unless", "except", "optional", "only when"):
        if exemption in drafting.lower():
            wrong.append(f"Drafting has exemption wording: {exemption!r}")
    if "Trivial logistics" not in text.split("## Sending", 1)[-1]:
        wrong.append("de-slop's trivial-logistics skip left Sending")
    for line in wrong:
        print(f"FAIL {line}")
    print("ok" if not wrong else f"{len(wrong)} failed")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
