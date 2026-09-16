#!/usr/bin/env python3
"""Fail the build when a link to an APIMart page bypasses its attributed short link."""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_APIMART = re.compile(r"https://(?:[a-z0-9-]+\.)?apimart\.ai/[^\s)\]<>]*")
SHORT = re.compile(r"https://go\.apimart\.ai/k-[0-9a-f]+")
API_HOST = re.compile(r"https://api\.apimart\.ai/")
DOCS_HOST = re.compile(r"https://docs\.apimart\.ai/")

problems: list[str] = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.suffix not in {".md", ".py", ".sh", ".mjs", ".json"}:
        continue
    if path.name in {"check_links.py", "repo.json"} or ".git" in path.parts:
        continue
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if SHORT.search(line):
            continue
        for url in RAW_APIMART.findall(line):
            if API_HOST.match(url) or DOCS_HOST.match(url):
                continue          # API endpoint and documentation host are not attributed
            problems.append(f"{path.relative_to(ROOT)}:{lineno} unattributed apimart link -> {url}")

data = ROOT / "data/prompts.json"
if data.exists():
    items = json.loads(data.read_text())
    if not items:
        problems.append("data/prompts.json is empty")
    for item in items:
        if not item.get("prompt") or not item.get("model"):
            problems.append(f"incomplete prompt record: {item.get('slug')}")

if problems:
    print("\n".join(problems))
    sys.exit(1)
print("attribution and prompt data OK")
