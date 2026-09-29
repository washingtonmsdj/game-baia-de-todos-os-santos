import { createHash } from 'node:crypto';
import { copyFile, mkdir, stat } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const EXPECTED_SHA256 = 'F3D5DEE69DCAB15379817A9AE13E562DF8023FD7AF38E8B6A0CDB4742AB650A2';
const EXPECTED_BYTES = 47319716;
const SOURCE_NAME = 'yellow city bus 3d model.glb';
const here = dirname(fileURLToPath(import.meta.url));
const prototypeRoot = resolve(here, '..');
const repoRoot = resolve(prototypeRoot, '..', '..');

const candidates = [
  process.env.BOAS_INTEGRA_BUS_GLB,
  resolve(repoRoot, 'artifacts/incoming/integra-salvador', SOURCE_NAME),
  resolve(repoRoot, 'artifacts/incoming', SOURCE_NAME),
].filter(Boolean);

const destination = resolve(
  prototypeRoot,
  'public/assets/vehicles/integra-salvador',
  SOURCE_NAME,
);
async function sha256(path) {
  const file = await import('node:fs');
  return new Promise((resolveHash, reject) => {
    const hash = createHash('sha256');
    const stream = file.createReadStream(path);
    stream.on('data', (chunk) => hash.update(chunk));
    stream.on('error', reject);
    stream.on('end', () => resolveHash(hash.digest('hex').toUpperCase()));
  });
}

async function findSource() {
  for (const candidate of candidates) {
    try {
      const info = await stat(candidate);
      if (info.isFile()) return { path: candidate, size: info.size };
    } catch {
      // Try next approved location.
    }
  }
  return null;
}

const source = await findSource();
if (!source) {
  console.error('Integra bus GLB não encontrado. Defina BOAS_INTEGRA_BUS_GLB ou coloque o arquivo em artifacts/incoming/.');
  process.exit(2);
}
if (source.size !== EXPECTED_BYTES) {
  throw new Error(`Integra bus: tamanho incorreto ${source.size}; esperado ${EXPECTED_BYTES}`);
}

const digest = await sha256(source.path);
if (digest !== EXPECTED_SHA256) {
  throw new Error(`Integra bus: SHA-256 incorreto ${digest}; esperado ${EXPECTED_SHA256}`);
}

await mkdir(dirname(destination), { recursive: true });
await copyFile(source.path, destination);
const copied = await stat(destination);
const copiedDigest = await sha256(destination);
if (copied.size !== EXPECTED_BYTES || copiedDigest !== EXPECTED_SHA256) {
  throw new Error('Integra bus: verificação pós-cópia falhou');
}

console.log(JSON.stringify({
  ok: true,
  source: source.path,
  destination,
  bytes: copied.size,
  sha256: copiedDigest,
  gitPolicy: 'local_runtime_staging_not_versioned',
}, null, 2));
