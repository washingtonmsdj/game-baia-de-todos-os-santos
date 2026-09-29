import { loadRuntimeManifest } from './runtime/assets.js';
const settings=(await loadRuntimeManifest()).settings;
export const WORLD=Object.freeze(settings.world);
export const ROAD_WIDTHS=Object.freeze(settings.road_widths_gameplay_m);
