"""present/tts.py says each LEXICON word as listed and leaves the rest to the
engine: `splice` is run with a stand-in phonemizer that upper-cases and strips
its input, as kokoro's strips, so no model is needed.

    python3 tests/check_tts.py
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("tts", ROOT / "plugins/yudame/skills/present/tts.py")
tts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tts)

E, Y = tts.LEXICON["engels"], tts.LEXICON["yudame"]
L = tts.LEXICON
RO, R_O, RW, RA = L["read-only"], L["read only"], L["read-write"], L["read access"]
CASES = {
    "I'm Valor Engels": f"I'M VALOR {E}",
    "valor engels": f"VALOR {E}",
    "VALOR ENGELS": f"VALOR {E}",
    "I'm Valor Engels, at Yudame.": f"I'M VALOR {E}, AT {Y}.",
    "Work at yudame and YUDAME": f"WORK AT {Y} AND {Y}",
    "See valorengels.com now": f"SEE VALOR {E} DOT COM NOW",
    "yudame.com": f"{Y} DOT COM",
    "Mail valor@yuda.me today": f"MAIL VALOR@ {Y} TODAY",
    "Watch cap.yuda.me.": f"WATCH CAP DOT {Y}.",
    "Yudame's clients": f"{Y}z CLIENTS",
    "Engels's books": f"{E}ᵻz BOOKS",
    "Engels. Then": f"{E}. THEN",
    "It is read-only.": f"IT IS {RO}.",
    "The disk was read-only, so": f"THE DISK WAS {RO}, SO",
    "A read-only copy": f"A {RO} COPY",
    "Read-Only mode": f"{RO} MODE",
    "The file is read only.": f"THE FILE IS {R_O}.",
    "They were read only": f"THEY WERE {R_O}",
    "It's read only now": f"IT'S {R_O} NOW",
    "Engels made it read-only": f"{E} MADE IT {RO}",
    "I read only the summary.": None,
    "She read only two chapters.": None,
    "spread only": None,
    "bread-only": None,
    "I read it yesterday.": None,
    "You get read access.": f"YOU GET {RA}.",
    "Read  access": RA,
    "It is read-write for admins": f"IT IS {RW} FOR ADMINS",
    "a read-heavy load": f"A {L['read-heavy']} LOAD",
    "read permissions and read permission": f"{L['read permissions']} AND {L['read permission']}",
    "unread accessories": None,
    "Can you read it?": None,
    "Hello world.": None,
    "example.com": None,
}


def main() -> int:
    failed = 0
    for text, want in CASES.items():
        got = tts.splice(text, lambda t: t.strip().upper())
        if got != want:
            failed += 1
            print(f"FAIL {text!r}: got {got!r}, want {want!r}")
    print(f"{len(CASES)} cases, {failed} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
