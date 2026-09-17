# Contributing

Useful contributions:

1. A missing route, rate or billing unit — include the model id, the resolution or token direction, and the source page you checked.
2. A better estimator (per-tenant quota modelling, cached-input share, retry overhead).
3. Corrections where this snapshot disagrees with your own invoice, with the task or invoice evidence.

Before opening a pull request:

```bash
python tools/snapshot.py --from-file your_saved_pricing_page.html   # regenerates data/ and README tables
python tools/check_links.py
```

Every link to APIMart must be an attributed `go.apimart.ai` short link minted through the promo link API; hand-made tracking parameters are rejected by CI.
