import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export const OFFICIAL_CITY = Object.freeze({
  assetId: 'salvador-mvp-official-full-r30a11',
  sourceName: 'salvador_lacerda_mvp_r30a11_full.glb',
  defaultUrl: '/assets/city/salvador_lacerda_mvp_r30a11_full.glb',
  sourceScene: 'SALVADOR | ESBOCO OFICIAL',
  locations: Object.freeze(['elevador-lacerda', 'mercado-modelo', 'prefeitura-palacio-rio-branco']),
});

function loadGltf(url) {
  return new Promise((resolve, reject) => {
    new GLTFLoader().load(url, resolve, undefined, reject);
  });
}

function configureImportedCity(source) {
  const group = new THREE.Group();
  group.name = 'OFFICIAL CITY | Salvador | Blender hero geometry';
  // O Blender é Z-up e usa XY no plano. O GLTF Y-up converte Blender Y para
  // -Z; inverter somente o eixo de profundidade recompõe o espaço do runtime.
  group.scale.z = -1;
  source.traverse((object) => {
    if (!object.isMesh) return;
    object.castShadow = true;
    object.receiveShadow = true;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      if (material) material.side = THREE.DoubleSide;
    }
  });
  group.add(source);
  group.userData = {
    assetId: OFFICIAL_CITY.assetId,
    sourceKind: 'official_blender_full_glb',
    sourceScene: OFFICIAL_CITY.sourceScene,
    sourceUrl: OFFICIAL_CITY.defaultUrl,
    locations: [...OFFICIAL_CITY.locations],
    coordinateMapping: 'Blender XY -> Three.js XZ (Y-up GLTF depth corrected)',
  };
  return group;
}

export async function loadOfficialCity(options = {}) {
  const url = options.url || OFFICIAL_CITY.defaultUrl;
  const gltf = await loadGltf(url);
  const group = configureImportedCity(gltf.scene);
  group.userData.sourceUrl = url;
  return { object: group, asset: OFFICIAL_CITY, url };
}

