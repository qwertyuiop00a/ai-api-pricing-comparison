# Security

- This repository contains no credentials and needs none: the pricing snapshot is read from a public page.
- Never commit API keys. Keys belong in environment variables (`APIMART_API_KEY`) or a secret manager.
- Retried requests must reuse an `Idempotency-Key`, otherwise a timeout can bill the same image twice.
- Report a leaked key or a data error privately to the maintainer instead of opening a public issue.
