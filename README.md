# AI API Pricing Comparison — Per-Image, Per-Second and Per-Million-Token Costs

A machine-checkable pricing snapshot for **image**, **video** and **text** API routes, rebuilt every day from the
public pricing payload. Use it to answer the only question that matters before a batch job runs: *what will this
cost, and which route gives the same output for less?*

<!-- snapshot:date -->2026-09-17<!-- /snapshot:date -->

**Attributed entry points:** [Browse the model catalog](https://go.apimart.ai/k-118dd7) · [Current pricing](https://go.apimart.ai/k-748909) · [Get an API key](https://go.apimart.ai/k-c1f263)

## What this repository is (and is not)

- **Is:** a reproducible snapshot plus the tool that produces it, a cost calculator you can run offline, and the
  route-level comparison that pricing tables usually hide (per-image vs token billing).
- **Is not:** a promise that a price will hold. Every number below is a snapshot with a date; the extractor re-runs daily
  in CI and commits the diff, so the history of price changes is in this repository's git log.

## How the snapshot is produced

| Item | Value |
| --- | --- |
| Source page | `https://apimart.ai/en/pricing` |
| Method | React Server Component payload of the public page — **no API key required** |
| Extractor | [`tools/snapshot.py`](tools/snapshot.py) (fetch → parse → write `data/pricing.json` → refresh the tables below) |
| Snapshot date | <!-- snapshot:date -->2026-09-17<!-- /snapshot:date --> |
| Models captured | 304 across `image`, `token`, per-second and per-call billing units |
| CI | [`.github/workflows/refresh-pricing.yml`](.github/workflows/refresh-pricing.yml) runs daily at 06:17 UTC and commits only when something moved |

Among the things it answers:

- how much one image costs on a per-image route, by resolution (`1K` / `2K` / `4K`);
- how much one second of generated video costs, by resolution tier (`480P` / `720P` / `1080P`);
- how much a text model costs per million input, cached-input and output tokens.

## Image generation pricing (per delivered image)

Effective prices after the default group discount; list prices are in [`data/pricing.json`](data/pricing.json).

<!-- pricing:image:start -->
| Route (model id) | 1K / default | 2K | 4K | Notes |
| --- | --- | --- | --- | --- |
| `gpt-image-2.5-ext` — image2.5 (GPT-Image-2.5 ext route) | $0.0085 | $0.014 | $0.021 | per-image relay route, the cheapest image2.5 entry |
| `gemini-3-pro-image-preview` — Nano Banana Pro | $0.03 | $0.03 | $0.04 | highest-fidelity Gemini image route |
| `gemini-3.1-flash-image-preview` — Nano Banana 2 | $0.015 | $0.02 | $0.025 | fast Gemini image route |
| `gemini-2.5-flash-image-preview` — Nano Banana | $0.0125 | $0.0125 | $0.0125 | first-generation Gemini image route |
| `grok-imagine-1.5-apimart` — Grok Image 1.5 | $0.015 | $0.015 | $0.015 | text-to-image on the Grok Imagine route |
| `grok-imagine-1.5-edit-apimart` — Grok Image 1.5 (edit) | $0.015 | $0.015 | $0.015 | image editing on the same route family |
| `grok-imagine-image` — Grok Imagine image | $0.016 | $0.016 | — | alternative Grok image route |
| `seedream-4-0` — Seedance 4.0 image | $0.0195 | $0.0195 | $0.0195 | Seedream family image route |
| `seedream-4-5` — Seedance 4.5 image | $0.026 | $0.026 | $0.026 | Seedream family image route |
| `gpt-image-2` — GPT-Image-2 (ext) | $0.0085 | $0.014 | $0.021 | previous-generation per-image route |
<!-- pricing:image:end -->

## Video generation pricing (per second of output)

Video routes bill by resolution and seconds of output, and reference-image inputs are priced separately on most
Seedance routes — check the `*-input` keys in `data/pricing.json` before budgeting an image-to-video job.

<!-- pricing:video:start -->
| Route (model id) | 480p / second | 720p / second | 1080p / second | Notes |
| --- | --- | --- | --- | --- |
| `seedance-2.5` — Seedance 2.5 | $0.0961 | $0.216 | $0.3849 | current Seedance video route |
| `seedance-2.0` — Seedance 2.0 | $0.066 | $0.142 | $0.3544 | previous Seedance video route |
| `seedance-2.0-mini` — Seedance 2.0 mini | $0.0106 | $0.0229 | — | budget video route |
| `seedance-2.0-fast` — Seedance 2.0 fast | $0.0398 | $0.0856 | — | latency-optimised video route |
| `seedance-1-5-pro` — Seedance 1.5 Pro | $0.0204 | $0.044 | $0.108 | older Pro route kept for comparison |
| `seedance-1-0-pro-quality` — Seedance 1.0 Pro Quality | $0.0204 | $0.044 | $0.104 | legacy Pro route |
| `kling-3.0-turbo` — Kling 3.0 Turbo | — | $0.1144 | $0.1432 | third-party video route |
<!-- pricing:video:end -->

## Text model pricing (per million tokens)

<!-- pricing:token:start -->
| Model id | Input / 1M | Cached input / 1M | Output / 1M | Notes |
| --- | --- | --- | --- | --- |
| `gpt-5.5` — GPT-5.5 | $4.00 | $0.4 | $24.00 | flagship reasoning/chat tier |
| `gpt-5.5-pro` — GPT-5.5 Pro | $24.00 | — | $144.00 | highest-tier GPT-5.5 |
| `gpt-5.4` — GPT-5.4 | $2.00 | $0.2 | $12.00 | previous flagship tier |
| `gpt-5.1` — GPT-5.1 | $1.00 | $0.1 | $8.00 | mid-tier GPT-5 line |
| `gpt-5-mini` — GPT-5 mini | $0.2 | $0.02 | $1.60 | cheap GPT-5 tier |
| `gpt-5-nano` — GPT-5 nano | $0.04 | $0.004 | $0.32 | cheapest GPT-5 tier |
| `claude-opus-5` — Claude Opus 5 | $4.00 | $0.4 | $20.00 | Anthropic flagship |
| `claude-opus-4-8` — Claude Opus 4.8 | $4.00 | $0.4 | $20.00 | previous Anthropic flagship |
| `claude-sonnet-4-6` — Claude Sonnet 4.6 | $2.40 | $0.24 | $12.00 | balanced Anthropic tier |
| `claude-haiku-4-5-20251001` — Claude Haiku 4.5 | $0.8 | $0.08 | $4.00 | cheap Anthropic tier |
| `deepseek-v4-pro` — DeepSeek V4 Pro | $1.03 | $0.2057 | $3.09 | DeepSeek flagship |
| `deepseek-v4-flash` — DeepSeek V4 Flash | $0.3429 | $0.0686 | $1.03 | cheap DeepSeek tier |
| `deepseek-v3.2` — DeepSeek V3.2 | $0.2056 | — | $0.3084 | previous DeepSeek generation |
<!-- pricing:token:end -->

## Why the route matters more than the model name

The same model family is often sold on two routes with different billing units, and the cheaper one is not always the
one with the familiar model name:

| Route style | Unit | What it means for a pipeline |
| --- | --- | --- |
| Token-billed flagship (`gpt-image-2.5-flare`, `claude-opus-5`, `gpt-5.5`) | per million tokens | cost scales with output size; budgeting requires measuring |
| Relayed per-image (`gpt-image-2.5-ext`, `gemini-3-pro-image-preview`) | per delivered image (by resolution) | cost per asset is a constant you can multiply |
| Per-second video (`seedance-2.0`, `seedance-2.5`) | per second of output (by resolution) | cost = clip length × resolution rate × videos |
| Per-call / per-track units | per call, per track | flat fee per artefact |

Practical consequences:

1. **A flat per-image route makes cost a multiplication.** 1,000 images at $0.0085 is $8.50 — `1,000 × 0.0085`.
2. **Token-billed image output is dominated by the image output rate, not the prompt.** That is why this snapshot lists
   `text_input` / `image_input` / `image_output` separately for token-billed image routes.
3. **Per-second video pricing punishes long clips, not resolution alone.** A 10-second 480P clip on the budget Seedance
   route can cost less than a 4-second 1080P clip on a premium route.

## Estimate your own workload

```bash
# one image on the cheapest image2.5 entry (1K, per-image route)
python examples/cost_calculator.py image --model gpt-image-2.5-ext --resolution 1K --count 1000
# -> gpt-image-2.5-ext @ 1K: $0.0085/image x 1000 = $8.50

# a batch of 10-second budget video clips
python examples/cost_calculator.py video --model seedance-2.0-mini --resolution 480P --seconds 10 --count 50
# -> seedance-2.0-mini @ 480P: $0.0106/second x 10.0s x 50 = $5.28

# a text workload: 1M input + 100k output tokens
python examples/cost_calculator.py tokens --model gpt-5.5 --input-tokens 1000000 --output-tokens 100000
# -> gpt-5.5: input $4.0000 + output $2.4000 = $6.40
```

Discover model ids before you estimate:

```bash
python examples/cost_calculator.py list --spec image --grep image2.5
python examples/cost_calculator.py list --spec token --grep claude
```

## Verify a price in three ways

1. **Re-run the extractor** — `python tools/snapshot.py --from-file page.html` and read `data/pricing.json`.
2. **Read the task response** — a completed generation task returns `cost` (USD) and `credits_cost` for that exact job;
   that number, not the list price, is what a budget reconciliation should sum.
3. **Sum delivered artefacts, not submissions** — retries without an `Idempotency-Key` bill twice, and failed tasks
   should not appear as image line items.

## FAQ

**What is the cheapest way to generate one image?**
On this snapshot the per-image relay entries are the cheapest tier: image2.5 (`gpt-image-2.5-ext`) at $0.0085 per 1K
image. Nano Banana 2 sits at $0.015 and Grok Image 1.5 at $0.015, Nano Banana Pro at $0.03 per image ($0.04 at 4K).

**Is per-image billing always cheaper than token billing?**
No. Token billing rewards small, cache-heavy workloads (cached input can be a tenth of input price), while per-image
billing wins on large, uniform batches. Compare both on your own prompt set — the calculator above gives you the
arithmetic, the routes give you the output.

**How do I compare two LLM routes fairly?**
Convert both to the same unit and include the cached-input share: `cost = input/1M × in_rate + cached/1M × cached_rate +
output/1M × out_rate`. A model with a higher output rate can still be cheaper if it emits fewer tokens.

**Why publish a pricing snapshot as a repository instead of a page?**
Because a git repository gives you the diff. When a price moves, the commit shows the old and new value with a
timestamp, and the CI keeps it fresher than a hand-updated table.

**Do these prices include the input prompt cost?**
For per-image routes, no: the unit price covers the delivered image. For token-billed routes the snapshot lists
`text_input`, `image_input` and `image_output` separately so you can price the prompt as well.

## Related searches

- `ai api pricing comparison`
- `llm api comparison`
- `cheapest llm api`
- `ai api pricing calculator`
- `image generation api pricing`
- `video generation api cost`
- `image2.5 api pricing`
- `ai api gateway`

## Attributed links (how this repository is measured)

| Purpose | Attributed link | Target |
| --- | --- | --- |
| Browse the model catalog | <https://go.apimart.ai/k-118dd7> | `apimart.ai/model` |
| Current pricing page | <https://go.apimart.ai/k-748909> | `apimart.ai/pricing` |
| Get an API key | <https://go.apimart.ai/k-c1f263> | `apimart.ai/keys` |

Outbound APIMart links are minted through the promo link API (`go.apimart.ai`) so traffic from this repository is
attributed. Hand-made tracking parameters are rejected by CI (`tools/check_links.py`).

## Disclosure

APIMart is the service whose public pricing page is the data source for this snapshot; this repository is published to
document it, not to claim official status. Prices, model names and limits belong to their respective owners, and the
`ext` / relayed routes are third-party relay endpoints rather than first-party vendor endpoints. Observation date:
<!-- snapshot:date -->2026-09-17<!-- /snapshot:date -->. Verify with one paid request before scaling a batch.

## Repository map

```text
README.md                     pricing snapshot, route comparison, calculator and FAQ
data/pricing.json             full snapshot (304 models: image, per-second, token, per-call)
tools/snapshot.py             fetch → parse → rebuild tables (runs daily in CI)
tools/check_links.py          attribution + data guard (CI)
examples/cost_calculator.py   offline cost estimates for image, video and token routes
.github/workflows/            daily price refresh + validation
LICENSE                       MIT
```

## License

MIT — see [LICENSE](LICENSE). Model names, prices and vendor documentation remain the property of their owners.
