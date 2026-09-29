import * as THREE from 'three';
import { WORLD } from './worldConfig.js';
import { isWaterAt, sampleGameplayGround, WORLD_BOUNDS } from './terrain.js';
import { sampleWaterHeight } from './water.js';

export const PlayerMode = Object.freeze({
  ON_FOOT: 'A PÉ',
  SWIMMING: 'NADANDO',
  DIVING: 'MERGULHO',
});

export class PlayerController {
  constructor(camera, controls, colliders = []) {
    this.camera = camera;
    this.controls = controls;
    this.colliders = colliders;
    this.keys = new Set();
    this.mode = PlayerMode.ON_FOOT;
    this.eyeHeight = 1.72;
    this.verticalVelocity = 0;
    this.forward = new THREE.Vector3();
    this.right = new THREE.Vector3();
    this.move = new THREE.Vector3();
    this.up = new THREE.Vector3(0, 1, 0);
    this.lastGround = null;

    this.onKeyDown = (event) => {
      this.keys.add(event.code);
      if (event.code === 'KeyR') this.reset();
    };
    this.onKeyUp = (event) => this.keys.delete(event.code);
    addEventListener('keydown', this.onKeyDown);
    addEventListener('keyup', this.onKeyUp);
    this.reset();
  }

  reset() {
    const { x, z } = WORLD.spawn;
    const ground = sampleGameplayGround(x, z) ?? WORLD.waterLevel;
    this.camera.position.set(x, ground + this.eyeHeight, z);
    this.camera.rotation.set(0, THREE.MathUtils.degToRad(WORLD.spawn.headingDeg), 0);
    this.verticalVelocity = 0;
    this.mode = PlayerMode.ON_FOOT;
  }
  _readHorizontalInput() {
    this.camera.getWorldDirection(this.forward);
    this.forward.y = 0;
    if (this.forward.lengthSq() < 0.001) this.forward.set(0, 0, -1);
    this.forward.normalize();
    this.right.crossVectors(this.forward, this.up).normalize();
    this.move.set(0, 0, 0);
    if (this.keys.has('KeyW')) this.move.add(this.forward);
    if (this.keys.has('KeyS')) this.move.sub(this.forward);
    if (this.keys.has('KeyD')) this.move.add(this.right);
    if (this.keys.has('KeyA')) this.move.sub(this.right);
    if (this.move.lengthSq() > 0) this.move.normalize();
    return this.move;
  }

  _clampWorld() {
    const margin = 8;
    this.camera.position.x = THREE.MathUtils.clamp(
      this.camera.position.x,
      WORLD_BOUNDS.minX + margin,
      WORLD_BOUNDS.maxX - margin,
    );
    this.camera.position.z = THREE.MathUtils.clamp(
      this.camera.position.z,
      WORLD_BOUNDS.minZ + margin,
      WORLD_BOUNDS.maxZ - margin,
    );
  }

  _blocked(x, z) {
    for (const collider of this.colliders) {
      const dx = x - collider.x;
      const dz = z - collider.z;
      const limit = collider.radius + 0.55;
      if (dx * dx + dz * dz < limit * limit) return true;
    }
    return false;
  }

  _moveOnGround(move, distance) {
    const x = this.camera.position.x + move.x * distance;
    if (!this._blocked(x, this.camera.position.z)) this.camera.position.x = x;
    const z = this.camera.position.z + move.z * distance;
    if (!this._blocked(this.camera.position.x, z)) this.camera.position.z = z;
  }

  _updateOnFoot(dt) {
    const move = this._readHorizontalInput();
    const sprint = this.keys.has('ShiftLeft') || this.keys.has('ShiftRight');
    const speed = sprint ? 8.5 : 5.2;
    this._moveOnGround(move, speed * dt);
    const ground = sampleGameplayGround(this.camera.position.x, this.camera.position.z);
    if (ground == null) return;
    this.lastGround = ground;
    const floorY = ground + this.eyeHeight;
    const grounded = this.camera.position.y <= floorY + 0.04;
    if (grounded && this.keys.has('Space')) {
      this.verticalVelocity = 5.2;
    }
    this.verticalVelocity -= WORLD.gravity * dt;
    this.camera.position.y += this.verticalVelocity * dt;
    if (this.camera.position.y < floorY) {
      this.camera.position.y = floorY;
      this.verticalVelocity = 0;
    }
  }

  _updateSwimming(dt, surface) {
    const move = this._readHorizontalInput();
    const boost = this.keys.has('ShiftLeft') || this.keys.has('ShiftRight');
    const speed = boost ? 5.2 : 3.2;
    this.camera.position.addScaledVector(move, speed * dt);
    const targetY = surface + 0.18;
    this.camera.position.y = THREE.MathUtils.damp(this.camera.position.y, targetY, 5.5, dt);
    if (this.keys.has('KeyQ')) this.camera.position.y -= 2.4 * dt;
    if (this.keys.has('KeyE') || this.keys.has('Space')) this.camera.position.y += 1.8 * dt;
  }

  _updateDiving(dt) {
    this.camera.getWorldDirection(this.forward).normalize();
    this.right.crossVectors(this.forward, this.up).normalize();
    this.move.set(0, 0, 0);
    if (this.keys.has('KeyW')) this.move.add(this.forward);
    if (this.keys.has('KeyS')) this.move.sub(this.forward);
    if (this.keys.has('KeyD')) this.move.add(this.right);
    if (this.keys.has('KeyA')) this.move.sub(this.right);
    if (this.keys.has('KeyE') || this.keys.has('Space')) this.move.y += 1;
    if (this.keys.has('KeyQ')) this.move.y -= 1;
    if (this.move.lengthSq() > 0) this.move.normalize();
    const boost = this.keys.has('ShiftLeft') || this.keys.has('ShiftRight');
    this.camera.position.addScaledVector(this.move, (boost ? 5.8 : 3.6) * dt);
  }

  update(dt, time) {
    const surface = sampleWaterHeight(this.camera.position.x, this.camera.position.z, time);
    const overWater = isWaterAt(this.camera.position.x, this.camera.position.z);
    const depth = surface - this.camera.position.y;

    if (!overWater) {
      this.mode = PlayerMode.ON_FOOT;
      this._updateOnFoot(dt);
    } else if (depth > 0.65 || this.keys.has('KeyQ')) {
      this.mode = PlayerMode.DIVING;
      this._updateDiving(dt);
    } else {
      this.mode = PlayerMode.SWIMMING;
      this._updateSwimming(dt, surface);
    }

    this._clampWorld();
    const updatedSurface = sampleWaterHeight(this.camera.position.x, this.camera.position.z, time);
    const updatedGround = sampleGameplayGround(this.camera.position.x, this.camera.position.z);
    if (this.mode === PlayerMode.DIVING) {
      const minY = Math.max(-14.0, updatedSurface - 15.0);
      this.camera.position.y = Math.max(minY, this.camera.position.y);
      if (this.camera.position.y > updatedSurface + 0.35) this.camera.position.y = updatedSurface + 0.35;
    }

    return {
      mode: this.mode,
      surface: updatedSurface,
      depth: Math.max(0, updatedSurface - this.camera.position.y),
      ground: updatedGround,
      overWater: isWaterAt(this.camera.position.x, this.camera.position.z),
      position: this.camera.position,
    };
  }

  dispose() {
    removeEventListener('keydown', this.onKeyDown);
    removeEventListener('keyup', this.onKeyUp);
  }
}
