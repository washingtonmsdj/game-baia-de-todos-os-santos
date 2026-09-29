import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const endpoint = process.env.CDP_ENDPOINT ?? 'http://127.0.0.1:9223/json';
const targetUrl = process.env.TARGET_URL ?? 'http://127.0.0.1:5173/';
const output = resolve(process.argv[2] ?? 'foundation-capture.png');
const pages = await (await fetch(endpoint)).json();
let page = pages.find((item) => item.type === 'page' && item.url.startsWith(targetUrl));
if (!page) page = pages.find((item) => item.type === 'page');
if (!page) throw new Error('No Chrome DevTools page target is available');

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
if (!page.url.startsWith(targetUrl)) {
  await send('Page.navigate', { url: targetUrl });
}
await new Promise((resolve) => setTimeout(resolve, 4500));
const info = await send('Runtime.evaluate', {
  expression: `({title:document.title, canvas:[...document.querySelectorAll('canvas')].map(c=>[c.width,c.height]), status:document.querySelector('#status')?.textContent, stats:document.querySelector('#world-stats')?.textContent, loading:document.querySelector('#loading')?.className, bodyText:document.body.innerText.slice(0,500)})`,
  returnByValue: true,
});
const shot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true });
writeFileSync(output, Buffer.from(shot.data, 'base64'));
console.log(JSON.stringify({
  output,
  page: targetUrl,
  ...info.result.value,
}, null, 2));
ws.close();
