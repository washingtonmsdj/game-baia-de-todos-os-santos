import * as THREE from 'three';
import { Sky } from 'three/addons/objects/Sky.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import './styles.css';
import { createWaterMesh } from './water.js';
import { createTerrainMesh, createCoastlineGuide, configureTerrain } from './terrain.js';
import { loadFoundationData } from './foundationData.js';
import {
  loadRoadGraph,
  buildRoadSegments,
  createRoadSurface,
  createRoadDebugLines,
  buildTrafficArcs,
  roadGraphStats,
} from './roadGraph.js';
import { TrafficSystem } from './traffic.js';
import { createUrbanMassing } from './urban.js';
import { PlayerController, PlayerMode } from './player.js';
import { createFortProxy, createBoatProxy } from './landmarks.js';
import { createOfficialLandmarks } from './officialLandmarks.js';
import { loadOfficialCity } from './officialCity.js';
import { createIntegraBus, integraBusStatus } from './integraBus.js';

const app = document.querySelector('#app');
const loading = document.querySelector('#loading');
const status = document.querySelector('#status');
const coords = document.querySelector('#coords');
const worldStats = document.querySelector('#world-stats');
const busStatusLabel = document.querySelector('#bus-status');
const fpsLabel = document.querySelector('#fps');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xc8dbe6);
scene.fog = new THREE.FogExp2(0xb8cfdb, 0.00125);

const camera = new THREE.PerspectiveCamera(64, innerWidth / innerHeight, 0.08, 3200);
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.65));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.02;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);
const sky = new Sky();
sky.scale.setScalar(2600);
scene.add(sky);
const skyUniforms = sky.material.uniforms;
skyUniforms.turbidity.value = 7.4;
skyUniforms.rayleigh.value = 1.5;
skyUniforms.mieCoefficient.value = 0.0045;
skyUniforms.mieDirectionalG.value = 0.81;
const sunDirection = new THREE.Vector3().setFromSphericalCoords(
  1,
  THREE.MathUtils.degToRad(49),
  THREE.MathUtils.degToRad(230),
).normalize();
skyUniforms.sunPosition.value.copy(sunDirection);

const hemi = new THREE.HemisphereLight(0xd9edff, 0x203632, 2.35);
scene.add(hemi);
const key = new THREE.DirectionalLight(0xfff0cf, 4.0);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.left = -180;
key.shadow.camera.right = 180;
key.shadow.camera.top = 180;
key.shadow.camera.bottom = -180;
key.shadow.camera.near = 1;
key.shadow.camera.far = 700;
scene.add(key);
scene.add(key.target);

const foundation = await loadFoundationData();
configureTerrain(foundation);

const terrain = createTerrainMesh();
scene.add(terrain);
const coastlineGuide = createCoastlineGuide();
scene.add(coastlineGuide);
const water = createWaterMesh();
scene.add(water);

const fort = createFortProxy();
scene.add(fort);
let officialCity;
let officialLandmarks;
try {
  officialCity = await loadOfficialCity();
  scene.add(officialCity.object);
  officialLandmarks = officialCity.object;
} catch (error) {
  console.warn('Cidade oficial GLB indisponível; usando marcos de fallback', error);
  officialLandmarks = createOfficialLandmarks();
  scene.add(officialLandmarks);
}
const boat = createBoatProxy();
scene.add(boat.object);
let graph;
let segments;
let trafficGraph;
let traffic;
let debugRoads;
let urban;
let graphStats;
let integraBus;

try {
  graph = await loadRoadGraph();
  segments = buildRoadSegments(graph);
  const roads = createRoadSurface(segments);
  scene.add(roads.sidewalk, roads.road);
  debugRoads = createRoadDebugLines(segments);
  scene.add(debugRoads);

  trafficGraph = buildTrafficArcs(graph, segments);
  traffic = new TrafficSystem(trafficGraph);
  scene.add(traffic.mesh);

  urban = createUrbanMassing(segments, 320, foundation);
  scene.add(urban.mesh);
  graphStats = roadGraphStats(graph, segments, trafficGraph);
  integraBus = await createIntegraBus(segments);
  scene.add(integraBus.object);
  if (integraBus.loadError) console.info('Integra bus: usando proxy de staging', integraBus.loadError);
  loading.classList.add('hidden');
} catch (error) {
  console.error(error);
  loading.textContent = `ERRO AO CARREGAR FUNDAÇÃO: ${error.message}`;
  throw error;
}

const controls = new PointerLockControls(camera, renderer.domElement);
renderer.domElement.addEventListener('click', () => controls.lock());
const player = new PlayerController(camera, controls, urban.colliders);

addEventListener('keydown', (event) => {
  if (event.code === 'KeyG' && debugRoads) debugRoads.visible = !debugRoads.visible;
  if (event.code === 'KeyT' && traffic) traffic.setVisible(!traffic.enabled);
  if (event.code === 'KeyB' && integraBus) integraBus.object.visible = !integraBus.object.visible;
});
const clock = new THREE.Clock();
window.__ALL_SAINTS__ = {
  version: 'R30A.13-official-mvp-city+torino-31065',
  camera,
  player,
  traffic,
  boat: boat.object,
  boatController: boat,
  officialLandmarks,
  officialCity,
  integraBus,
  graphStats,
  foundationStats: foundation.stats,
  teleport(x, z, y = null) {
    camera.position.x = Number(x);
    camera.position.z = Number(z);
    if (y !== null) camera.position.y = Number(y);
    player.verticalVelocity = 0;
  },
  reset() { player.reset(); },
  snapshot() {
    const t = traffic.getStats();
    return {
      mode: player.mode,
      position: camera.position.toArray(),
      traffic: t,
      graph: graphStats,
      buildings: urban.stats.buildings,
      foundation: foundation.stats,
      integraBus: integraBusStatus(integraBus),
      officialLandmarks: officialLandmarks.userData,
    };
  },
};
let smoothedFps = 60;
let telemetryTimer = 0;

function updateEnvironment(state, dt) {
  const diving = state.mode === PlayerMode.DIVING;
  if (diving) {
    scene.fog.color.set(0x0c5265);
    scene.fog.density = 0.026 + Math.min(0.026, state.depth * 0.0022);
    renderer.toneMappingExposure = THREE.MathUtils.damp(renderer.toneMappingExposure, 0.68, 3.5, dt);
    sky.visible = false;
    hemi.intensity = 0.75;
    status.textContent = `MERGULHO · ${state.depth.toFixed(1)} m`;
  } else {
    scene.fog.color.set(0xb8cfdb);
    scene.fog.density = 0.00125;
    renderer.toneMappingExposure = THREE.MathUtils.damp(renderer.toneMappingExposure, 1.02, 3.5, dt);
    sky.visible = true;
    hemi.intensity = 2.35;
    status.textContent = state.mode === PlayerMode.SWIMMING ? 'NADANDO' : 'A PÉ';
  }
}

function updateSunRig() {
  key.position.copy(camera.position).addScaledVector(sunDirection, 320);
  key.position.y += 160;
  key.target.position.copy(camera.position);
  key.target.position.y -= 20;
  key.target.updateMatrixWorld();
}

function updateTelemetry(state, dt) {
  const p = state.position;
  coords.textContent = `x ${p.x.toFixed(1)} · y ${p.y.toFixed(1)} · z ${p.z.toFixed(1)}`;
  smoothedFps = THREE.MathUtils.lerp(smoothedFps, 1 / Math.max(dt, 0.0001), 0.08);
  telemetryTimer -= dt;
  if (telemetryTimer > 0) return;
  telemetryTimer = 0.35;
  const trafficStats = traffic.getStats();
  worldStats.textContent = `${graphStats.nodes} nós · ${graphStats.edges} segmentos · ${trafficStats.vehicles} veículos · ${trafficStats.averageSpeedKmh.toFixed(0)} km/h méd.`;
  const busState = integraBusStatus(integraBus);
  const busSource = busState.loadedApprovedGlb ? 'GLB AUTORIA' : 'PROXY';
  const busVisibility = integraBus.object.visible ? 'visível' : 'oculto';
  busStatusLabel.textContent = `ônibus ${busSource} · ${busVisibility} · B alterna`;
  fpsLabel.textContent = `${smoothedFps.toFixed(0)} FPS · ${urban.stats.buildings} volumes urbanos`;
}
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;
  water.material.uniforms.uTime.value = time;
  const state = player.update(dt, time);
  traffic.update(dt);
  boat.update(time);
  updateEnvironment(state, dt);
  updateSunRig();
  updateTelemetry(state, dt);
  renderer.render(scene, camera);
}

animate();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.65));
});

