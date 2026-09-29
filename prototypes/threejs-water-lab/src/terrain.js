import { WORLD } from './worldConfig.js';
let officialGround = null;
let coastlineSamples = [];
export function configureGroundSurface(surface) { officialGround = surface; }
export function configureTerrain(data) {
  coastlineSamples = (data?.city?.coastline ?? [])
    .flatMap(item=>item.points ?? [])
    .filter(point=>Array.isArray(point) && point.length>=2)
    .map(([x,y])=>({x:Number(x),z:-Number(y)})).sort((a,b)=>a.z-b.z);
}
export function coastlineX(z) {
  if (!coastlineSamples.length) return -Infinity;
  if(z<=coastlineSamples[0].z) return coastlineSamples[0].x;
  const last=coastlineSamples[coastlineSamples.length-1];
  if(z>=last.z) return last.x;
  let lo=0,hi=coastlineSamples.length-1;
  while(hi-lo>1) { const mid=(lo+hi)>>1; if(coastlineSamples[mid].z<=z) lo=mid; else hi=mid; }
  const a=coastlineSamples[lo],b=coastlineSamples[hi];
  return a.x+(b.x-a.x)*(z-a.z)/Math.max(0.001,b.z-a.z);
}
export function isWaterAt(x,z) { return x<coastlineX(z); }
export function sampleTerrainHeight(x,z) { return officialGround?.sample(x,z) ?? null; }
export function sampleGameplayGround(x,z,ceiling=Infinity) { return officialGround?.sample(x,z,ceiling) ?? null; }
export function sampleRoadSurface(x,z) { return officialGround?.sample(x,z,Infinity,true) ?? null; }
export function sampleRoadHeight(x,z) { return sampleRoadSurface(x,z) ?? sampleTerrainHeight(x,z); }
export function terrainSourceAt() { return officialGround?.source ?? 'pending'; }
export const WORLD_BOUNDS=Object.freeze({
  minX:Math.min(WORLD.cityBounds.minX,WORLD.oceanBounds.minX),
  maxX:Math.max(WORLD.cityBounds.maxX,WORLD.oceanBounds.maxX),
  minZ:Math.min(WORLD.cityBounds.minZ,WORLD.oceanBounds.minZ),
  maxZ:Math.max(WORLD.cityBounds.maxZ,WORLD.oceanBounds.maxZ),
});
