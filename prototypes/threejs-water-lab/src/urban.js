import * as THREE from 'three';
import { sampleTerrainHeight } from './terrain.js';

function boundsForPolygon(points) {
  let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
  for (const [x, z] of points) {
    minX = Math.min(minX, x); maxX = Math.max(maxX, x);
    minZ = Math.min(minZ, z); maxZ = Math.max(maxZ, z);
  }
  return { minX, maxX, minZ, maxZ };
}

function dominantAngle(points) {
  let bestLength = 0;
  let bestAngle = 0;
  for (let i = 0; i < points.length; i++) {
    const a = points[i], b = points[(i + 1) % points.length];
    const dx = b[0] - a[0], dz = b[1] - a[1];
    const length = dx * dx + dz * dz;
    if (length > bestLength) {
      bestLength = length;
      bestAngle = Math.atan2(dx, dz);
    }
  }
  return bestAngle;
}

function createFromFoundation(buildings) {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const material = new THREE.MeshStandardMaterial({ color: 0xb8aa94, roughness: 0.9, metalness: 0.0 });
  const mesh = new THREE.InstancedMesh(geometry, material, buildings.length);
  mesh.name = 'Foundation Urban Massing | OSM footprints';
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  const matrix = new THREE.Matrix4();
  const quaternion = new THREE.Quaternion();
  const scale = new THREE.Vector3();
  const position = new THREE.Vector3();
  const up = new THREE.Vector3(0, 1, 0);
  const tint = new THREE.Color();
  const colliders = [];

  for (let i = 0; i < buildings.length; i++) {
    const building = buildings[i];
    const box = boundsForPolygon(building.polygon);
    const width = Math.max(2.5, box.maxX - box.minX);
    const depth = Math.max(2.5, box.maxZ - box.minZ);
    const height = Math.max(3.0, Number(building.height_m) || 8.0);
    const x = (box.minX + box.maxX) * 0.5;
    const z = (box.minZ + box.maxZ) * 0.5;
    colliders.push({ x, z, radius: Math.max(width, depth) * 0.46 });
    const y = sampleTerrainHeight(x, z) + height * 0.5 + 0.08;
    const angle = dominantAngle(building.polygon);
    quaternion.setFromAxisAngle(up, angle);
    scale.set(width, height, depth);
    position.set(x, y, z);
    matrix.compose(position, quaternion, scale);
    mesh.setMatrixAt(i, matrix);
    const sourceTint = building.height_source === 'visual_proxy' ? 0.86 : 1.0;
    tint.setRGB(0.72 * sourceTint, 0.66 * sourceTint, 0.56 * sourceTint);
    mesh.setColorAt(i, tint);
  }
  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  return {
    mesh,
    colliders,
    stats: {
      buildings: buildings.length,
      source: 'OSM/georef building footprints',
      authoritative: true,
      heightsAuthoritative: false,
    },
  };
}

export function createUrbanMassing(segments, targetCount = 320, foundation = null) {
  const buildings = foundation?.city?.buildings ?? [];
  if (buildings.length) return createFromFoundation(buildings);

  const synthetic = [];
  for (const segment of segments.slice(0, targetCount)) {
    const center = new THREE.Vector3().lerpVectors(segment.a, segment.b, 0.5);
    const half = Math.max(3, segment.width * 0.9);
    synthetic.push({
      polygon: [[center.x - half, center.z - half], [center.x + half, center.z - half], [center.x + half, center.z + half], [center.x - half, center.z + half]],
      height_m: 8,
      height_source: 'visual_proxy',
    });
  }
  const result = createFromFoundation(synthetic);
  result.stats.source = 'road fallback proxy';
  result.stats.authoritative = false;
  return result;
}
