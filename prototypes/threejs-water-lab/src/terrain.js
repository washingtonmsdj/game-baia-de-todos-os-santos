import * as THREE from 'three';
import { WORLD } from './worldConfig.js';

const WORLD_MIN_X = Math.min(WORLD.cityBounds.minX, WORLD.oceanBounds.minX);
const WORLD_MAX_X = Math.max(WORLD.cityBounds.maxX, WORLD.oceanBounds.maxX);
const WORLD_MIN_Z = Math.min(WORLD.cityBounds.minZ, WORLD.oceanBounds.minZ);
const WORLD_MAX_Z = Math.max(WORLD.cityBounds.maxZ, WORLD.oceanBounds.maxZ);

let foundation = null;
let terrainGrid = null;
let coastlineSamples = [];

export function configureTerrain(data) {
  foundation = data;
  terrainGrid = data?.terrain?.grid ?? null;
  coastlineSamples = (data?.city?.coastline ?? [])
    .flatMap((item) => item.points ?? [])
    .filter((point) => Array.isArray(point) && point.length >= 2)
    .map(([x, z]) => ({ x: Number(x), z: Number(z) }))
    .sort((a, b) => a.z - b.z);
}

function hash2(x, z) {
  const v = Math.sin(x * 12.9898 + z * 78.233) * 43758.5453;
  return v - Math.floor(v);
}

function smoothNoise(x, z) {
  const ix = Math.floor(x), iz = Math.floor(z);
  const fx = x - ix, fz = z - iz;
  const sx = fx * fx * (3 - 2 * fx), sz = fz * fz * (3 - 2 * fz);
  const a = hash2(ix, iz), b = hash2(ix + 1, iz);
  const c = hash2(ix, iz + 1), d = hash2(ix + 1, iz + 1);
  return THREE.MathUtils.lerp(
    THREE.MathUtils.lerp(a, b, sx),
    THREE.MathUtils.lerp(c, d, sx),
    sz,
  );
}

function fallbackCoastlineX(z) {
  return -392 + Math.sin(z * 0.0052) * 28 + Math.sin(z * 0.014) * 11;
}

export function coastlineX(z) {
  if (coastlineSamples.length < 2) return fallbackCoastlineX(z);
  if (z <= coastlineSamples[0].z) return coastlineSamples[0].x;
  const last = coastlineSamples[coastlineSamples.length - 1];
  if (z >= last.z) return last.x;
  let lo = 0, hi = coastlineSamples.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (coastlineSamples[mid].z <= z) lo = mid;
    else hi = mid;
  }
  const a = coastlineSamples[lo], b = coastlineSamples[hi];
  const span = Math.max(0.001, b.z - a.z);
  return THREE.MathUtils.lerp(a.x, b.x, (z - a.z) / span);
}

export function isWaterAt(x, z) {
  return x < coastlineX(z);
}

function sampleRuntimeGrid(x, z) {
  const g = terrainGrid;
  if (!g || x < g.min_x || x > g.max_x || z < g.min_z || z > g.max_z) return null;
  const u = (x - g.min_x) / Math.max(0.001, g.max_x - g.min_x) * (g.nx - 1);
  const v = (z - g.min_z) / Math.max(0.001, g.max_z - g.min_z) * (g.nz - 1);
  const x0 = Math.floor(u), z0 = Math.floor(v);
  const x1 = Math.min(g.nx - 1, x0 + 1), z1 = Math.min(g.nz - 1, z0 + 1);
  const tx = u - x0, tz = v - z0;
  const h00 = g.heights[z0 * g.nx + x0];
  const h10 = g.heights[z0 * g.nx + x1];
  const h01 = g.heights[z1 * g.nx + x0];
  const h11 = g.heights[z1 * g.nx + x1];
  return THREE.MathUtils.lerp(
    THREE.MathUtils.lerp(h00, h10, tx),
    THREE.MathUtils.lerp(h01, h11, tx),
    tz,
  );
}

function fallbackTerrainHeight(x, z) {
  const shore = coastlineX(z);
  const signedDistance = x - shore;
  if (signedDistance < 0) {
    const offshore = Math.min(1, -signedDistance / 420);
    const shelf = THREE.MathUtils.lerp(-1.2, -13.5, Math.pow(offshore, 0.72));
    return WORLD.waterLevel + shelf + (smoothNoise(x * 0.018, z * 0.018) - 0.5) * 0.9;
  }
  const inland = Math.min(1, signedDistance / 520);
  const coastalRise = 0.65 + Math.pow(inland, 0.76) * 27;
  const broadHills = Math.sin(z * 0.0061) * 4.8 + Math.sin((x + z) * 0.0032) * 3.2;
  const detail = (smoothNoise(x * 0.012, z * 0.012) - 0.5) * 5.2;
  return WORLD.waterLevel + coastalRise + broadHills * inland + detail * inland;
}

export function sampleTerrainHeight(x, z) {
  if (isWaterAt(x, z)) return fallbackTerrainHeight(x, z);
  return sampleRuntimeGrid(x, z) ?? fallbackTerrainHeight(x, z);
}

export function sampleGameplayGround(x, z) {
  if (isWaterAt(x, z)) return null;
  return sampleTerrainHeight(x, z);
}

export function terrainSourceAt(x, z) {
  if (isWaterAt(x, z)) return 'water/seabed-proxy';
  return sampleRuntimeGrid(x, z) == null ? 'procedural-fallback' : 'blender-terrain-samples';
}

export function createTerrainMesh() {
  const width = WORLD_MAX_X - WORLD_MIN_X;
  const depth = WORLD_MAX_Z - WORLD_MIN_Z;
  const geometry = new THREE.PlaneGeometry(width, depth, 190, 220);
  geometry.rotateX(-Math.PI / 2);
  geometry.translate((WORLD_MIN_X + WORLD_MAX_X) * 0.5, 0, (WORLD_MIN_Z + WORLD_MAX_Z) * 0.5);
  const pos = geometry.attributes.position;
  const colors = new Float32Array(pos.count * 3);
  const landLow = new THREE.Color('#61705d');
  const landHigh = new THREE.Color('#7d806c');
  const sand = new THREE.Color('#a49778');
  const seabed = new THREE.Color('#315b59');
  const color = new THREE.Color();
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), z = pos.getZ(i);
    const y = sampleTerrainHeight(x, z);
    pos.setY(i, y);
    if (isWaterAt(x, z)) {
      color.copy(seabed).multiplyScalar(0.78 + smoothNoise(x * 0.01, z * 0.01) * 0.22);
    } else {
      const shore = Math.min(1, Math.max(0, (x - coastlineX(z)) / 40));
      color.copy(sand).lerp(landLow, shore).lerp(
        landHigh,
        Math.min(1, Math.max(0, (y - 8) / 40)) * 0.58,
      );
    }
    colors[i * 3] = color.r;
    colors[i * 3 + 1] = color.g;
    colors[i * 3 + 2] = color.b;
  }
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  geometry.computeVertexNormals();
  const material = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.96, metalness: 0.0 });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = 'Foundation Terrain | Blender samples + fallback';
  mesh.receiveShadow = true;
  return mesh;
}

export function createCoastlineGuide() {
  const points = [];
  if (coastlineSamples.length) {
    for (const p of coastlineSamples) {
      points.push(new THREE.Vector3(p.x, WORLD.waterLevel + 0.12, p.z));
    }
  } else {
    for (let z = WORLD_MIN_Z; z <= WORLD_MAX_Z; z += 8) {
      const x = coastlineX(z);
      points.push(new THREE.Vector3(x, WORLD.waterLevel + 0.12, z));
    }
  }
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({ color: 0xd6c79a, transparent: true, opacity: 0.62 });
  const line = new THREE.Line(geometry, material);
  line.name = 'Foundation Coastline | OSM/georef candidate';
  return line;
}

export const WORLD_BOUNDS = Object.freeze({ minX: WORLD_MIN_X, maxX: WORLD_MAX_X, minZ: WORLD_MIN_Z, maxZ: WORLD_MAX_Z });
