#!/usr/bin/env python3
"""Fail the build when a link to an APIMart page bypasses its attributed short link."""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED_RAW = re.compile(r"https://(docs\.apimart\.ai|apimart\.ai)/[^)\s]*")
SHORT = re.compile(r"https://go\.apimart\.ai/k-[0-9a-f]+")
SKIP_FILES = {"tools/check_links.py", ".github/workflows/validate.yml"}

problems: list[str] = []
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or path.suffix not in {".md", ".py", ".sh", ".mjs", ".json"}:
        continue
    if path.name in SKIP_FILES or ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for target in ALLOWED_RAW.findall(text):
        for match in re.finditer(re.escape(target), text):
            line_start = text.rfind("\n", 0, match.start()) + 1
            line = text[line_start:text.find("\n", match.start())]
            if SHORT.search(line) or "docs.apimart.ai" in line or "api.apimart.ai" in line:
                continue
            problems.append(f"{path.relative_to(ROOT)}: unattributed apimart link -> {target}")

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
