import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let manifestPromise;
export function loadRuntimeManifest() {
  if (!manifestPromise) manifestPromise = fetch('/world/runtime.json', {cache:'no-store'})
    .then(async response => {
      if (!response.ok) throw new Error('Pacote de runtime ausente. Execute tools/runtime/package_world.py após exportar a fonte ativa.');
      const data = await response.json();
      if (data.schema !== 'boas/runtime-world-v1' || data.coordinates?.runtime !== 'X,Z,-Y') {
        throw new Error('Contrato de runtime/coordenadas incompatível');
      }
      if (!data.source?.sha256 || !data.assets?.surfaces || !Array.isArray(data.sectors)) {
        throw new Error('Manifesto incompleto');
      }
      return data;
    }).catch(error => {
      const loading = document.querySelector('#loading');
      if (loading) loading.textContent = error.message;
      throw error;
    });
  return manifestPromise;
}

export async function loadAssetBytes(entry) {
  if (!entry?.url?.startsWith('/world/releases/')) throw new Error('Asset fora da release');
  const response = await fetch(entry.url);
  if (!response.ok) throw new Error(`${entry.id}: HTTP ${response.status}`);
  const bytes = await response.arrayBuffer();
  if (bytes.byteLength !== entry.bytes) throw new Error(`${entry.id}: tamanho divergente`);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  const hash = [...new Uint8Array(digest)].map(n=>n.toString(16).padStart(2,'0')).join('');
  if (hash !== entry.sha256) throw new Error(`${entry.id}: hash divergente`);
  return bytes;
}

export async function loadJsonAsset(entry) {
  return JSON.parse(new TextDecoder().decode(await loadAssetBytes(entry)));
}

export async function loadGlbAsset(entry) {
  return new GLTFLoader().parseAsync(await loadAssetBytes(entry), entry.url.slice(0,entry.url.lastIndexOf('/')+1));
}

export function disposeScene(root) {
  const geometries=new Set(), materials=new Set(), textures=new Set();
  root.traverse(object=>{
    if(object.geometry) geometries.add(object.geometry);
    for(const material of object.material ? (Array.isArray(object.material)?object.material:[object.material]) : []) {
      materials.add(material);
      for(const value of Object.values(material)) if(value?.isTexture) textures.add(value);
    }
  });
  for(const resource of [...geometries,...materials,...textures]) resource.dispose();
  root.removeFromParent();
}
