export const WORLD = Object.freeze({
  waterLevel: 0.35,
  gravity: 9.81,
  cityBounds: {
    minX: -460,
    maxX: 720,
    minZ: -560,
    maxZ: 1520,
  },
  oceanBounds: {
    minX: -1400,
    maxX: -365,
    minZ: -900,
    maxZ: 1580,
  },
  spawn: {
    x: -34.0,
    z: 28.0,
    headingDeg: 180,
  },
  traffic: {
    vehicles: 72,
    minSpeed: 7,
    maxSpeed: 15,
  },
});

export const ROAD_WIDTHS = Object.freeze({
  primary: 9.0,
  secondary: 7.5,
  tertiary: 6.4,
  residential: 5.2,
  service: 3.8,
  cycleway: 2.4,
  default: 4.8,
});

