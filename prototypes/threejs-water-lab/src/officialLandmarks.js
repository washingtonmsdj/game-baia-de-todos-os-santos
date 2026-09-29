import * as THREE from 'three';
import { sampleTerrainHeight } from './terrain.js';

const MATERIALS = Object.freeze({
  stone: new THREE.MeshStandardMaterial({ color: 0xd8c8a7, roughness: 0.82 }),
  plaster: new THREE.MeshStandardMaterial({ color: 0xe6dfcf, roughness: 0.76 }),
  trim: new THREE.MeshStandardMaterial({ color: 0x8a6848, roughness: 0.72 }),
  roof: new THREE.MeshStandardMaterial({ color: 0x9b5532, roughness: 0.86 }),
  glass: new THREE.MeshStandardMaterial({ color: 0x25414d, roughness: 0.24, metalness: 0.05 }),
  shadow: new THREE.MeshStandardMaterial({ color: 0x273039, roughness: 0.9 }),
});

function box(group, name, size, position, material, radius = 0) {
  const geometry = new THREE.BoxGeometry(...size);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = name;
  mesh.position.set(...position);
  if (radius) {
    const bevel = new THREE.Mesh(geometry, material);
    bevel.visible = false;
  }
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  group.add(mesh);
  return mesh;
}

function cylinder(group, name, radius, height, position, material, radialSegments = 16) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, height, radialSegments), material);
  mesh.name = name;
  mesh.position.set(...position);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  group.add(mesh);
  return mesh;
}

function label(text, color = '#fff1c4') {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 96;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = 'bold 38px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillStyle = 'rgba(17, 26, 32, .82)';
  ctx.fillRect(8, 8, 496, 80);
  ctx.fillStyle = color;
  ctx.fillText(text, 256, 58);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    map: new THREE.CanvasTexture(canvas),
    transparent: true,
    depthTest: false,
  }));
  sprite.scale.set(18, 3.4, 1);
  sprite.renderOrder = 20;
  return sprite;
}

function place(group, x, z, yOffset = 0) {
  group.position.set(x, sampleTerrainHeight(x, z) + yOffset, z);
}

function createElevadorLacerda() {
  const group = new THREE.Group();
  group.name = 'HERO | Elevador Lacerda | oficial MVP';
  const tower = (x) => {
    box(group, 'Torre Elevador', [12, 54, 18], [x, 27, 0], MATERIALS.plaster);
    box(group, 'Faixa vertical', [1.2, 52, 18.4], [x - 5.9, 27, 0], MATERIALS.trim);
    box(group, 'Faixa vertical', [1.2, 52, 18.4], [x + 5.9, 27, 0], MATERIALS.trim);
    for (let y = 9; y < 48; y += 8) box(group, 'Janela torre', [8, 2.4, 18.5], [x, y, 0], MATERIALS.glass);
  };
  tower(-7.5);
  tower(7.5);
  box(group, 'Passarela superior', [28, 5, 22], [0, 52, 0], MATERIALS.stone);
  box(group, 'Passarela baixa', [25, 4, 15], [0, 8, 0], MATERIALS.stone);
  box(group, 'Galeria central', [10, 41, 13], [0, 28, 0], MATERIALS.shadow);
  box(group, 'Cobertura superior', [31, 2, 24], [0, 55.5, 0], MATERIALS.trim);
  const sign = label('ELEVADOR LACERDA');
  sign.position.set(0, 58, 0);
  group.add(sign);
  place(group, -20, 24);
  group.userData = { locationId: 'elevador-lacerda', source: 'official MVP landmark proxy', fidelity: 'blockout' };
  return group;
}

function createMercadoModelo() {
  const group = new THREE.Group();
  group.name = 'HERO | Mercado Modelo | oficial MVP';
  box(group, 'Corpo Mercado Modelo', [64, 10, 64], [0, 5, 0], MATERIALS.plaster);
  box(group, 'Telhado Mercado Modelo', [68, 5, 68], [0, 12, 0], MATERIALS.roof);
  box(group, 'Cornija Mercado Modelo', [70, 1.2, 70], [0, 15.2, 0], MATERIALS.trim);
  box(group, 'Entrada Mercado Modelo', [18, 8, 1.2], [0, 7, 32.4], MATERIALS.trim);
  for (const x of [-27, -18, -9, 9, 18, 27]) {
    box(group, 'Janela Mercado Modelo', [5.2, 4.4, 1], [x, 7.5, 32.8], MATERIALS.glass);
    box(group, 'Janela Mercado Modelo', [5.2, 4.4, 1], [x, 7.5, -32.8], MATERIALS.glass);
  }
  for (const [x, z] of [[-27, -27], [27, -27], [-27, 27], [27, 27]]) {
    cylinder(group, 'Torreão Mercado Modelo', 4.5, 20, [x, 18, z], MATERIALS.plaster, 20);
    cylinder(group, 'Coroamento torreão', 5.1, 1.3, [x, 28.2, z], MATERIALS.roof, 20);
  }
  const sign = label('MERCADO MODELO');
  sign.position.set(0, 30, 0);
  group.add(sign);
  place(group, -130, 190, 0);
  group.userData = { locationId: 'mercado-modelo', osmId: 'way:59392558', source: 'official OSM footprint + MVP hero proxy' };
  return group;
}

function createPrefeitura() {
  const group = new THREE.Group();
  group.name = 'HERO | Prefeitura / Palácio Rio Branco | oficial MVP';
  box(group, 'Palácio Rio Branco', [34, 14, 22], [0, 7, 0], MATERIALS.plaster);
  box(group, 'Ala central Palácio', [15, 21, 13], [0, 17, 0], MATERIALS.plaster);
  box(group, 'Telhado Palácio', [38, 3, 25], [0, 24, 0], MATERIALS.roof);
  box(group, 'Pórtico Prefeitura', [20, 5, 2], [0, 3, 11.5], MATERIALS.trim);
  for (const x of [-12, -6, 6, 12]) {
    cylinder(group, 'Coluna Prefeitura', 0.75, 8, [x, 8, 12], MATERIALS.stone, 12);
    box(group, 'Janela Prefeitura', [3.2, 4.2, 0.8], [x, 13, 11.3], MATERIALS.glass);
  }
  const sign = label('PREFEITURA · PALÁCIO RIO BRANCO');
  sign.position.set(0, 29, 0);
  group.add(sign);
  place(group, -12, -54);
  group.userData = { locationId: 'palacio-rio-branco', osmId: 'way:402383814', source: 'official OSM footprint + MVP hero proxy' };
  return group;
}

export function createOfficialLandmarks() {
  const group = new THREE.Group();
  group.name = 'OFFICIAL MVP | Salvador | Hero landmarks';
  group.add(createElevadorLacerda(), createMercadoModelo(), createPrefeitura());
  group.userData = {
    areaId: 'mvp-centro-lacerda',
    status: 'official-city-hero-proxies',
    locations: ['elevador-lacerda', 'mercado-modelo', 'palacio-rio-branco'],
  };
  return group;
}
