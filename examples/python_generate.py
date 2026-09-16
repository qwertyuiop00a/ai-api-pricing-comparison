#!/usr/bin/env python3
"""image2.5 (GPT-Image-2.5) client: submit, poll with backoff, download, record cost."""
from __future__ import annotations
import argparse, os, pathlib, time, uuid
import requests

BASE = os.environ.get("APIMART_BASE_URL", "https://api.apimart.ai/v1").rstrip("/")
KEY = os.environ["APIMART_API_KEY"]
HEADERS = {
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "X-APIMart-Response-Version": "2026-07-27",
}


def generate(prompt: str, *, version: str = "flare", resolution: str = "1K",
             size: str = "1:1", n: int = 1, references: list[str] | None = None) -> dict:
    """Submit one image2.5 task and return the completed task payload."""
    headers = {**HEADERS, "Idempotency-Key": str(uuid.uuid4())}
    body = {"model": "gpt-image-2.5-ext", "version": version, "prompt": prompt,
            "size": size, "resolution": resolution, "n": n}
    if references:
        body["image_urls"] = references
    created = requests.post(f"{BASE}/images/generations", headers=headers, json=body, timeout=60)
    created.raise_for_status()
    task_id = created.json()["data"]["id"]

    delay, waited = 3.0, 0.0
    while waited < 900:
        task = requests.get(f"{BASE}/tasks/{task_id}", headers=HEADERS, timeout=60).json()["data"]
        if task["status"] == "completed":
            return task
        if task["status"] == "failed":
            raise RuntimeError(f"task {task_id} failed: {task}")
        time.sleep(delay)
        waited += delay
        delay = min(delay * 2, 10)
    raise TimeoutError(task_id)


def download(task: dict, outdir: pathlib.Path) -> list[pathlib.Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    saved = []
    for url in task["result"]["images"][0]["url"]:
        dest = outdir / (url.rsplit("/", 1)[-1] or "image.png")
        dest.write_bytes(requests.get(url, timeout=120).content)
        saved.append(dest)
    return saved


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate an image with image2.5 (GPT-Image-2.5) on APIMart")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--version", default="flare", choices=["flare", "sunburst"])
    ap.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"])
    ap.add_argument("--size", default="1:1")
    ap.add_argument("--n", type=int, default=1, choices=[1, 2, 3, 4])
    ap.add_argument("--out", default="out")
    args = ap.parse_args()

    task = generate(args.prompt, version=args.version, resolution=args.resolution, size=args.size, n=args.n)
    files = download(task, pathlib.Path(args.out))
    print(f"cost=${task.get('cost')} credits={task.get('credits_cost')} time={task.get('actual_time')}s")
    for f in files:
        print("saved", f)
