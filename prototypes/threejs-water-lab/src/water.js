import * as THREE from 'three';

export const WATER_LEVEL = 0.35;

export const WAVES = [
  { dir: new THREE.Vector2(1.0, 0.18).normalize(), amp: 0.42, length: 18.0, speed: 1.35, chop: 0.38 },
  { dir: new THREE.Vector2(0.45, 0.90).normalize(), amp: 0.22, length: 9.0, speed: 1.05, chop: 0.30 },
  { dir: new THREE.Vector2(-0.72, 0.35).normalize(), amp: 0.12, length: 4.4, speed: 0.82, chop: 0.20 },
  { dir: new THREE.Vector2(0.22, -0.98).normalize(), amp: 0.055, length: 2.1, speed: 0.58, chop: 0.12 },
];

export function sampleWaterHeight(x, z, time) {
  let height = WATER_LEVEL;
  for (const wave of WAVES) {
    const k = (Math.PI * 2) / wave.length;
    const phase = k * (wave.dir.x * x + wave.dir.y * z) + time * wave.speed;
    height += wave.amp * Math.sin(phase);
  }
  return height;
}

export function sampleWaterNormal(x, z, time, target = new THREE.Vector3()) {
  let dx = 0;
  let dz = 0;
  for (const wave of WAVES) {
    const k = (Math.PI * 2) / wave.length;
    const phase = k * (wave.dir.x * x + wave.dir.y * z) + time * wave.speed;
    const slope = wave.amp * k * Math.cos(phase);
    dx += slope * wave.dir.x;
    dz += slope * wave.dir.y;
  }
  return target.set(-dx, 1, -dz).normalize();
}

const vertexShader = /* glsl */`
uniform float uTime;
uniform float uWaterLevel;
varying vec3 vWorldPos;
varying vec3 vWorldNormal;
varying float vCrest;

vec3 wave(vec3 p, vec2 dir, float amp, float len, float speed, float chop, inout vec2 slope) {
  float k = 6.28318530718 / len;
  float phase = k * dot(dir, p.xz) + uTime * speed;
  float s = sin(phase);
  float c = cos(phase);
  slope += dir * (amp * k * c);
  p.xz += dir * (chop * amp * c);
  p.y += amp * s;
  return p;
}

void main() {
  vec3 p = position;
  p.y += uWaterLevel;
  vec2 slope = vec2(0.0);
  p = wave(p, normalize(vec2(1.0, .18)), .42, 18.0, 1.35, .38, slope);
  p = wave(p, normalize(vec2(.45, .90)), .22, 9.0, 1.05, .30, slope);
  p = wave(p, normalize(vec2(-.72, .35)), .12, 4.4, .82, .20, slope);
  p = wave(p, normalize(vec2(.22, -.98)), .055, 2.1, .58, .12, slope);
  vec3 localNormal = normalize(vec3(-slope.x, 1.0, -slope.y));
  vec4 world = modelMatrix * vec4(p, 1.0);
  vWorldPos = world.xyz;
  vWorldNormal = normalize(mat3(modelMatrix) * localNormal);
  vCrest = smoothstep(.38, .72, p.y - uWaterLevel);
  gl_Position = projectionMatrix * viewMatrix * world;
}
`;

const fragmentShader = /* glsl */`
uniform float uTime;
uniform vec3 uSunDirection;
uniform vec3 uDeepColor;
uniform vec3 uShallowColor;
uniform vec3 uSkyColor;
uniform vec3 uSunColor;
varying vec3 vWorldPos;
varying vec3 vWorldNormal;
varying float vCrest;

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.,0.)), f.x),
             mix(hash(i + vec2(0.,1.)), hash(i + vec2(1.,1.)), f.x), f.y);
}

void main() {
  vec3 N = normalize(vWorldNormal);
  vec3 V = normalize(cameraPosition - vWorldPos);
  float ndv = clamp(dot(N, V), 0.0, 1.0);
  float fresnel = 0.025 + 0.975 * pow(1.0 - ndv, 5.0);
  float sun = pow(max(dot(reflect(-uSunDirection, N), V), 0.0), 180.0);
  float horizon = pow(1.0 - max(N.y, 0.0), 2.0);
  float micro = noise(vWorldPos.xz * 2.2 + vec2(uTime * .07, -uTime * .05));
  vec3 body = mix(uDeepColor, uShallowColor, clamp(.18 + N.y * .34 + micro * .10, 0.0, 1.0));
  vec3 reflected = mix(uSkyColor * .52, uSkyColor * 1.25, fresnel + horizon * .35);
  float foamNoise = noise(vWorldPos.xz * .72 + uTime * .06);
  float crestFoam = smoothstep(.96, 1.10, vCrest + foamNoise * .18);
  float shoreDist = max(vWorldPos.x + 6.0, 0.0);
  float shoreFoam = (1.0 - smoothstep(0.0, 4.5, shoreDist)) * smoothstep(.48, .78, foamNoise);
  float foam = max(crestFoam, shoreFoam * .58);
  vec3 color = mix(body, reflected, fresnel * .78);
  color += uSunColor * sun * 2.6;
  color = mix(color, vec3(.82, .92, .94), foam * .72);
  float alpha = mix(.93, .985, fresnel);
  gl_FragColor = vec4(color, alpha);
}
`;

export function createWaterMesh() {
  const geometry = new THREE.PlaneGeometry(420, 420, 260, 260);
  geometry.rotateX(-Math.PI / 2);
  const material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: true,
    uniforms: {
      uTime: { value: 0 },
      uWaterLevel: { value: WATER_LEVEL },
      uSunDirection: { value: new THREE.Vector3(0.35, 0.84, 0.42).normalize() },
      uDeepColor: { value: new THREE.Color('#063f55') },
      uShallowColor: { value: new THREE.Color('#13859a') },
      uSkyColor: { value: new THREE.Color('#89b8db') },
      uSunColor: { value: new THREE.Color('#fff2cf') },
    },
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  mesh.receiveShadow = true;
  mesh.name = 'All Saints Runtime Water Prototype';
  return mesh;
}

