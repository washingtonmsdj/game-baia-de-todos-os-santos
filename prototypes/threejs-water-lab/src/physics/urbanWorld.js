import RAPIER from '../../vendor/rapier3d-compat/rapier.es.js';

export async function createUrbanPhysics(config,dimensions) {
  await RAPIER.init();
  const world=new RAPIER.World({x:0,y:-9.81,z:0});world.timestep=1/60;
  for(const mesh of config.surfaces)world.createCollider(RAPIER.ColliderDesc.trimesh(new Float32Array(mesh.positions),new Uint32Array(mesh.indices)));
  for(const obstacle of config.obstacles) {
    if(obstacle.vertices) {const desc=RAPIER.ColliderDesc.convexHull(new Float32Array(obstacle.vertices));if(desc)world.createCollider(desc);}
    else {const [lo,hi]=obstacle.bounds;world.createCollider(RAPIER.ColliderDesc.cuboid(...lo.map((v,i)=>(hi[i]-v)/2)).setTranslation(...lo.map((v,i)=>(hi[i]+v)/2)));}
  }
  const body=world.createRigidBody(RAPIER.RigidBodyDesc.kinematicPositionBased());
  const capsule=world.createCollider(RAPIER.ColliderDesc.capsule(.5,.32),body);
  const controller=world.createCharacterController(.025);
  controller.enableAutostep(.24,.3,false);controller.enableSnapToGround(.35);controller.setMaxSlopeClimbAngle(Math.PI/4);controller.setMinSlopeSlideAngle(Math.PI/3);
  const cars=[];
  function updateCars(simulation) {
    for(const car of simulation.cars) {
      if(!cars[car.id]) {const b=world.createRigidBody(RAPIER.RigidBodyDesc.kinematicPositionBased());world.createCollider(RAPIER.ColliderDesc.cuboid(dimensions[0]/2,dimensions[1]/2,dimensions[2]/2),b);cars[car.id]=b;}
      const yaw=Math.atan2(car.direction[0],car.direction[2]);const b=cars[car.id];
      b.setNextKinematicTranslation({x:car.p[0],y:car.p[1]+dimensions[1]/2,z:car.p[2]});b.setNextKinematicRotation({x:0,y:Math.sin(yaw/2),z:0,w:Math.cos(yaw/2)});
    }
  }
  return {world,body,capsule,controller,updateCars};
}
