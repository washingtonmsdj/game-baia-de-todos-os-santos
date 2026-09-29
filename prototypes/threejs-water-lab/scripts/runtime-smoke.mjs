const endpoint = process.env.CDP_ENDPOINT ?? 'http://127.0.0.1:9223/json';
const targetUrl = process.env.TARGET_URL ?? 'http://127.0.0.1:5173/';
const pages = await (await fetch(endpoint)).json();
const page = pages.find((item) => item.type === 'page' && item.url.startsWith(targetUrl));
if (!page) throw new Error(`Foundation Lab page not found at ${targetUrl}`);

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((ok, fail) => {
  ws.addEventListener('open', ok, { once: true });
  ws.addEventListener('error', fail, { once: true });
});
let nextId = 1;
const pending = new Map();
ws.addEventListener('message', (event) => {
  const message = JSON.parse(event.data);
  if (!message.id || !pending.has(message.id)) return;
  const handlers = pending.get(message.id);
  pending.delete(message.id);
  message.error ? handlers.reject(new Error(JSON.stringify(message.error))) : handlers.resolve(message.result);
});

function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text ?? 'runtime evaluation failed');
  return result.result.value;
}

await send('Runtime.enable');
let ready = false;
for (let attempt = 0; attempt < 120; attempt++) {
  ready = await evaluate(`Boolean(window.__ALL_SAINTS__?.snapshot)`);
  if (ready) break;
  await new Promise((resolve) => setTimeout(resolve, 250));
}
if (!ready) {
  const diagnostic = await evaluate(`({
    loading: document.querySelector('#loading')?.textContent ?? null,
    body: document.body?.innerText?.slice(0, 500) ?? null,
  })`);
  throw new Error(`window.__ALL_SAINTS__ runtime API is not ready: ${JSON.stringify(diagnostic)}`);
}

const initial = await evaluate(`window.__ALL_SAINTS__.snapshot()`);
if (initial.mode !== 'A PÉ') throw new Error(`expected land spawn, got ${initial.mode}`);
if (initial.buildings < 1000) throw new Error('foundation buildings were not loaded');
if (initial.traffic.vehicles < 40) throw new Error('traffic population is too small');
if (!initial.integraBus) throw new Error('Integra bus staging status is missing');
if (initial.integraBus.assetId !== 'vehicle-integra-salvador-01') throw new Error('Integra bus asset id mismatch');
if (initial.integraBus.runtimeReady !== false) throw new Error('Integra bus must remain authoring-only');
if (initial.integraBus.sourceTriangles !== 1954141) throw new Error('Integra bus source triangle count mismatch');
if (!['proxy', 'approved_glb_candidate'].includes(initial.integraBus.sourceKind)) {
  throw new Error(`unexpected Integra source kind: ${initial.integraBus.sourceKind}`);
}

const busVisible0 = await evaluate(`window.__ALL_SAINTS__.integraBus.object.visible`);
await evaluate(`window.__ALL_SAINTS__.integraBus.object.visible = !window.__ALL_SAINTS__.integraBus.object.visible`);
const busVisible1 = await evaluate(`window.__ALL_SAINTS__.integraBus.object.visible`);
if (busVisible0 === busVisible1) throw new Error('Integra bus visibility toggle failed');
await evaluate(`window.__ALL_SAINTS__.integraBus.object.visible = true`);

const t0 = await evaluate(`window.__ALL_SAINTS__.traffic.vehicles[0].t`);
await evaluate(`window.__ALL_SAINTS__.traffic.update(0.5)`);
const t1 = await evaluate(`window.__ALL_SAINTS__.traffic.vehicles[0].t`);
if (t0 === t1) throw new Error('traffic agent did not advance under deterministic update');

await evaluate(`window.__ALL_SAINTS__.teleport(-520, 20, -2.0)`);
await evaluate(`window.__ALL_SAINTS__.player.update(0.016, 10.0)`);
const diving = await evaluate(`window.__ALL_SAINTS__.snapshot()`);
if (diving.mode !== 'MERGULHO') throw new Error(`expected diving state, got ${diving.mode}`);
await evaluate(`window.__ALL_SAINTS__.reset()`);
await evaluate(`window.__ALL_SAINTS__.player.update(0.016, 11.0)`);
const reset = await evaluate(`window.__ALL_SAINTS__.snapshot()`);
if (reset.mode !== 'A PÉ') throw new Error(`reset did not return to land: ${reset.mode}`);
const boatY0 = await evaluate(`window.__ALL_SAINTS__.boat.position.y`);
await evaluate(`window.__ALL_SAINTS__.boatController.update(20.0)`);
const boatY1 = await evaluate(`window.__ALL_SAINTS__.boat.position.y`);
if (Math.abs(boatY1 - boatY0) < 1e-5) throw new Error('boat buoyancy proxy did not react to waves');

console.log(JSON.stringify({
  ok: true,
  initial,
  trafficAdvanced: { from: t0, to: t1 },
  integraBus: initial.integraBus,
  busVisibilityToggle: { from: busVisible0, to: busVisible1 },
  diving,
  reset,
  boatDeltaY: boatY1 - boatY0,
}, null, 2));
ws.close();
