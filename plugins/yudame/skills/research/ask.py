#!/usr/bin/env python3
"""Ask one model one question through OpenRouter, with web search, and print the answer,
its sources and its cost. Optional: the research skill stands without it.

    ask.py MODEL "prompt" [--file PROMPT_FILE] [--no-web] [--json]
    ask.py --list [WORD]          models on OpenRouter whose id contains WORD

Needs OPENROUTER_API_KEY. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

API = "https://openrouter.ai/api/v1"


def request(model: str, prompt: str, web: bool = True) -> dict:
    """The chat request: web search through OpenRouter's web plugin, cost reported back."""
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "usage": {"include": True}}
    if web:
        body["plugins"] = [{"id": "web"}]
    return body


def read(response: dict) -> dict:
    """The answer, its cited URLs (each once, in order) and the cost in dollars."""
    message = response["choices"][0]["message"]
    sources, seen = [], set()
    for a in message.get("annotations") or []:
        cite = a.get("url_citation") or {}
        if cite.get("url") and cite["url"] not in seen:
            seen.add(cite["url"])
            sources.append({"url": cite["url"], "title": cite.get("title") or ""})
    for url in response.get("citations") or []:
        if url not in seen:
            seen.add(url)
            sources.append({"url": url, "title": ""})
    return {"model": response.get("model"), "answer": message.get("content") or "", "sources": sources, "cost": (response.get("usage") or {}).get("cost")}


def call(path: str, body: dict | None, key: str, opener=urllib.request.urlopen) -> dict:
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with opener(req, timeout=1800) as r:
        return json.load(r)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("model", nargs="?")
    p.add_argument("prompt", nargs="?", default="")
    p.add_argument("--file", help="read the prompt from a file")
    p.add_argument("--no-web", action="store_true", help="no web search (for cross-checking and writing)")
    p.add_argument("--json", action="store_true", help="print the result as JSON")
    p.add_argument("--list", nargs="?", const="", metavar="WORD")
    args = p.parse_args(argv)
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("OPENROUTER_API_KEY is not set", file=sys.stderr)
        return 2
    if args.list is not None:
        for m in call("/models", None, key)["data"]:
            if args.list.lower() in m["id"].lower():
                print(m["id"])
        return 0
    if not args.model:
        p.error("name a model, or --list")
    prompt = open(args.file).read() if args.file else args.prompt
    result = read(call("/chat/completions", request(args.model, prompt, web=not args.no_web), key))
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(result["answer"])
    if result["sources"]:
        print("\nSources:")
        for s in result["sources"]:
            print(f"- {s['title'] + ' ' if s['title'] else ''}{s['url']}")
    cost = result["cost"]
    print(f"\n[{result['model']}, cost {'$%.4f' % cost if cost is not None else 'not reported'}]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
