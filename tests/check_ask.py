"""research/ask.py sends one OpenRouter chat request with the web plugin and cost
reporting, and reads back the answer, each cited URL once, and the cost. A stand-in
opener plays OpenRouter, so no network or key is needed.

    python3 tests/check_ask.py
"""

import importlib.util
import io
import json
import os
import sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("ask", ROOT / "plugins/yudame/skills/research/ask.py")
ask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ask)

RESPONSE = {
    "model": "perplexity/sonar-pro",
    "choices": [{"message": {"content": "The answer.", "annotations": [
        {"type": "url_citation", "url_citation": {"url": "https://a.example", "title": "A"}},
        {"type": "url_citation", "url_citation": {"url": "https://a.example", "title": "A"}},
    ]}}],
    "citations": ["https://a.example", "https://b.example"],
    "usage": {"cost": 0.0123},
}


class Reply(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def main() -> int:
    failed = []

    def check(name, ok):
        if not ok:
            failed.append(name)
            print(f"FAIL {name}")

    body = ask.request("m", "q")
    check("web plugin on by default", body["plugins"] == [{"id": "web"}])
    check("cost requested", body["usage"] == {"include": True})
    check("no web when asked", "plugins" not in ask.request("m", "q", web=False))
    got = ask.read(RESPONSE)
    check("answer read", got["answer"] == "The answer.")
    check("each source once, in order", [s["url"] for s in got["sources"]] == ["https://a.example", "https://b.example"])
    check("cost read", got["cost"] == 0.0123)
    check("missing cost is None", ask.read({"choices": [{"message": {"content": "x"}}]})["cost"] is None)

    sent = []

    def opener(req, timeout):
        sent.append((req.full_url, json.loads(req.data), req.get_header("Authorization")))
        return Reply(json.dumps(RESPONSE).encode())

    out = ask.call("/chat/completions", ask.request("m", "q"), "KEY", opener=opener)
    check("posts to OpenRouter with the key", sent[0][0] == "https://openrouter.ai/api/v1/chat/completions" and sent[0][2] == "Bearer KEY")
    check("returns the response", out == RESPONSE)

    os.environ.pop("OPENROUTER_API_KEY", None)
    err = io.StringIO()
    with redirect_stderr(err), redirect_stdout(io.StringIO()):
        code = ask.main(["m", "q"])
    check("no key: exit 2 with the reason", code == 2 and "OPENROUTER_API_KEY" in err.getvalue())

    agent = (ROOT / "plugins/yudame/agents/researcher.md").read_text()
    head = agent.split("---")[1]
    check("researcher preloads the research skill", "\nskills: research\n" in head)
    check("researcher can find ask.py", "*/skills/research/ask.py" in agent)

    print(f"12 checks, {len(failed)} failing")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
