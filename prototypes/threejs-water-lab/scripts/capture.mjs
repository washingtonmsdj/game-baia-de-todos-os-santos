import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const endpoint = process.env.CDP_ENDPOINT ?? 'http://127.0.0.1:9223/json';
const output = resolve(process.argv[2] ?? 'water-lab-capture.png');
const pages = await (await fetch(endpoint)).json();
const page = pages.find((item) => item.type === 'page' && item.url.includes('127.0.0.1:5173'));
if (!page) throw new Error('Three.js Water Lab page not found in Chrome DevTools');

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

await send('Page.enable');
await send('Runtime.enable');
await new Promise((resolve) => setTimeout(resolve, 2500));
const info = await send('Runtime.evaluate', {
  expression: `({title:document.title, canvas:[...document.querySelectorAll('canvas')].map(c=>[c.width,c.height]), status:document.querySelector('#status')?.textContent, bodyText:document.body.innerText.slice(0,300)})`,
  returnByValue: true,
});
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true });
writeFileSync(output, Buffer.from(shot.data, 'base64'));
console.log(JSON.stringify({ output, page: page.url, ...info.result.value }, null, 2));
ws.close();
