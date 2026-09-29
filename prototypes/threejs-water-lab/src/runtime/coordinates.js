// Rotação própria; não altera chirality nem aplica escala negativa ao mundo.
export function blenderToRuntime(x,y,z=0) { return [x,z,-y]; }
