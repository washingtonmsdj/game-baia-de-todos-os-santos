import * as THREE from 'three';
import { WORLD } from './worldConfig.js';

const Z_AXIS = new THREE.Vector3(0, 0, 1);
const tempPosition = new THREE.Vector3();
const tempDirection = new THREE.Vector3();
const tempRight = new THREE.Vector3();
const tempQuaternion = new THREE.Quaternion();
const tempMatrix = new THREE.Matrix4();
const tempScale = new THREE.Vector3(1.8, 1.25, 4.2);

function seededRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state * 1664525 + 1013904223) >>> 0;
    return state / 4294967296;
  };
}

function arcEndpoints(arc) {
  return arc.reverse
    ? [arc.segment.b, arc.segment.a]
    : [arc.segment.a, arc.segment.b];
}

function arcLength(arc) {
  const [a, b] = arcEndpoints(arc);
  return a.distanceTo(b);
}

export class TrafficSystem {
  constructor(trafficGraph, count = WORLD.traffic.vehicles) {
    this.graph = trafficGraph;
    this.random = seededRandom(0xA11A5A17);
    this.vehicles = [];
    this.enabled = true;
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshStandardMaterial({ color: 0x9b2f24, roughness: 0.52, metalness: 0.08 });
    this.mesh = new THREE.InstancedMesh(geometry, material, count);
    this.mesh.name = 'Foundation Traffic Vehicles';
    this.mesh.castShadow = true;
    this.mesh.receiveShadow = true;

    const usable = trafficGraph.arcs.filter((arc) => arcLength(arc) > 3);
    for (let i = 0; i < count; i++) {
      const arc = usable[Math.floor(this.random() * usable.length)];
      this.vehicles.push({
        arc,
        t: this.random(),
        speed: arc.segment.speed * (0.72 + this.random() * 0.32),
        desiredSpeed: arc.segment.speed * (0.78 + this.random() * 0.34),
      });
    }
    this._writeInstances();
  }

  setVisible(value) {
    this.enabled = Boolean(value);
    this.mesh.visible = this.enabled;
  }

  _chooseNext(vehicle) {
    const candidates = this.graph.outgoing.get(vehicle.arc.toId) ?? [];
    if (!candidates.length) return null;
    const withoutUTurn = candidates.filter((candidate) => candidate.toId !== vehicle.arc.fromId);
    const pool = withoutUTurn.length ? withoutUTurn : candidates;
    return pool[Math.floor(this.random() * pool.length)];
  }
  _applyHeadway(dt) {
    const groups = new Map();
    for (const vehicle of this.vehicles) {
      const key = `${vehicle.arc.fromId}>${vehicle.arc.toId}:${vehicle.arc.segment.id}`;
      const list = groups.get(key) ?? [];
      list.push(vehicle);
      groups.set(key, list);
    }
    for (const list of groups.values()) {
      list.sort((a, b) => a.t - b.t);
      const length = arcLength(list[0].arc);
      for (let i = 0; i < list.length; i++) {
        const vehicle = list[i];
        let target = vehicle.desiredSpeed;
        const lead = list[i + 1];
        if (lead) {
          const gap = (lead.t - vehicle.t) * length;
          if (gap < 14) target = Math.min(target, Math.max(0, (gap - 3.5) * 0.9));
        }
        const rate = target < vehicle.speed ? 7.5 : 2.2;
        vehicle.speed += THREE.MathUtils.clamp(target - vehicle.speed, -rate * dt, rate * dt);
      }
    }
  }

  update(dt) {
    if (!this.enabled) return;
    this._applyHeadway(dt);
    for (const vehicle of this.vehicles) {
      let length = Math.max(0.1, arcLength(vehicle.arc));
      vehicle.t += (vehicle.speed * dt) / length;
      let guard = 0;
      while (vehicle.t >= 1 && guard++ < 4) {
        const overflowMeters = (vehicle.t - 1) * length;
        const next = this._chooseNext(vehicle);
        if (!next) {
          vehicle.arc = this.graph.arcs[Math.floor(this.random() * this.graph.arcs.length)];
          vehicle.t = this.random() * 0.35;
          break;
        }
        vehicle.arc = next;
        length = Math.max(0.1, arcLength(vehicle.arc));
        vehicle.t = overflowMeters / length;
        vehicle.desiredSpeed = vehicle.arc.segment.speed * (0.78 + this.random() * 0.34);
      }
    }
    this._writeInstances();
  }

  _writeInstances() {
    const laneOffsetFactor = 0.22;
    for (let i = 0; i < this.vehicles.length; i++) {
      const vehicle = this.vehicles[i];
      const [a, b] = arcEndpoints(vehicle.arc);
      tempPosition.lerpVectors(a, b, THREE.MathUtils.clamp(vehicle.t, 0, 1));
      tempDirection.subVectors(b, a).normalize();
      tempRight.set(tempDirection.z, 0, -tempDirection.x).normalize();
      const laneOffset = Math.min(1.6, vehicle.arc.segment.width * laneOffsetFactor);
      tempPosition.addScaledVector(tempRight, laneOffset);
      tempPosition.y += 0.76;
      tempQuaternion.setFromUnitVectors(Z_AXIS, tempDirection);
      tempMatrix.compose(tempPosition, tempQuaternion, tempScale);
      this.mesh.setMatrixAt(i, tempMatrix);
    }
    this.mesh.instanceMatrix.needsUpdate = true;
  }

  getStats() {
    if (!this.vehicles.length) return { vehicles: 0, averageSpeedKmh: 0 };
    const average = this.vehicles.reduce((sum, vehicle) => sum + vehicle.speed, 0) / this.vehicles.length;
    return {
      vehicles: this.vehicles.length,
      averageSpeedKmh: average * 3.6,
    };
  }
}
