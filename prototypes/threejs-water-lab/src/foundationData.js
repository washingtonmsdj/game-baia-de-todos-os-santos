import { loadRuntimeManifest, loadJsonAsset } from './runtime/assets.js';
let cachedFoundation = null;

export async function loadFoundationData() {
  if (cachedFoundation) return cachedFoundation;
  const manifest=await loadRuntimeManifest();
  const payload=await loadJsonAsset(manifest.assets.foundation);
  if (payload.schema !== 'bay-of-all-saints/foundation-runtime-v1') {
    throw new Error(`foundation runtime schema inválido: ${payload.schema ?? 'ausente'}`);
  }
  if (!payload.terrain?.grid || !Array.isArray(payload.city?.buildings)) {
    throw new Error('foundation runtime incompleto');
  }
  cachedFoundation = payload;
  return cachedFoundation;
}
