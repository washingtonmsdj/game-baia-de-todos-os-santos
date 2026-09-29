import * as THREE from 'three';
import { ROAD_WIDTHS } from './worldConfig.js';
import { sampleRoadHeight } from './terrain.js';
import { loadRuntimeManifest, loadJsonAsset } from './runtime/assets.js';
import { blenderToRuntime } from './runtime/coordinates.js';

const X_AXIS = new THREE.Vector3(1, 0, 0);

export function roadWidth(highway) {
  return ROAD_WIDTHS[highway] ?? ROAD_WIDTHS.default;
}

export function roadSpeed(highway) {
  switch (highway) {
    case 'primary': return 15;
    case 'secondary': return 13;
    case 'tertiary': return 11;
    case 'residential': return 8.5;
    case 'service': return 6.0;
    case 'cycleway': return 4.5;
    default: return 8.0;
  }
}

export async function loadRoadGraph() {
  const manifest=await loadRuntimeManifest();
  const raw=await loadJsonAsset(manifest.assets.roads);
  if (!Array.isArray(raw.nodes) || !Array.isArray(raw.edges) || !Array.isArray(raw.ways)) {
    throw new Error('invalid road graph payload');
  }
  const nodes = new Map(raw.nodes.map((node) => [String(node.id), node]));
  const ways = new Map(raw.ways.map((way) => [Number(way.osm_way_id), way]));
  return { raw, nodes, ways };
}
function segmentFromEdge(edge, graph) {
  const from = graph.nodes.get(String(edge.from));
  const to = graph.nodes.get(String(edge.to));
  if (!from || !to) return null;
  const way = graph.ways.get(Number(edge.osm_way_id)) ?? {};
  const [ax, , az] = blenderToRuntime(...from.blender_xy);
  const [bx, , bz] = blenderToRuntime(...to.blender_xy);
  const ay = sampleRoadHeight(ax, az);
  const by = sampleRoadHeight(bx, bz);
  if (ay == null || by == null) return null;
  return {
    id: edge.id,
    edge,
    way,
    from,
    to,
    a: new THREE.Vector3(ax, ay, az),
    b: new THREE.Vector3(bx, by, bz),
    width: roadWidth(way.highway),
    speed: roadSpeed(way.highway),
  };
}

export function buildRoadSegments(graph) {
  const segments = [];
  for (const edge of graph.raw.edges) {
    const segment = segmentFromEdge(edge, graph);
    if (segment) segments.push(segment);
  }
  return segments;
}
function writeSegmentMatrix(segment, width, yOffset, target) {
  const a = segment.a.clone();
  const b = segment.b.clone();
  a.y += yOffset;
  b.y += yOffset;
  const direction = b.clone().sub(a);
  const length = Math.max(0.01, direction.length());
  const quaternion = new THREE.Quaternion().setFromUnitVectors(X_AXIS, direction.normalize());
  const position = a.add(b).multiplyScalar(0.5);
  const scale = new THREE.Vector3(length, 0.10, width);
  target.compose(position, quaternion, scale);
}

export function createRoadSurface(segments) {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const sidewalkMaterial = new THREE.MeshStandardMaterial({
    color: 0x8c8d88,
    roughness: 0.95,
  });
  const roadMaterial = new THREE.MeshStandardMaterial({
    color: 0x272b2d,
    roughness: 0.91,
  });
  const sidewalk = new THREE.InstancedMesh(geometry, sidewalkMaterial, segments.length);
  const road = new THREE.InstancedMesh(geometry, roadMaterial, segments.length);
  const matrix = new THREE.Matrix4();
  for (let i = 0; i < segments.length; i++) {
    writeSegmentMatrix(segments[i], segments[i].width + 3.2, -0.05, matrix);
    sidewalk.setMatrixAt(i, matrix);
    writeSegmentMatrix(segments[i], segments[i].width, 0.03, matrix);
    road.setMatrixAt(i, matrix);
  }
  sidewalk.instanceMatrix.needsUpdate = true;
  road.instanceMatrix.needsUpdate = true;
  sidewalk.receiveShadow = true;
  road.receiveShadow = true;
  sidewalk.name = 'Foundation Sidewalk Network';
  road.name = 'Foundation Road Network';
  return { road, sidewalk };
}

export function createRoadDebugLines(segments) {
  const points = [];
  for (const segment of segments) {
    points.push(segment.a.clone().add(new THREE.Vector3(0, 0.22, 0)));
    points.push(segment.b.clone().add(new THREE.Vector3(0, 0.22, 0)));
  }
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({ color: 0xffc64a, transparent: true, opacity: 0.72 });
  const lines = new THREE.LineSegments(geometry, material);
  lines.name = 'Road Graph Debug';
  lines.visible = false;
  return lines;
}

export function buildTrafficArcs(graph, segments) {
  const byId = new Map(segments.map((segment) => [segment.id, segment]));
  const outgoing = new Map();
  const arcs = [];
  const pushArc = (fromId, toId, segment, reverse) => {
    const arc = { fromId: String(fromId), toId: String(toId), segment, reverse };
    arcs.push(arc);
    const list = outgoing.get(arc.fromId) ?? [];
    list.push(arc);
    outgoing.set(arc.fromId, list);
  };
  for (const edge of graph.raw.edges) {
    if (edge.access === 'restricted') continue;
    const segment = byId.get(edge.id);
    if (!segment) continue;
    pushArc(edge.from, edge.to, segment, false);
    if (edge.direction === 'both') pushArc(edge.to, edge.from, segment, true);
  }
  return { arcs, outgoing };
}

export function roadGraphStats(graph, segments, trafficGraph) {
  return {
    nodes: graph.raw.nodes.length,
    edges: graph.raw.edges.length,
    ways: graph.raw.ways.length,
    renderedSegments: segments.length,
    trafficArcs: trafficGraph.arcs.length,
    junctions: graph.raw.stats?.junction_candidates ?? 0,
    oneWayEdges: graph.raw.stats?.one_way_edges ?? 0,
  };
}
