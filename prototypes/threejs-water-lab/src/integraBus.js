import { measureWheelContacts, groundVehicle } from './vehicleGrounding.js';
import * as THREE from 'three';
import { loadRuntimeManifest, loadGlbAsset } from './runtime/assets.js';
const vehicleAsset=(await loadRuntimeManifest()).assets.vehicle;

export const INTEGRA_BUS=Object.freeze({
  assetId:vehicleAsset.id, sourceName:vehicleAsset.source.file,
  sourceSha256:vehicleAsset.sha256, sourceBytes:vehicleAsset.bytes,
  sourceTriangles:null, target:Object.freeze(vehicleAsset.dimensions),
  defaultUrl:vehicleAsset.url, runtimeStatus:'candidate_needs_lod_and_vehicle_rig',
});

const FORWARD = new THREE.Vector3(0, 0, 1);

function segmentLength(segment) {
  return segment.a.distanceTo(segment.b);
}

export function chooseIntegraStagingSegment(segments) {
  const usable = segments.filter((segment) => segmentLength(segment) >= 8);
  if (!usable.length) throw new Error('Integra bus: nenhum segmento R30A.7 >= 8 m');
  return usable.reduce((best, segment) => {
    const midpoint = segment.a.clone().add(segment.b).multiplyScalar(0.5);
    const score = midpoint.x * midpoint.x + midpoint.z * midpoint.z;
    return !best || score < best.score ? { segment, score } : best;
  }, null).segment;
}

function collectMeshStats(root) {
  let meshes = 0;
  let vertices = 0;
  let triangles = 0;
  const materials = new Set();
  root.traverse((object) => {
    if (!object.isMesh) return;
    meshes += 1;
    const geometry = object.geometry;
    vertices += geometry.attributes.position?.count ?? 0;
    triangles += geometry.index
      ? geometry.index.count / 3
      : (geometry.attributes.position?.count ?? 0) / 3;
    const list = Array.isArray(object.material) ? object.material : [object.material];
    for (const item of list) if (item) materials.add(item.uuid);
    object.castShadow = true;
    object.receiveShadow = true;
  });
  return {
    meshes,
    vertices,
    triangles: Math.round(triangles),
    materials: materials.size,
  };
}

function normalizeLoadedBus(source) {
  // A exportação antiga incluiu pisos de apresentação com 200 m de largura.
  // Eles não fazem parte do veículo e não podem participar da medição.
  const presentation = [];
  source.traverse(object => {
    if (/ch[aã]o.*est[uú]dio/i.test(object.name)) presentation.push(object);
  });
  for (const object of presentation) object.removeFromParent();
  const wrapper = new THREE.Group();
  wrapper.name = 'Integra Salvador Imported GLB';
  wrapper.add(source);
  source.updateMatrixWorld(true);

  const box = new THREE.Box3();
  source.traverse(object => {
    if (object.isMesh && !/retrovisor|plataforma/i.test(object.name)) {
      box.union(new THREE.Box3().setFromObject(object, true));
    }
  });
  const size = box.getSize(new THREE.Vector3());
  if (Math.min(size.x, size.y, size.z) <= 0) {
    throw new Error('Integra bus: bounding box inválida no GLB');
  }
  source.scale.set(
    INTEGRA_BUS.target.width / size.x,
    INTEGRA_BUS.target.height / size.y,
    INTEGRA_BUS.target.length / size.z,
  );
  source.updateMatrixWorld(true);

  const scaledBox = new THREE.Box3().setFromObject(source, true);
  const scaledCenter = scaledBox.getCenter(new THREE.Vector3());
  source.position.x -= scaledCenter.x;
  source.position.z -= scaledCenter.z;
  source.position.y -= scaledBox.min.y;
  source.updateMatrixWorld(true);
  wrapper.userData.dimensionBasis = 'Carroceria sem retrovisores e plataforma; dimensões nominais do projeto, não ficha técnica homologada';
  return wrapper;
}

function placeOnSegment(root, segment) {
  const midpoint = segment.a.clone().add(segment.b).multiplyScalar(0.5);
  const direction = segment.b.clone().sub(segment.a);
  direction.y = 0;
  direction.normalize();
  root.position.copy(midpoint);
  root.visible = groundVehicle(root.position, root.quaternion, direction, root.userData.wheelContacts);
  root.userData.stagingRoad = segment.way?.name || segment.id;
  root.userData.stagingSegmentId = segment.id;
}

function configureRoot(root, sourceKind, stats) {
  root.name = 'R30A13 | BUS | TORINO SALVADOR 31065';
  root.userData.assetId = INTEGRA_BUS.assetId;
  root.userData.assetType = 'vehicle';
  root.userData.vehicleClass = 'urban_bus';
  root.userData.sourceKind = sourceKind;
  root.userData.revision = 'v03';
  root.userData.doorSide = '-X';
  root.userData.exteriorDetail = 'front-rear-concept-v03';
  root.userData.sourceSha256 = INTEGRA_BUS.sourceSha256;
  root.userData.trafficBinding = 'candidate_only';
  root.userData.placement = 'road_graph_centerline_staging';
  root.userData.runtimeStatus = INTEGRA_BUS.runtimeStatus;
  root.userData.meshStats = stats;
  root.userData.targetDimensions = INTEGRA_BUS.target;
  root.userData.requiresLod = true;
  root.userData.requiresWheelRig = true;
  root.userData.requiresCollisionProxy = true;
}

export async function createIntegraBus(segments) {
  const segment=chooseIntegraStagingSegment(segments);
  const url=vehicleAsset.url;
  const gltf=await loadGlbAsset(vehicleAsset);
  const root=normalizeLoadedBus(gltf.scene);
  const stats=collectMeshStats(root);
  const sourceKind='approved_glb_candidate';
  const loadError=null;

  configureRoot(root, sourceKind, stats);
  const stagedSize = new THREE.Box3().setFromObject(root, true).getSize(new THREE.Vector3());
  root.userData.stagedDimensions = { x: stagedSize.x, y: stagedSize.y, z: stagedSize.z };
  root.userData.wheelContacts = measureWheelContacts(root);
  placeOnSegment(root, segment);
  root.userData.assetUrl = url;
  root.userData.loadError = loadError;

  return {
    object: root,
    sourceKind,
    loadError,
    assetUrl: url,
    stats,
    segment,
    contract: INTEGRA_BUS,
  };
}

export function integraBusStatus(bus) {
  return {
    assetId: INTEGRA_BUS.assetId,
    sourceKind: bus.sourceKind,
    loadedApprovedGlb: bus.sourceKind === 'approved_glb_candidate',
    sourceTriangles: INTEGRA_BUS.sourceTriangles,
    renderedTriangles: bus.stats.triangles,
    stagedDimensions: bus.object.userData.stagedDimensions,
    targetDimensions: { ...INTEGRA_BUS.target },
    runtimeReady: false,
    runtimeStatus: INTEGRA_BUS.runtimeStatus,
    stagingRoad: bus.object.userData.stagingRoad,
    stagingSegmentId: bus.object.userData.stagingSegmentId,
    loadError: bus.loadError,
  };
}
