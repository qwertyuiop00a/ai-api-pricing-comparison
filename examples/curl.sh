#!/usr/bin/env bash
# image2.5 (GPT-Image-2.5) via the APIMart relayed route: submit, then poll, then download.
set -euo pipefail
: "${APIMART_API_KEY:?export APIMART_API_KEY first}"
BASE="https://api.apimart.ai/v1"
PROMPT="${1:-A cozy reading nook beside a window on a rainy day, warm table lamp, cinematic lighting}"
VERSION="${2:-flare}"          # flare | sunburst
SIZE="${3:-1:1}"               # auto | 1:1 | 16:9 | 9:16 | 4:3 | 3:4 | 3:2 | 2:3 | 5:4 | 4:5 | 21:9
RESOLUTION="${4:-1K}"          # 1K | 2K | 4K
IDEMPOTENCY_KEY="$(uuidgen)"     # reuse on retry of the same logical image

TASK_ID="$(curl -sS --request POST "$BASE/images/generations" \
  --header "Authorization: Bearer $APIMART_API_KEY" \
  --header 'Content-Type: application/json' \
  --header 'X-APIMart-Response-Version: 2026-07-27' \
  --header "Idempotency-Key: $IDEMPOTENCY_KEY" \
  --data "$(cat <<JSON
{"model":"gpt-image-2.5-ext","version":"$VERSION","prompt":"$PROMPT","size":"$SIZE","resolution":"$RESOLUTION","n":1}
JSON
)" | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["id"])')"

echo "task: $TASK_ID"
while :; do
  RESPONSE="$(curl -sS "$BASE/tasks/$TASK_ID" --header "Authorization: Bearer $APIMART_API_KEY")"
  STATUS="$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["status"])')"
  echo "status: $STATUS"
  [ "$STATUS" = "completed" ] && break
  [ "$STATUS" = "failed" ] && { printf '%s\n' "$RESPONSE"; exit 1; }
  sleep 5
done
printf '%s' "$RESPONSE" | python3 -c 'import json,sys; d=json.load(sys.stdin)["data"]; print("cost:", d.get("cost")); [print(u) for u in d["result"]["images"][0]["url"]]'
