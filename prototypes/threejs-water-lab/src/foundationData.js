let cachedFoundation = null;

export async function loadFoundationData() {
  if (cachedFoundation) return cachedFoundation;
  const response = await fetch('/data/foundation_runtime.json', { cache: 'no-cache' });
  if (!response.ok) throw new Error(`foundation runtime HTTP ${response.status}`);
  const payload = await response.json();
  if (payload.schema !== 'bay-of-all-saints/foundation-runtime-v1') {
    throw new Error(`foundation runtime schema inválido: ${payload.schema ?? 'ausente'}`);
  }
  if (!payload.terrain?.grid || !Array.isArray(payload.city?.buildings)) {
    throw new Error('foundation runtime incompleto');
  }
  cachedFoundation = payload;
  return cachedFoundation;
}
