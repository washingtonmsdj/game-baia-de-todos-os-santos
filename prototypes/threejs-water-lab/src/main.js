import * as THREE from 'three';
import { Sky } from 'three/addons/objects/Sky.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import './styles.css';
import { WATER_LEVEL, createWaterMesh, sampleWaterHeight, sampleWaterNormal } from './water.js';

const app = document.querySelector('#app');
const status = document.querySelector('#status');
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0xb8cfdb, 0.0018);

const camera = new THREE.PerspectiveCamera(64, innerWidth / innerHeight, 0.08, 1600);
camera.position.set(26, 5.4, 26);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);

const clock = new THREE.Clock();
const controls = new PointerLockControls(camera, renderer.domElement);
renderer.domElement.addEventListener('click', () => controls.lock());

const sky = new Sky();
sky.scale.setScalar(900);
scene.add(sky);
const skyU = sky.material.uniforms;
skyU.turbidity.value = 7.5;
skyU.rayleigh.value = 1.45;
skyU.mieCoefficient.value = 0.0045;
skyU.mieDirectionalG.value = 0.81;
const sun = new THREE.Vector3().setFromSphericalCoords(1, THREE.MathUtils.degToRad(48), THREE.MathUtils.degToRad(230));
skyU.sunPosition.value.copy(sun);

const hemi = new THREE.HemisphereLight(0xd9edff, 0x16363a, 2.5);
scene.add(hemi);
const key = new THREE.DirectionalLight(0xfff0cf, 4.2);
key.position.copy(sun).multiplyScalar(120);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.left = -110;
key.shadow.camera.right = 110;
key.shadow.camera.top = 110;
key.shadow.camera.bottom = -110;
scene.add(key);

const water = createWaterMesh();
scene.add(water);

const seabed = new THREE.Mesh(
  new THREE.PlaneGeometry(420, 420),
  new THREE.MeshStandardMaterial({ color: 0x285d5a, roughness: 0.96, metalness: 0.0 })
);
seabed.rotation.x = -Math.PI / 2;
seabed.position.y = -8.0;
seabed.receiveShadow = true;
scene.add(seabed);

const landMat = new THREE.MeshStandardMaterial({ color: 0x8e8070, roughness: 0.95 });
const land = new THREE.Mesh(new THREE.BoxGeometry(125, 9, 300), landMat);
land.position.set(-78, -3.9, 0);
land.receiveShadow = true;
land.castShadow = true;
scene.add(land);

const quayMat = new THREE.MeshStandardMaterial({ color: 0xa7a29a, roughness: 0.82 });
const quay = new THREE.Mesh(new THREE.BoxGeometry(10, 1.2, 280), quayMat);
quay.position.set(-11, -0.2, 0);
quay.receiveShadow = true;
quay.castShadow = true;
scene.add(quay);

let seed = 7421;
function random() {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296;
}
const city = new THREE.Group();
const cityMat = new THREE.MeshStandardMaterial({ color: 0xbba890, roughness: 0.88 });
for (let i = 0; i < 95; i++) {
  const w = 3 + random() * 7;
  const d = 4 + random() * 10;
  const h = 4 + Math.pow(random(), 1.6) * 25;
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), cityMat);
  mesh.position.set(-16 - random() * 100, h * 0.5 + 0.6, -135 + random() * 270);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  city.add(mesh);
}
scene.add(city);

const fort = new THREE.Group();
const fortMat = new THREE.MeshStandardMaterial({ color: 0xc5b49a, roughness: 0.86 });
const drum = new THREE.Mesh(new THREE.CylinderGeometry(11, 13, 5.5, 48), fortMat);
drum.position.y = 2.7;
drum.castShadow = true;
drum.receiveShadow = true;
fort.add(drum);
const tower = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 5.5, 7, 32), fortMat);
tower.position.y = 8.7;
tower.castShadow = true;
fort.add(tower);
fort.position.set(54, WATER_LEVEL - 0.7, 18);
scene.add(fort);

const boat = new THREE.Group();
const hull = new THREE.Mesh(
  new THREE.BoxGeometry(5.6, 1.1, 2.0),
  new THREE.MeshStandardMaterial({ color: 0x4a2418, roughness: 0.68 })
);
hull.castShadow = true;
boat.add(hull);
const cabin = new THREE.Mesh(
  new THREE.BoxGeometry(1.8, 1.3, 1.45),
  new THREE.MeshStandardMaterial({ color: 0xe7e1d4, roughness: 0.5 })
);
cabin.position.set(-0.5, 1.0, 0);
cabin.castShadow = true;
boat.add(cabin);
boat.position.set(34, WATER_LEVEL + 0.6, -22);
scene.add(boat);

const particleGeo = new THREE.BufferGeometry();
const particlePos = new Float32Array(900 * 3);
for (let i = 0; i < 900; i++) {
  particlePos[i * 3] = -20 + random() * 180;
  particlePos[i * 3 + 1] = -7.4 + random() * 7.2;
  particlePos[i * 3 + 2] = -145 + random() * 290;
}
particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePos, 3));

const particles = new THREE.Points(
  particleGeo,
  new THREE.PointsMaterial({ color: 0xb7e5e7, size: 0.035, transparent: true, opacity: 0.4, depthWrite: false })
);
scene.add(particles);

const keys = new Set();
addEventListener('keydown', (event) => {
  keys.add(event.code);
  if (event.code === 'KeyR') {
    camera.position.set(26, 5.4, 26);
    camera.rotation.set(0, 0, 0);
  }
});
addEventListener('keyup', (event) => keys.delete(event.code));

const move = new THREE.Vector3();
const forward = new THREE.Vector3();
const right = new THREE.Vector3();
const up = new THREE.Vector3(0, 1, 0);
const waterNormal = new THREE.Vector3();
const boatUp = new THREE.Vector3(0, 1, 0);
const boatQuat = new THREE.Quaternion();

function updateMovement(dt, underwater) {
  camera.getWorldDirection(forward);
  forward.y = 0;
  forward.normalize();
  right.crossVectors(forward, up).normalize();
  move.set(0, 0, 0);
  if (keys.has('KeyW')) move.add(forward);
  if (keys.has('KeyS')) move.sub(forward);
  if (keys.has('KeyD')) move.add(right);
  if (keys.has('KeyA')) move.sub(right);
  if (keys.has('KeyE')) move.y += 1;
  if (keys.has('KeyQ')) move.y -= 1;
  if (move.lengthSq() > 0) move.normalize();
  const boost = keys.has('ShiftLeft') || keys.has('ShiftRight');
  const speed = underwater ? (boost ? 11 : 5.2) : (boost ? 24 : 9.5);
  camera.position.addScaledVector(move, speed * dt);
}

function updateBoat(time) {
  const y = sampleWaterHeight(boat.position.x, boat.position.z, time);
  boat.position.y = y + 0.55;
  sampleWaterNormal(boat.position.x, boat.position.z, time, waterNormal);
  boatQuat.setFromUnitVectors(boatUp, waterNormal);
  boat.quaternion.slerp(boatQuat, 0.08);
}

function updateEnvironment(underwater, depth) {
  if (underwater) {
    scene.fog.color.set(0x0c5265);
    scene.fog.density = 0.055;
    renderer.toneMappingExposure = 0.72;
    sky.visible = false;
    status.textContent = `MERGULHO · ${depth.toFixed(1)} m`;
  } else {
    scene.fog.color.set(0xb8cfdb);
    scene.fog.density = 0.0018;
    renderer.toneMappingExposure = 1.08;
    sky.visible = true;
    status.textContent = 'SUPERFÍCIE';
  }
}

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;
  water.material.uniforms.uTime.value = time;
  const surface = sampleWaterHeight(camera.position.x, camera.position.z, time);
  const underwater = camera.position.y < surface - 0.08;
  updateMovement(dt, underwater);
  const newSurface = sampleWaterHeight(camera.position.x, camera.position.z, time);
  updateEnvironment(camera.position.y < newSurface - 0.08, Math.max(0, newSurface - camera.position.y));
  updateBoat(time);
  particles.rotation.y = time * 0.006;
  renderer.render(scene, camera);
}

camera.lookAt(new THREE.Vector3(-18, 2, 0));
animate();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
});
