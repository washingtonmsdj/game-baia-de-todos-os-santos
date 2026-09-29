import * as THREE from 'three';
import { loadRuntimeManifest, loadJsonAsset } from './runtime/assets.js';

// Índice espacial dos colisores e superfícies jogáveis da cena oficial.
// A arte é carregada exclusivamente do GLB; este módulo não cria cenário.
export async function loadGroundSurface() {
  const manifest=await loadRuntimeManifest();
  const data=await loadJsonAsset(manifest.assets.surfaces);
  if(data.coordinates !== manifest.coordinates.runtime || data.source_sha256 !== manifest.source.sha256) {
    throw new Error('Superfícies de outra revisão ou sistema de coordenadas');
  }
  const cells = new Map();
  const roadCells = new Map();
  const size = 16;
  for (const item of data.meshes) {
    const positions = item.positions;
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setIndex(item.indices);
    const p = geometry.attributes.position;
    for (let i = 0; i < item.indices.length; i += 3) {
      const v = item.indices.slice(i, i + 3).map(k => [p.getX(k), p.getY(k), p.getZ(k)]);
      const [a,b,c] = v;
      const denominator = (b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2]);
      if (Math.abs(denominator) < 1e-8) continue;
      const triangle = {v, denominator, role:item.role};
      for(let x=Math.floor(Math.min(a[0],b[0],c[0])/size);x<=Math.floor(Math.max(a[0],b[0],c[0])/size);x++) {
        for(let z=Math.floor(Math.min(a[2],b[2],c[2])/size);z<=Math.floor(Math.max(a[2],b[2],c[2])/size);z++) {
          const key=`${x},${z}`;
          if(!cells.has(key)) cells.set(key,[]);
          cells.get(key).push(triangle);
          if(item.role==='road') {
            if(!roadCells.has(key)) roadCells.set(key,[]);
            roadCells.get(key).push(triangle);
          }
        }
      }
    }
  }
  function sample(x,z,ceiling=Infinity, roadOnly=false) {
    let height=null;
    for(const {v:[a,b,c],denominator,role} of (roadOnly ? roadCells : cells).get(`${Math.floor(x/size)},${Math.floor(z/size)}`) ?? []) {
      if(roadOnly && role!=='road') continue;
      const u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/denominator;
      const v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/denominator;
      if(u < -1e-6 || v < -1e-6 || u+v > 1.000001) continue;
      const y=u*a[1]+v*b[1]+(1-u-v)*c[1];
      if(y<=ceiling && (height===null || y>height)) height=y;
    }
    return height;
  }
  return {sample,source:data.source};
}
