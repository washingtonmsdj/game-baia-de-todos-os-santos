import * as THREE from 'three';
import { loadGlbAsset, disposeScene } from './assets.js';

function distanceToBounds(position,bounds) {
  const dx=Math.max(bounds[0][0]-position.x,0,position.x-bounds[1][0]);
  const dz=Math.max(bounds[0][2]-position.z,0,position.z-bounds[1][2]);
  return Math.hypot(dx,dz);
}

export class StreamingCity {
  constructor(manifest,onProgress=()=>{}) {
    this.manifest=manifest;
    this.object=new THREE.Group();
    this.object.name='Cidade oficial | setores de runtime';
    this.object.userData={sourceFile:manifest.source.file,sourceSha256:manifest.source.sha256,
      sourceKind:'official_blender_sector_package',release:manifest.release,coordinateMapping:manifest.coordinates.runtime};
    this.options=manifest.settings.streaming;
    this.loaded=new Map(); this.pending=new Map(); this.errors=new Map();
    this.desired=new Set(); this.active=0; this.disposed=false;
    this.onProgress=onProgress;
    this.position=new THREE.Vector3();
    this.overview=false;
  }
  async initialize(position) {
    this.setInterest(position,false);
    const essential=this.manifest.sectors.filter(s=>this.desired.has(s.id));
    // Duas cargas no máximo, inclusive na inicialização.
    let cursor=0;
    await Promise.all(Array.from({length:this.options.concurrency},async()=>{
      while(cursor<essential.length) await this.load(essential[cursor++]);
    }));
  }
  async load(entry) {
    if(this.loaded.has(entry.id)) return;
    if(this.pending.has(entry.id)) return this.pending.get(entry.id);
    const work=(async()=>{
      this.active++;
      try {
        const gltf=await loadGlbAsset(entry);
        if(this.disposed || !this.desired.has(entry.id)) { disposeScene(gltf.scene); return; }
        gltf.scene.traverse(object=>{
          if(!object.isMesh) return;
          object.castShadow=true; object.receiveShadow=true;
          // Mantém sidedness e materiais definidos no Blender.
        });
        gltf.scene.name=entry.id;
        this.object.add(gltf.scene);
        this.loaded.set(entry.id,gltf.scene);
        this.errors.delete(entry.id);
      } catch(error) {
        this.errors.set(entry.id,error.message);
        throw error;
      } finally {
        this.active--;
        this.pending.delete(entry.id);
        this.onProgress(this.getStats());
      }
    })();
    this.pending.set(entry.id,work);
    return work;
  }
  setInterest(position,overview) {
    this.position.copy(position); this.overview=overview;
    this.desired=new Set(this.manifest.sectors.filter(s=>s.always_loaded || overview ||
      distanceToBounds(position,s.bounds)<=this.options.load_radius_m).map(s=>s.id));
  }
  update(position,overview=false) {
    this.setInterest(position,overview);
    for(const entry of this.manifest.sectors) {
      if(!entry.always_loaded && !overview && this.loaded.has(entry.id) &&
         distanceToBounds(position,entry.bounds)>this.options.unload_radius_m) {
        disposeScene(this.loaded.get(entry.id)); this.loaded.delete(entry.id);
      }
    }
    const queue=this.manifest.sectors.filter(s=>this.desired.has(s.id) && !this.loaded.has(s.id) &&
      !this.pending.has(s.id) && !this.errors.has(s.id))
      .sort((a,b)=>distanceToBounds(position,a.bounds)-distanceToBounds(position,b.bounds));
    for(const entry of queue.slice(0,Math.max(0,this.options.concurrency-this.active))) {
      this.load(entry).catch(error=>console.error('Falha de setor oficial:',entry.id,error));
    }
    this.onProgress(this.getStats());
  }
  isReadyAt(position) {
    return this.manifest.sectors.filter(s=>s.always_loaded || distanceToBounds(position,s.bounds)===0)
      .every(s=>this.loaded.has(s.id));
  }
  getStats() { return {loaded:this.loaded.size,total:this.manifest.sectors.length,pending:this.active,errors:[...this.errors.entries()]}; }
  dispose() { this.disposed=true; for(const scene of this.loaded.values()) disposeScene(scene); this.loaded.clear(); }
}
