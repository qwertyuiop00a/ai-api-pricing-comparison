#!/usr/bin/env python3
"""Refresh the AI API pricing snapshot and regenerate the README tables.

The APIMart pricing page ships its catalog inside the React Server Component payload, so the
whole model list (per-image prices by resolution, per-second video rates, per-million-token LLM
rates, plus effective prices after the default group discount) can be read without an API key.

Usage:
    python tools/snapshot.py                 # fetch live page, update data/pricing.json + README tables
    python tools/snapshot.py --from-file X   # parse a saved HTML page instead of fetching
    python tools/snapshot.py --check         # exit 1 when the snapshot changed (CI guard)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "pricing.json"
README = ROOT / "README.md"
PAGE = "https://apimart.ai/en/pricing"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")

# Curated rows: (model id, display name, why it is on the list)
IMAGE_PICKS = [
    ("gpt-image-2.5-ext", "image2.5 (GPT-Image-2.5 ext route)", "per-image relay route, the cheapest image2.5 entry"),
    ("gemini-3-pro-image-preview", "Nano Banana Pro", "highest-fidelity Gemini image route"),
    ("gemini-3.1-flash-image-preview", "Nano Banana 2", "fast Gemini image route"),
    ("gemini-2.5-flash-image-preview", "Nano Banana", "first-generation Gemini image route"),
    ("grok-imagine-1.5-apimart", "Grok Image 1.5", "text-to-image on the Grok Imagine route"),
    ("grok-imagine-1.5-edit-apimart", "Grok Image 1.5 (edit)", "image editing on the same route family"),
    ("grok-imagine-image", "Grok Imagine image", "alternative Grok image route"),
    ("seedream-4-0", "Seedance 4.0 image", "Seedream family image route"),
    ("seedream-4-5", "Seedance 4.5 image", "Seedream family image route"),
    ("gpt-image-2", "GPT-Image-2 (ext)", "previous-generation per-image route"),
]
VIDEO_PICKS = [
    ("seedance-2.5", "Seedance 2.5", "current Seedance video route"),
    ("seedance-2.0", "Seedance 2.0", "previous Seedance video route"),
    ("seedance-2.0-mini", "Seedance 2.0 mini", "budget video route"),
    ("seedance-2.0-fast", "Seedance 2.0 fast", "latency-optimised video route"),
    ("seedance-1-5-pro", "Seedance 1.5 Pro", "older Pro route kept for comparison"),
    ("seedance-1-0-pro-quality", "Seedance 1.0 Pro Quality", "legacy Pro route"),
    ("kling-3.0-turbo", "Kling 3.0 Turbo", "third-party video route"),
]
TOKEN_PICKS = [
    ("gpt-5.5", "GPT-5.5", "flagship reasoning/chat tier"),
    ("gpt-5.5-pro", "GPT-5.5 Pro", "highest-tier GPT-5.5"),
    ("gpt-5.4", "GPT-5.4", "previous flagship tier"),
    ("gpt-5.1", "GPT-5.1", "mid-tier GPT-5 line"),
    ("gpt-5-mini", "GPT-5 mini", "cheap GPT-5 tier"),
    ("gpt-5-nano", "GPT-5 nano", "cheapest GPT-5 tier"),
    ("claude-opus-5", "Claude Opus 5", "Anthropic flagship"),
    ("claude-opus-4-8", "Claude Opus 4.8", "previous Anthropic flagship"),
    ("claude-sonnet-4-6", "Claude Sonnet 4.6", "balanced Anthropic tier"),
    ("claude-haiku-4-5-20251001", "Claude Haiku 4.5", "cheap Anthropic tier"),
    ("deepseek-v4-pro", "DeepSeek V4 Pro", "DeepSeek flagship"),
    ("deepseek-v4-flash", "DeepSeek V4 Flash", "cheap DeepSeek tier"),
    ("deepseek-v3.2", "DeepSeek V3.2", "previous DeepSeek generation"),
]


def fetch(url: str = PAGE) -> str:
    cp = subprocess.run(["curl", "-sL", "-m", "45", "-H", f"User-Agent: {UA}", url],
                        capture_output=True, text=True)
    if not cp.stdout:
        raise SystemExit("failed to fetch the pricing page")
    return cp.stdout


def rsc_blob(html: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', html)
    return "".join(c.encode().decode("unicode_escape", errors="ignore") for c in chunks)


def balanced_objects(text: str) -> list[str]:
    out, i, n = [], 0, len(text)
    while True:
        i = text.find('{"id":"', i)
        if i < 0:
            return out
        depth, j = 0, i
        while j < n:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(text[i:j + 1])
        i = j + 1


def parse_models(blob: str) -> list[dict]:
    models = []
    for raw in balanced_objects(blob):
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        if not isinstance(rec, dict) or not rec.get("id"):
            continue
        spec = rec.get("specification")
        entry = {"id": rec["id"], "name": rec.get("name"), "alias": rec.get("alias"), "specification": spec}
        fixed = rec.get("fixed_prices") or {}
        pricing = rec.get("pricing") or {}
        if fixed.get("items"):
            entry["unit"] = fixed.get("unit")
            entry["prices"] = {i["key"]: {"list": i.get("original_price"), "effective": i.get("after_discount")}
                               for i in fixed["items"]}
        elif pricing.get("rates"):
            entry["unit"] = pricing.get("unit")
            entry["prices"] = {"list": pricing.get("rates"), "effective": pricing.get("effective_rates")}
            entry["billing_type"] = pricing.get("billing_type")
            entry["origin"] = pricing.get("origin")
        else:
            continue
        models.append(entry)
    return models


def money(v) -> str:
    if v in (None, ""):
        return "—"
    v = float(v)
    if v == 0:
        return "free"
    if v < 0.01:
        return f"${v:.6f}".rstrip("0").rstrip(".")
    if v < 1:
        return f"${v:.4f}".rstrip("0").rstrip(".")
    return f"${v:,.2f}"


def pick(prices: dict, key: str, variant: str = "flare"):
    """Resolve a price cell: variant@KEY (e.g. flare@1K) -> KEY -> default."""
    for candidate in (f"{variant}@{key}", key, "default"):
        if candidate in prices:
            return prices[candidate]
    return None


def image_table(models: dict) -> str:
    rows = ["| Route (model id) | 1K / default | 2K | 4K | Notes |", "| --- | --- | --- | --- | --- |"]
    for mid, label, note in IMAGE_PICKS:
        m = models.get(mid)
        if not m or "prices" not in m:
            continue
        p = m["prices"]
        cells = []
        for key in ("1K", "2K", "4K"):
            v = pick(p, key)
            cells.append(money(v.get("effective") if isinstance(v, dict) else v))
        rows.append(f"| `{mid}` — {label} | {cells[0]} | {cells[1]} | {cells[2]} | {note} |")
    return "\n".join(rows)


def video_table(models: dict) -> str:
    rows = ["| Route (model id) | 480p / second | 720p / second | 1080p / second | Notes |", "| --- | --- | --- | --- | --- |"]
    for mid, label, note in VIDEO_PICKS:
        m = models.get(mid)
        if not m or "prices" not in m:
            continue
        p = m["prices"]
        cells = []
        for key in ("480P", "720P", "1080P"):
            v = pick(p, key)
            cells.append(money(v.get("effective") if isinstance(v, dict) else v))
        rows.append(f"| `{mid}` — {label} | {cells[0]} | {cells[1]} | {cells[2]} | {note} |")
    return "\n".join(rows)


def token_table(models: dict) -> str:
    rows = ["| Model id | Input / 1M | Cached input / 1M | Output / 1M | Notes |", "| --- | --- | --- | --- | --- |"]
    for mid, label, note in TOKEN_PICKS:
        m = models.get(mid)
        if not m or "prices" not in m:
            continue
        p = m["prices"]
        eff = p.get("effective", p)
        rows.append(f"| `{mid}` — {label} | {money(eff.get('input'))} | {money(eff.get('cached_input'))} | "
                    f"{money(eff.get('output'))} | {note} |")
    return "\n".join(rows)


def replace_block(text: str, name: str, body: str) -> str:
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise SystemExit(f"marker block {name} not found in README")
    return pattern.sub(f"{start}\n{body}\n{end}", text)


def main() -> None:
    ap = argparse.ArgumentParser(description="Refresh the APIMart pricing snapshot")
    ap.add_argument("--from-file", help="parse a saved pricing page instead of fetching")
    ap.add_argument("--check", action="store_true", help="exit 1 if the snapshot changed")
    args = ap.parse_args()

    html = pathlib.Path(args.from_file).read_text(errors="ignore") if args.from_file else fetch()
    models_list = parse_models(rsc_blob(html))
    models = {m["id"]: m for m in models_list}
    snapshot = {
        "source": PAGE,
        "method": "React Server Component payload of the public pricing page (no API key required)",
        "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_count": len(models_list),
        "specification_counts": {s: sum(1 for m in models_list if m["specification"] == s)
                                 for s in sorted({m["specification"] for m in models_list})},
        "models": models_list,
    }
    new_json = json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"
    old_json = DATA.read_text() if DATA.exists() else ""
    changed = new_json != old_json
    if args.check:
        print("snapshot changed" if changed else "snapshot unchanged")
        sys.exit(1 if changed else 0)

    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(new_json)

    readme = README.read_text()
    readme = replace_block(readme, "pricing:image", image_table(models))
    readme = replace_block(readme, "pricing:video", video_table(models))
    readme = replace_block(readme, "pricing:token", token_table(models))
    readme = re.sub(r"<!-- snapshot:date -->[^<]*<!-- /snapshot:date -->",
                    f"<!-- snapshot:date -->{snapshot['extracted_at'][:10]}<!-- /snapshot:date -->", readme)
    README.write_text(readme)
    print(f"snapshot written: {len(models_list)} models ({snapshot['specification_counts']}), README tables refreshed")


if __name__ == "__main__":
    main()
