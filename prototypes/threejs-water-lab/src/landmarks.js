import * as THREE from 'three';
import { WATER_LEVEL, sampleWaterHeight, sampleWaterNormal } from './water.js';

export function createFortProxy() {
  const group = new THREE.Group();
  const stone = new THREE.MeshStandardMaterial({ color: 0xc7b79e, roughness: 0.88 });
  const drum = new THREE.Mesh(new THREE.CylinderGeometry(17, 20, 6.5, 64), stone);
  drum.position.y = 3.1;
  drum.castShadow = true;
  drum.receiveShadow = true;
  group.add(drum);

  const tower = new THREE.Mesh(new THREE.CylinderGeometry(6.5, 7.8, 9.5, 48), stone);
  tower.position.y = 10.8;
  tower.castShadow = true;
  group.add(tower);

  const roof = new THREE.Mesh(
    new THREE.CylinderGeometry(7.2, 7.2, 0.9, 48),
    new THREE.MeshStandardMaterial({ color: 0x8c6b55, roughness: 0.9 }),
  );
  roof.position.y = 15.5;
  roof.castShadow = true;
  group.add(roof);

  group.position.set(-570, WATER_LEVEL - 1.3, 95);
  group.name = 'Forte São Marcelo | proxy de escala';
  return group;
}

export function createBoatProxy() {
  const boat = new THREE.Group();
  const hull = new THREE.Mesh(
    new THREE.BoxGeometry(7.2, 1.2, 2.5),
    new THREE.MeshStandardMaterial({ color: 0x48271c, roughness: 0.68 }),
  );
  hull.castShadow = true;
  boat.add(hull);

  const cabin = new THREE.Mesh(
    new THREE.BoxGeometry(2.4, 1.6, 1.7),
    new THREE.MeshStandardMaterial({ color: 0xe4dfd4, roughness: 0.5 }),
  );
  cabin.position.set(-0.7, 1.25, 0);
  cabin.castShadow = true;
  boat.add(cabin);
  boat.position.set(-470, WATER_LEVEL + 0.7, -60);
  boat.name = 'Boat Buoyancy Proxy';

  const normal = new THREE.Vector3();
  const up = new THREE.Vector3(0, 1, 0);
  const targetQuaternion = new THREE.Quaternion();
  return {
    object: boat,
    update(time) {
      boat.position.z = -60 + Math.sin(time * 0.08) * 35;
      boat.position.x = -470 + Math.sin(time * 0.045) * 18;
      const y = sampleWaterHeight(boat.position.x, boat.position.z, time);
      boat.position.y = y + 0.62;
      sampleWaterNormal(boat.position.x, boat.position.z, time, normal);
      targetQuaternion.setFromUnitVectors(up, normal);
      boat.quaternion.slerp(targetQuaternion, 0.08);
    },
  };
}
