import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

export async function createUrbanView(scene,simulation,config) {
  const asset=await new GLTFLoader().loadAsync('/assets/vehicles/car-v14.glb');
  const group=new THREE.Group();scene.add(group);asset.scene.updateMatrixWorld(true);
  const materials=new Map();
  asset.scene.traverse(o=>{if(!o.isMesh)return;
    const geometry=(o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone()).applyMatrix4(o.matrixWorld);
    for(const name of Object.keys(geometry.attributes))if(!['position','normal','uv'].includes(name))geometry.deleteAttribute(name);
    if(!geometry.attributes.normal)geometry.computeVertexNormals();if(!geometry.attributes.uv)geometry.setAttribute('uv',new THREE.BufferAttribute(new Float32Array(geometry.attributes.position.count*2),2));
    if(Array.isArray(o.material))throw new Error('Asset de carro exige divisão por material');
    const batch=materials.get(o.material)||{material:o.material,geometries:[]};batch.geometries.push(geometry);materials.set(o.material,batch);
  });
  const batches=[...materials.values()].map(batch=>{const geometry=mergeGeometries(batch.geometries,false);if(!geometry)throw new Error('Geometrias incompatíveis no carro');const mesh=new THREE.InstancedMesh(geometry,batch.material,simulation.cars.length);mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);mesh.frustumCulled=false;group.add(mesh);return mesh;});
  const cars=simulation.cars.map(()=>new THREE.Object3D());
  const pedestrians=simulation.pedestrians.map(p=>{const o=new THREE.Group();o.name='Pedestre '+p.id;
    const clothes=new THREE.MeshStandardMaterial({color:[0x346a83,0xa34c40,0xe4be55,0x47614a,0x665581,0xddd6be][p.id]});
    const body=new THREE.Mesh(new THREE.CapsuleGeometry(.22,.52,3,6),clothes);body.position.y=1.12;o.add(body);
    const head=new THREE.Mesh(new THREE.SphereGeometry(.14,8,6),new THREE.MeshStandardMaterial({color:0xa9714f}));head.position.y=1.69;o.add(head);
    for(const sign of [-1,1]){const leg=new THREE.Mesh(new THREE.BoxGeometry(.14,.64,.17),new THREE.MeshStandardMaterial({color:0x243344}));leg.position.set(sign*.13,.4,0);o.add(leg);}
    group.add(o);return o;});
  const lamps=[];const known=new Set();
  function bindSignals() {scene.traverse(o=>{if(!o.isMesh||!o.name.startsWith('SLICE_LAMP')||known.has(o.uuid))return;const match=o.name.match(/SLICE_LAMP_(main|side|ped)_(red|amber|green)/);if(!match)return;o.material=o.material.clone();known.add(o.uuid);lamps.push({o,group:match[1],color:match[2]});});}
  let timer=0;
  function update(dt) {
    simulation.cars.forEach((car,i)=>{const o=cars[i];o.position.fromArray(car.p);o.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),new THREE.Vector3(...car.direction));o.updateMatrix();for(const mesh of batches)mesh.setMatrixAt(i,o.matrix);});
    for(const mesh of batches)mesh.instanceMatrix.needsUpdate=true;
    simulation.pedestrians.forEach((p,i)=>{const o=pedestrians[i];o.position.fromArray(p.p);const swing=Math.sin(p.walked*8)*.34;o.children[2].rotation.x=swing;o.children[3].rotation.x=-swing;});
    timer-=dt;if(timer<=0){bindSignals();timer=.5;}
    for(const {o,group,color} of lamps){const phase=simulation.phase.group;const active=color==='red'?!(phase===group||phase===group+'Amber'):color==='amber'?phase===group+'Amber':phase===group;o.material.emissive.copy(o.material.color);o.material.emissiveIntensity=active?3:.025;}
  }
  return {group,update,cars,pedestrians,lamps};
}
