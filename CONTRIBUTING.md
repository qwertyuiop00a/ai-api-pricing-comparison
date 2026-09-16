# Contributing

Useful contributions to this repository:

1. A prompt recipe that reliably produces a usable asset (prompt + output + `version` + aspect ratio).
2. A correction to the pricing or limit notes, with the source page and the date you checked it.
3. A client example in another language that keeps the same submit → poll → download lifecycle.

Before opening a pull request:

```bash
python3 tools/check_links.py          # attribution links and prompt data
```

Rules: keep every APIMart link attributed through its `go.apimart.ai` short link, never commit API keys, and do not
paste outputs that contain third-party trademarks you have no right to publish.
