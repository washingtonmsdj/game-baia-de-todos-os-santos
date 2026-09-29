import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { WORLD } from '../src/worldConfig.js';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const graph = JSON.parse(await readFile(resolve(root, 'public/data/road_graph.json'), 'utf8'));
const water = JSON.parse(await readFile(resolve(root, 'public/data/water_runtime_contract.json'), 'utf8'));
const foundation = JSON.parse(await readFile(resolve(root, 'public/data/foundation_runtime.json'), 'utf8'));
const integraBus = JSON.parse(await readFile(resolve(root, 'public/data/integra_bus_asset.json'), 'utf8')); 

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(graph.schema, 'road graph schema missing');
assert(graph.nodes.length >= 600, 'road graph unexpectedly small');
assert(graph.edges.length >= 700, 'road edge set unexpectedly small');
assert(graph.ways.length >= 150, 'road way set unexpectedly small');

const nodes = new Set(graph.nodes.map((node) => String(node.id)));
const ways = new Set(graph.ways.map((way) => Number(way.osm_way_id)));
let brokenEdges = 0;
let directedArcs = 0;
for (const edge of graph.edges) {
  if (!nodes.has(String(edge.from)) || !nodes.has(String(edge.to))) brokenEdges++;
  if (!ways.has(Number(edge.osm_way_id))) brokenEdges++;
  if (edge.access !== 'restricted') directedArcs += edge.direction === 'both' ? 2 : 1;
}
assert(brokenEdges === 0, `road graph has ${brokenEdges} broken references`);
assert(directedArcs > graph.edges.length, 'traffic graph lacks bidirectional arcs');
assert(water.gameplay.swimmable === true, 'water must remain swimmable');
assert(water.gameplay.diveable === true, 'water must remain diveable');
assert(water.gameplay.boats_supported === true, 'water must support boats');
assert(water.gameplay.runtime_surface_query_required === true, 'runtime water query contract missing');
assert(water.gameplay.runtime_buoyancy_required === true, 'runtime buoyancy contract missing');
assert(WORLD.waterLevel === water.water_level_m, 'prototype water level drifted from authored contract');
assert(WORLD.traffic.vehicles >= 40, 'traffic lab should exercise a meaningful agent count');
assert(foundation.schema === 'bay-of-all-saints/foundation-runtime-v1', 'foundation runtime schema mismatch');
assert(foundation.coordinate_space === 'blender_world_meters', 'foundation coordinate space mismatch');
assert(foundation.city.buildings.length >= 1000, 'foundation building set unexpectedly small');
assert(foundation.terrain.grid.heights.length === foundation.terrain.grid.nx * foundation.terrain.grid.nz, 'terrain grid dimensions are inconsistent');
assert(foundation.city.coastline.length > 0, 'foundation coastline is missing');
assert(integraBus.schema === 'bay-of-all-saints/threejs-integra-bus-v1', 'Integra bus schema mismatch');
assert(integraBus.asset_id === 'vehicle-integra-salvador-01', 'Integra bus asset id drifted');
assert(integraBus.source_sha256 === 'F3D5DEE69DCAB15379817A9AE13E562DF8023FD7AF38E8B6A0CDB4742AB650A2', 'Integra bus SHA drifted');
assert(integraBus.source_triangles === 1954141, 'Integra bus source triangle count drifted');
assert(integraBus.runtime_ready === false, 'heavy Integra GLB must not be promoted to runtime-ready');
assert(integraBus.traffic_binding === 'candidate_only', 'Integra bus must remain candidate-only on R30A.7 road graph');
assert(integraBus.target_dimensions_m.length === 12.0, 'Integra bus target length drifted');
assert(integraBus.target_dimensions_m.width === 2.55, 'Integra bus target width drifted');
assert(integraBus.target_dimensions_m.height === 3.25, 'Integra bus target height drifted');

console.log(JSON.stringify({
  ok: true,
  graph: {
    nodes: graph.nodes.length,
    edges: graph.edges.length,
    ways: graph.ways.length,
    directedArcs,
  },
  water: {
    level: water.water_level_m,
    swimmable: water.gameplay.swimmable,
    diveable: water.gameplay.diveable,
    boats: water.gameplay.boats_supported,
  },
  foundation: { buildings: foundation.city.buildings.length, terrainSamples: foundation.terrain.source_sample_count, grid: [foundation.terrain.grid.nx, foundation.terrain.grid.nz] },
  trafficVehicles: WORLD.traffic.vehicles,
  integraBus: { assetId: integraBus.asset_id, sourceTriangles: integraBus.source_triangles, runtimeReady: integraBus.runtime_ready },
}, null, 2));

