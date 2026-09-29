import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export const INTEGRA_BUS = Object.freeze({
  assetId: 'vehicle-torino-salvador-31065',
  sourceName: 'onibus_torino_31065_v03.glb',
  sourceSha256: 'F3F9BE5E2B6DF944677348EAD51F4A96D4607933F594DCFFF60BA45A752A7EB7',
  sourceBytes: 4666548,
  sourceGeometryCount: 480,
  sourceVertices: null,
  sourceTriangles: null,
  target: Object.freeze({ length: 12.0, width: 2.55, height: 3.25 }),
  defaultUrl: '/assets/vehicles/torino-31065/onibus_torino_31065_v03.glb',
  runtimeStatus: 'authoring_only_needs_lod_and_vehicle_rig',
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

function material(color, roughness = 0.62, metalness = 0.02) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness });
}

function wheelMesh() {
  const tire = new THREE.Mesh(
    new THREE.CylinderGeometry(0.48, 0.48, 0.28, 18),
    material(0x17191a, 0.88, 0.02),
  );
  tire.rotation.z = Math.PI / 2;
  tire.castShadow = true;
  tire.receiveShadow = true;
  return tire;
}

export function createIntegraBusProxy() {
  const root = new THREE.Group();
  root.name = 'Torino 31065 Bus Proxy';
  root.userData.proxy = true;

  const body = new THREE.Mesh(
    new THREE.BoxGeometry(2.55, 2.45, 11.75),
    material(0xf2bf1b, 0.5, 0.04),
  );
  body.position.y = 1.52;
  body.castShadow = true;
  body.receiveShadow = true;
  root.add(body);

  const roof = new THREE.Mesh(
    new THREE.BoxGeometry(2.44, 0.38, 11.35),
    material(0xe9e5d7, 0.72),
  );
  roof.position.y = 3.06;
  roof.castShadow = true;
  root.add(roof);

  const glass = material(0x1f3540, 0.22, 0.08);
  const sideWindowGeometry = new THREE.BoxGeometry(0.04, 1.02, 8.9);
  for (const x of [-1.286, 1.286]) {
    const windows = new THREE.Mesh(sideWindowGeometry, glass);
    windows.position.set(x, 2.12, -0.35);
    root.add(windows);
  }

  const frontGlass = new THREE.Mesh(new THREE.BoxGeometry(2.18, 1.05, 0.04), glass);
  frontGlass.position.set(0, 2.12, 5.89);
  root.add(frontGlass);
  const rearGlass = frontGlass.clone();
  rearGlass.position.z = -5.89;
  root.add(rearGlass);

  const wheelPositions = [
    [-1.135, 0.48, 3.75], [1.135, 0.48, 3.75],
    [-1.135, 0.48, -3.9], [1.135, 0.48, -3.9],
  ];
  for (const [x, y, z] of wheelPositions) {
    const wheel = wheelMesh();
    wheel.position.set(x, y, z);
    root.add(wheel);
  }

  const bumperMaterial = material(0x2d3233, 0.85, 0.04);
  for (const z of [-5.91, 5.91]) {
    const bumper = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.34, 0.18), bumperMaterial);
    bumper.position.set(0, 0.62, z);
    root.add(bumper);
  }
  return root;
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
  const wrapper = new THREE.Group();
  wrapper.name = 'Integra Salvador Imported GLB';
  wrapper.add(source);
  source.updateMatrixWorld(true);

  const box = new THREE.Box3().setFromObject(source);
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

  const scaledBox = new THREE.Box3().setFromObject(source);
  const scaledCenter = scaledBox.getCenter(new THREE.Vector3());
  source.position.x -= scaledCenter.x;
  source.position.z -= scaledCenter.z;
  source.position.y -= scaledBox.min.y;
  source.updateMatrixWorld(true);
  return wrapper;
}

function placeOnSegment(root, segment) {
  const midpoint = segment.a.clone().add(segment.b).multiplyScalar(0.5);
  const direction = segment.b.clone().sub(segment.a);
  direction.y = 0;
  direction.normalize();
  root.position.copy(midpoint);
  root.position.y += 0.05;
  root.quaternion.setFromUnitVectors(FORWARD, direction);
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
  root.userData.requiresLod = true;
  root.userData.requiresWheelRig = true;
  root.userData.requiresCollisionProxy = true;
}

async function assertGlbAvailable(url) {
  const response = await fetch(url, { method: 'HEAD', cache: 'no-store' });
  const contentType = response.headers.get('content-type') || '';
  if (!response.ok || contentType.includes('text/html')) {
    throw new Error(`Integra bus GLB não staged em ${url}`);
  }
}

async function loadGltf(url) {
  await assertGlbAvailable(url);
  return new Promise((resolve, reject) => {
    new GLTFLoader().load(url, resolve, undefined, reject);
  });
}

export async function createIntegraBus(segments, options = {}) {
  const segment = chooseIntegraStagingSegment(segments);
  const url = options.url || import.meta.env.VITE_INTEGRA_BUS_GLB_URL || INTEGRA_BUS.defaultUrl;
  let root;
  let sourceKind = 'proxy';
  let loadError = null;
  let stats;

  try {
    const gltf = await loadGltf(url);
    root = normalizeLoadedBus(gltf.scene);
    stats = collectMeshStats(root);
    sourceKind = 'approved_glb_candidate';
  } catch (error) {
    loadError = error instanceof Error ? error.message : String(error);
    root = createIntegraBusProxy();
    stats = collectMeshStats(root);
  }

  configureRoot(root, sourceKind, stats);
  const stagedSize = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
  root.userData.stagedDimensions = { x: stagedSize.x, y: stagedSize.y, z: stagedSize.z };
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
