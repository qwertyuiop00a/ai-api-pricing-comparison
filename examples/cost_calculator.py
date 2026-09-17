#!/usr/bin/env python3
"""Estimate an AI workload's cost from data/pricing.json (no network, no API key).

Examples
--------
    python examples/cost_calculator.py image --model gpt-image-2.5-ext --resolution 1K --count 1000
    python examples/cost_calculator.py video --model seedance-2.0-mini --resolution 480P --seconds 10 --count 50
    python examples/cost_calculator.py tokens --model gpt-5.5 --input-tokens 250000 --output-tokens 40000
    python examples/cost_calculator.py list --spec image
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "pricing.json"


def load() -> dict[str, dict]:
    payload = json.loads(DATA.read_text())
    return {m["id"]: m for m in payload["models"]}


def price_of(model: dict, key: str | None, variant: str = "flare") -> float:
    """Resolve a price: variant@KEY (e.g. flare@1K) -> KEY -> default."""
    prices = model.get("prices") or {}
    entry = None
    for candidate in ([f"{variant}@{key}", key] if key else []) + ["flare@default", "default"]:
        if candidate in prices:
            entry = prices[candidate]
            break
    if entry is None:
        raise SystemExit(f"no price for key {key!r} (variant {variant}) on {model['id']}; available: {sorted(prices)}")
    if isinstance(entry, dict):
        entry = entry.get("effective", entry.get("list"))
    return float(entry)


def main() -> None:
    ap = argparse.ArgumentParser(description="Estimate AI API cost from the local pricing snapshot")
    sub = ap.add_subparsers(dest="mode", required=True)

    p_img = sub.add_parser("image", help="per-image routes")
    p_img.add_argument("--model", required=True)
    p_img.add_argument("--resolution", default="1K")
    p_img.add_argument("--variant", default="flare", help="variant selector used by some routes, e.g. flare | sunburst")
    p_img.add_argument("--count", type=int, default=1)

    p_vid = sub.add_parser("video", help="per-second routes")
    p_vid.add_argument("--model", required=True)
    p_vid.add_argument("--resolution", default="720P")
    p_vid.add_argument("--variant", default="flare")
    p_vid.add_argument("--seconds", type=float, default=5)
    p_vid.add_argument("--count", type=int, default=1)

    p_tok = sub.add_parser("tokens", help="per-million-token routes")
    p_tok.add_argument("--model", required=True)
    p_tok.add_argument("--input-tokens", type=int, required=True)
    p_tok.add_argument("--output-tokens", type=int, required=True)

    p_list = sub.add_parser("list", help="list models in the snapshot")
    p_list.add_argument("--spec", default=None)
    p_list.add_argument("--grep", default=None)

    args = ap.parse_args()
    models = load()

    if args.mode == "list":
        for mid, m in sorted(models.items()):
            if args.spec and m.get("specification") != args.spec:
                continue
            if args.grep and args.grep.lower() not in mid.lower():
                continue
            print(f"{mid:44} {m.get('specification'):8} {m.get('unit')}")
        return

    if args.model not in models:
        raise SystemExit(f"unknown model id {args.model!r}; try: python examples/cost_calculator.py list --grep {args.model.split('-')[0]}")
    model = models[args.model]

    if args.mode == "image":
        unit = price_of(model, args.resolution, args.variant)
        total = unit * args.count
        print(f"{args.model} @ {args.resolution}: ${unit:.4f}/image x {args.count} = ${total:,.2f}")
    elif args.mode == "video":
        unit = price_of(model, args.resolution, args.variant)
        total = unit * args.seconds * args.count
        print(f"{args.model} @ {args.resolution}: ${unit:.4f}/second x {args.seconds}s x {args.count} = ${total:,.2f}")
    else:
        prices = model["prices"].get("effective", model["prices"])
        cost_in = args.input_tokens / 1_000_000 * float(prices.get("input", 0))
        cost_out = args.output_tokens / 1_000_000 * float(prices.get("output", 0))
        print(f"{args.model}: input ${cost_in:.4f} + output ${cost_out:.4f} = ${cost_in + cost_out:,.4f}")


if __name__ == "__main__":
    main()
