import * as THREE from 'three';
import { loadRuntimeManifest } from './runtime/assets.js';
import { StreamingCity } from './runtime/streamingCity.js';
export async function loadOfficialCity({onProgress}={}) {
  const manifest=await loadRuntimeManifest();
  const controller=new StreamingCity(manifest,onProgress);
  const spawn=manifest.settings.world.spawn;
  await controller.initialize(new THREE.Vector3(spawn.x,0,spawn.z));
  return {object:controller.object,controller,manifest};
}
