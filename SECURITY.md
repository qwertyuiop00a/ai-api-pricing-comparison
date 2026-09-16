# Security

- Never commit `APIMART_API_KEY` or any other credential; keep it in the environment or a secret manager.
- API keys seen in issues, logs or screenshots are considered compromised: rotate them immediately.
- Send keys in the `Authorization` header only, and send `Idempotency-Key` so a retried request cannot bill twice.
- Report a leaked key or a security problem privately to the maintainer rather than in a public issue.
