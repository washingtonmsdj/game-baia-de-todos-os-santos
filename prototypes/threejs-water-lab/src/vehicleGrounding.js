import * as THREE from 'three';
import { sampleRoadSurface, sampleGameplayGround } from './terrain.js';

// Pontos inferiores dos pneus medidos no próprio asset, em metros locais.
export function measureWheelContacts(root) {
  root.updateMatrixWorld(true);
  const inverse = root.matrixWorld.clone().invert();
  const contacts = [];
  root.traverse(object => {
    if (!object.isMesh || !/pneu/i.test(object.name)) return;
    const geometry = object.geometry.clone();
    geometry.applyMatrix4(inverse.clone().multiply(object.matrixWorld));
    geometry.computeBoundingBox();
    const box = geometry.boundingBox;
    contacts.push(new THREE.Vector3((box.min.x+box.max.x)/2, box.min.y, (box.min.z+box.max.z)/2));
    geometry.dispose();
  });
  if (contacts.length < 4) throw new Error('Pneus ausentes para apoiar o ônibus');
  return contacts;
}

export function groundVehicle(position, quaternion, heading, contacts) {
  const forward = new THREE.Vector3(heading.x,0,heading.z).normalize();
  const right = new THREE.Vector3(forward.z,0,-forward.x);
  quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(right,new THREE.Vector3(0,1,0),forward));
  // Reavalia as posições dos pneus após inclinar a carroceria.
  for (let iteration=0; iteration<3; iteration++) {
    const samples = contacts.map(local => {
      const rotated = local.clone().applyQuaternion(quaternion);
      const x=position.x+rotated.x, z=position.z+rotated.z;
      const center=sampleRoadSurface(position.x,position.z);
      const y = sampleRoadSurface(x,z) ?? (center==null ? null : sampleGameplayGround(x,z,center+1));
      return {local,rotated,y};
    });
    if (samples.some(s=>s.y==null)) return false;
    const avg = predicate => {
      const list=samples.filter(predicate);
      return list.reduce((sum,s)=>sum+s.y,0)/list.length;
    };
    const zmin=Math.min(...contacts.map(p=>p.z)), zmax=Math.max(...contacts.map(p=>p.z));
    const xmin=Math.min(...contacts.map(p=>p.x)), xmax=Math.max(...contacts.map(p=>p.x));
    const mid=(zmin+zmax)/2;
    const longitudinalProjection = Math.max(0.1, new THREE.Vector3(0,0,1).applyQuaternion(quaternion).dot(forward));
    const lateralProjection = Math.max(0.1, new THREE.Vector3(1,0,0).applyQuaternion(quaternion).dot(right));
    const pitch=(avg(s=>s.local.z>mid)-avg(s=>s.local.z<=mid))/((zmax-zmin)*longitudinalProjection);
    const roll=(avg(s=>s.local.x>0)-avg(s=>s.local.x<0))/((xmax-xmin)*lateralProjection);
    const f=forward.clone().add(new THREE.Vector3(0,pitch,0)).normalize();
    const r=right.clone().add(new THREE.Vector3(0,roll,0));
    const up=new THREE.Vector3().crossVectors(f,r).normalize();
    r.crossVectors(up,f).normalize();
    quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(r,up,f));
    position.y=samples.reduce((sum,s)=>sum+s.y-s.local.clone().applyQuaternion(quaternion).y,0)/samples.length;
  }
  return true;
}
