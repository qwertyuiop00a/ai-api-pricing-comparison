# image2.5 API Pricing — Where $0.0085 Per Image Comes From

A pricing page you can check against reality: what **image2.5** costs per image on the relayed route, how that compares with token billing on the official route, and the arithmetic for 100, 10,000 and 1,000,000 images.

**Attributed entry points:** [Open GPT Image 2.5 on APIMart](https://go.apimart.ai/k-b1b768) · [Current pricing](https://go.apimart.ai/k-c9d4c5) · [Get an API key](https://go.apimart.ai/k-9cb7f0)

## Contents

- [Model routes and IDs](#model-routes-and-ids)
- [Observed pricing](#observed-pricing)
- [What the output looks like](#what-the-output-looks-like)
- [Quickstart](#quickstart)
- [Request and response reference](#request-and-response-reference)
- [Worked cost examples at the observed 1K price](#worked-cost-examples-at-the-observed-1k-price)
- [Hidden costs that are not on the price list](#hidden-costs-that-are-not-on-the-price-list)
- [FAQ](#faq)
- [Attributed links](#attributed-links-how-this-repository-is-measured)
- [Repository map](#repository-map)

## Why per-image pricing is easier to defend internally

Image work usually runs as a batch job: N assets, one approval, one invoice. Token billing makes that awkward because
the unit you buy is not the unit you ship. A per-delivered-image route lets a content team answer "what does one asset
cost?" without a spreadsheet of token traces.

Two details matter when you model it:

- **Only delivered images bill.** A submitted task that never completes should not appear as an image line item; reconcile against the `cost` field on completed tasks, not against submission counts.
- **Resolution multiplies, variant does not.** Within the same family, moving from 1K to 2K or 4K changes unit price, while choosing `flare` or `sunburst` does not.

For the arithmetic below we use the observed 1K unit price of **$0.0085** and the same 2K/4K ladder that APIMart publishes on its pricing page. Treat every number as a snapshot, not a contract.

## Model routes and IDs

| Route | `model` value | Selector | Billing style | Best for |
| --- | --- | --- | --- | --- |
| Official (token) | `gpt-image-2.5-flare` | n/a | token usage, `quality` low → max | everyday generation, batch drafts |
| Official (token) | `gpt-image-2.5-sunburst` | n/a | token usage, `quality` low → max | editing precision, production assets |
| Relayed (per image) | `gpt-image-2.5-ext` | `version: "flare"` | per delivered image (`n` ≤ 4) | high-volume generation at a flat price |
| Relayed (per image) | `gpt-image-2.5-ext` | `version: "sunburst"` | per delivered image (`n` ≤ 4) | edits and reference-driven work at a flat price |

Both relayed variants accept `resolution` `1K` / `2K` / `4K`, ten aspect ratios plus `auto`, and up to 16 reference images in `image_urls`. The official route adds exact pixel dimensions and the `low / medium / high / xhigh / max` quality ladder.

- Family: **GPT Image 2.5** — the OpenAI image generation and editing series served through APIMart
- Model IDs: `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst` (official route); `gpt-image-2.5-ext` with `version: flare|sunburst` (per-image relay route)
- Base URL: `https://api.apimart.ai/v1` — OpenAI-compatible `POST /v1/images/generations`
- Async tasks: submit, then poll `GET /v1/tasks/{task_id}` until `status: completed`
- Output tiers: `1K`, `2K`, `4K`; up to 16 reference images for image-to-image; `n` ≤ 4
- Observed 1K price on the relayed route: **$0.0085 per delivered image** (checked 2026-09-16)

## Observed pricing

| version | 1K | 2K | 4K | billing unit |
| --- | --- | --- | --- | --- |
| `flare` | $0.0085 | $0.014 | $0.021 | per delivered image |
| `sunburst` | $0.0085 | $0.014 | check live pricing | per delivered image |

Per-image billing on the relayed route is charged for delivered images, and the task response reports the exact amount in `cost` / `credits_cost`, so the table above can be re-verified after a single paid call. The official `gpt-image-2.5-flare` / `gpt-image-2.5-sunburst` route is token-billed with a `low → medium → high → xhigh → max` quality ladder, which is why this repository keeps both the flat per-image expectation and the token-billed option side by side. Snapshot date: 2026-09-16.

## What the output looks like

Every render below came from a single `POST /v1/images/generations` call on the relayed route, at the aspect ratio shown.
| Output | Recipe | Use case | Version | Ratio | Prompt |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/02-rainy-tokyo-alley.jpg" width="220" alt="Cinematic night street generated with GPT Image 2.5"> | Cinematic night street | Cinematic still | `flare` | 16:9 | `Rain-slicked Tokyo alley at night, neon sign reflections on wet asphalt, a lone cyclist with an umbrella, cinematic 35mm film still, shallow depth of field` |
| <img src="assets/04-gradient-paper-plane-icon.jpg" width="220" alt="App icon / 3D asset generated with GPT Image 2.5"> | App icon / 3D asset | UI asset | `flare` | 1:1 | `Glossy 3D app icon of a paper plane folded from a coral to violet gradient material, floating on a soft neutral grey backdrop, subtle contact shadow, centered composition` |
| <img src="assets/11-floating-ruin-keyart.jpg" width="220" alt="Game key art generated with GPT Image 2.5"> | Game key art | Game concept art | `sunburst` | 16:9 | `Fantasy game key art, an armored knight standing on a floating stone ruin above a sea of clouds, dramatic backlight, painterly detail, wide cinematic composition` |

Every recipe ships with the exact JSON body in [`examples/`](examples).

## Quickstart

The relayed route is asynchronous: submit, then poll the task ID.

```bash
# text to image on the per-image route
IDEMPOTENCY_KEY="$(uuidgen)"
curl --request POST \
  --url https://api.apimart.ai/v1/images/generations \
  --header "Authorization: Bearer $APIMART_API_KEY" \
  --header 'Content-Type: application/json' \
  --header 'X-APIMart-Response-Version: 2026-07-27' \
  --header "Idempotency-Key: $IDEMPOTENCY_KEY" \
  --data '{
    "model": "gpt-image-2.5-ext",
    "version": "flare",
    "prompt": "A cozy reading nook beside a window on a rainy day, warm table lamp, cinematic lighting",
    "size": "1:1",
    "resolution": "1K",
    "n": 1
  }'
```

```python
import os, time, uuid, requests

BASE = "https://api.apimart.ai/v1"
HEADERS = {
    "Authorization": f"Bearer {os.environ['APIMART_API_KEY']}",
    "Content-Type": "application/json",
    "X-APIMart-Response-Version": "2026-07-27",
    "Idempotency-Key": str(uuid.uuid4()),   # reuse on retry, not on a new image
}

def generate(prompt: str, version: str = "flare", resolution: str = "1K", size: str = "1:1") -> str:
    r = requests.post(f"{BASE}/images/generations", headers=HEADERS, timeout=60, json={
        "model": "gpt-image-2.5-ext", "version": version, "prompt": prompt,
        "size": size, "resolution": resolution, "n": 1,
    })
    r.raise_for_status()
    task_id = r.json()["data"]["id"]
    while True:
        t = requests.get(f"{BASE}/tasks/{task_id}", headers=HEADERS, timeout=60).json()["data"]
        if t["status"] in ("completed", "failed"):
            return t
        time.sleep(5)
```

```javascript
const headers = {
  Authorization: `Bearer ${process.env.APIMART_API_KEY}`,
  "Content-Type": "application/json",
  "X-APIMart-Response-Version": "2026-07-27",
  "Idempotency-Key": crypto.randomUUID(),
};
const res = await fetch("https://api.apimart.ai/v1/images/generations", {
  method: "POST",
  headers,
  body: JSON.stringify({
    model: "gpt-image-2.5-ext", version: "flare", prompt: "A sky garden at dawn, architectural photography",
    size: "16:9", resolution: "1K", n: 1,
  }),
});
const { data } = await res.json();          // data.id === task id
// poll GET https://api.apimart.ai/v1/tasks/${data.id} until data.status === "completed"
```

Official (token-billed) route, for comparison — same path, no `version`, quality ladder instead:

```bash
curl --request POST --url https://api.apimart.ai/v1/images/generations \
  --header "Authorization: Bearer $APIMART_API_KEY" --header 'Content-Type: application/json' \
  --data '{"model":"gpt-image-2.5-sunburst","prompt":"Preserve the product label, replace the background with soft off-white, add a natural cast shadow","size":"1:1","resolution":"1k","quality":"high","n":1}'
```

Full field reference: [official route docs](https://docs.apimart.ai/en/api-reference/images/gpt-image-2.5/generation) and [ext route docs](https://docs.apimart.ai/en/api-reference/images/gpt-image-2.5-ext/generation). Get a key at [apimart.ai/keys](https://go.apimart.ai/k-9cb7f0).

## Request and response reference (ext route)

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `model` | string | required | `gpt-image-2.5-ext` |
| `version` | string | `flare` | `flare` or `sunburst` |
| `prompt` | string | required | must not be empty after trimming |
| `resolution` | string | `1K` | `1K`, `2K`, `4K` |
| `size` | string | `auto` | `auto` or 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 5:4, 4:5, 21:9 |
| `n` | integer | `1` | 1–4 per request on the relayed route |
| `image_urls` | string[] | — | up to 16 references, URL or data URL, no extra charge |

Submission returns `202` with `data.id` (the task ID) and `data.poll_url`; `GET /v1/tasks/{task_id}` then reports
`status` (`pending` → `processing` → `completed` / `failed`), `progress`, `cost`, `credits_cost` and, when finished,
`result.images[].url` with an `expires_at` timestamp. Download outputs before that timestamp — the URLs are temporary.

## Worked cost examples at the observed 1K price

| Volume | Cost at $0.0085 / image | Equivalent token-billed comparison |
| --- | --- | --- |
| 1 image | $0.0085 | depends on output tokens |
| 100 images | $0.85 | needs per-image token measurement |
| 10,000 images | $85.00 | reconciliation from usage logs |
| 100,000 images | $850.00 | rarely economical without a flat route |
| 1,000,000 images | $8,500.00 | negotiated contract territory |

At 2K and 4K the unit price rises in steps; multiply the same volumes by the 2K/4K row in the table above before you
commit a budget.


## Hidden costs that are not on the price list

| Cost centre | What it looks like in practice |
| --- | --- |
| Failed tasks | retries without an idempotency key bill twice |
| Storage | result URLs expire, so you must download and store outputs |
| Egress | re-serving generated images to users is not free |
| Review time | a rejected render costs review minutes, not just API cents |
| Prompt iteration | three variants per final asset triples the API line |



## FAQ

**Is $0.0085 per image the real image2.5 price?**

It is the observed 1K unit price on the `gpt-image-2.5-ext` route at the time of writing (2026-09-16), read back from the completed task's own `cost` field. Prices change; the [pricing page](https://go.apimart.ai/k-c9d4c5) is the authority.

**Is the cheapest route the same model as the official one?**

No. The `ext` route is a third-party relay that exposes the same family behaviour at a flat per-image price, while `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` are the officially routed, token-billed models. Test both against the same prompt set before you commit a pipeline to either.

**How do I keep a per-image budget from drifting?**

Sum the `cost` field of completed tasks per day, alert on cost per delivered asset rather than total spend, and always send an idempotency key so retries collapse into the original task.

**Does resolution or aspect ratio change the price?**

Resolution does (1K → 2K → 4K are separate price steps). Aspect ratio is a framing choice within a tier, not a separate price band.

## Related searches

- `image2.5 api`
- `image 2.5 api`
- `image2.5 api gateway`
- `image2-5 api`
- `gpt-image-2.5 api`
- `image2.5 api pricing`
- `ai api relay`
- `ai api gateway`
- `ai api aggregator`
- `apimart image2.5`
- `image2.5 api documentation`
- `openai compatible image api`
- `image2 5`
- `image2 5 api`
- `image 2 5 api`
- `api pricing`
- `apimart`

## Attributed links (how this repository is measured)

Every outbound link in this repository points at APIMart through a short link, so visits coming from this page are attributed instead of arriving as anonymous traffic.

| Purpose | Attributed link | Target |
| --- | --- | --- |
| Open GPT Image 2.5 on APIMart | <https://go.apimart.ai/k-b1b768> | `apimart.ai/model/gpt-image-2-5` |
| Current APIMart pricing | <https://go.apimart.ai/k-c9d4c5> | `apimart.ai/pricing` |
| Get an API key on APIMart | <https://go.apimart.ai/k-9cb7f0> | `apimart.ai/keys` |

- [ ] Attribution target: the three `go.apimart.ai` short links above, all minted through the promo link API (302 with `utm_source=kol_sponsor&utm_medium=sponsor&sclid=...`). The endpoint docs on `docs.apimart.ai` are referenced as plain links: the link service only accepts the `apimart.ai` main domain, so no attributed short link exists for them.
- [ ] Re-check the price on the pricing page before a production run: promotional routing can change.

## Disclosure

APIMart is the service described in this repository; this page is published to document it, not to claim official status. The `ext` route is a third-party relay endpoint billed per delivered image, while the `gpt-image-2.5-flare` / `gpt-image-2.5-sunburst` models are the token-billed route. Model names, prices and limits belong to their respective owners, and everything here is observation-dated (2026-09-16). Verify with a single paid request before scaling volume.


## Repository map

```text
image2.5-api-pricing-cheapest/
  PROMPTS.md           every recipe with its output
  README.md            overview, pricing, quickstart and FAQ
  examples/
    curl.sh            submit + poll with curl
    python_generate.py end-to-end Python client
    javascript.mjs     Node 18+ equivalent
  tools/check_links.py attribution + prompt-data validator
  .github/workflows/validate.yml  CI for the validator
  assets/              example renders (JPEG, resized for the README)
  LICENSE              MIT
```

## License

MIT — see [LICENSE](LICENSE). Model names and vendor documentation remain the property of their owners.
