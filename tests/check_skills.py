"""Every skill loads in Claude Code, Codex and Pi: each SKILL.md has
Agent Skills frontmatter (https://agentskills.io/specification) whose
`name` is its directory and whose `description` is set, and no two skills
share a name, since Codex and Pi read them from one flat directory.

    python3 tests/check_skills.py [junit.xml]
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip().strip("\"'")
    return {}


def problems() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    seen: dict[str, Path] = {}
    for skill in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
        where = str(skill.parent.relative_to(ROOT))
        fields = frontmatter(skill.read_text())
        wrong = found.setdefault(where, [])
        if fields.get("name") != skill.parent.name:
            wrong.append(f"name {fields.get('name')!r} is not its directory {skill.parent.name!r}")
        if not 0 < len(fields.get("description", "")) <= 1024:
            wrong.append("description is missing or over 1024 characters")
        if skill.parent.name in seen:
            wrong.append(f"name also used by {seen[skill.parent.name].relative_to(ROOT)}")
        seen[skill.parent.name] = skill.parent
    return found


def main() -> int:
    found = problems()
    failed = {k: v for k, v in found.items() if v}
    for where, wrong in failed.items():
        for w in wrong:
            print(f"{where}: {w}")
    if len(sys.argv) > 1:
        cases = "".join(
            f'<testcase classname="skills" name="{escape(k)}">'
            + "".join(f'<failure message="{escape(w, {chr(34): "&quot;"})}"/>' for w in v)
            + "</testcase>"
            for k, v in found.items()
        )
        Path(sys.argv[1]).write_text(
            f'<testsuite name="skills" tests="{len(found)}" failures="{len(failed)}">{cases}</testsuite>'
        )
    print(f"{len(found)} skills, {len(failed)} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
