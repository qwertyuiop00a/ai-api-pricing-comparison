// image2.5 (GPT-Image-2.5) via APIMart: submit, poll, download. Node 18+.
const BASE = process.env.APIMART_BASE_URL ?? "https://api.apimart.ai/v1";
const KEY = process.env.APIMART_API_KEY;
const HEADERS = {
  Authorization: `Bearer ${KEY}`,
  "Content-Type": "application/json",
  "X-APIMart-Response-Version": "2026-07-27",
};
const sleep = ms => new Promise(r => setTimeout(r, ms));

export async function generateImage(prompt, { version = "flare", resolution = "1K", size = "1:1", n = 1 } = {}) {
  const created = await fetch(`${BASE}/images/generations`, {
    method: "POST",
    headers: { ...HEADERS, "Idempotency-Key": crypto.randomUUID() },
    body: JSON.stringify({ model: "gpt-image-2.5-ext", version, prompt, size, resolution, n }),
  });
  if (!created.ok) throw new Error(`submit failed: ${created.status} ${await created.text()}`);
  const { data } = await created.json();
  let delay = 3000;
  for (let waited = 0; waited < 900_000; waited += delay) {
    const res = await fetch(`${BASE}/tasks/${data.id}`, { headers: HEADERS });
    const task = (await res.json()).data;
    if (task.status === "completed") return task;
    if (task.status === "failed") throw new Error(JSON.stringify(task));
    await sleep(delay);
    delay = Math.min(delay * 2, 10_000);
  }
  throw new Error(`timeout: ${data.id}`);
}

if (process.argv[1]?.endsWith("javascript.mjs")) {
  const task = await generateImage(process.argv[2] ?? "A sky garden at dawn, architectural photography",
    { version: process.argv[3] ?? "flare", size: "16:9" });
  console.log("cost:", task.cost, "urls:", task.result.images[0].url);
}
