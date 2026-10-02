import * as THREE from 'three';

export class UrbanPlayer {
  constructor(camera,controls,physics,config) {
    this.camera=camera;this.controls=controls;this.physics=physics;this.config=config;this.keys=new Set();this.mode='A PÉ';this.velocityY=0;this.grounded=false;this.falls=0;this.distance=0;this.move=new THREE.Vector3();
    this.onDown=e=>{if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();this.keys.add(e.code);if(e.code==='KeyR'&&!e.repeat)this.reset();};
    this.onUp=e=>this.keys.delete(e.code);this.onBlur=()=>this.keys.clear();
    addEventListener('keydown',this.onDown);addEventListener('keyup',this.onUp);addEventListener('blur',this.onBlur);document.addEventListener('visibilitychange',this.onBlur);this.reset();
  }
  reset() {
    const [x,y,z]=this.config.spawn;this.physics.body.setTranslation({x,y:y+.82,z},true);this.physics.body.setNextKinematicTranslation({x,y:y+.82,z});this.velocityY=0;this.keys.clear();this.syncCamera();
    const target=this.config.crossing.points[0].map((v,i)=>(v+this.config.crossing.points[1][i])/2);this.camera.lookAt(target[0],this.camera.position.y-.25,target[2]);this.camera.rotation.order='YXZ';
    this.physics.world.step();
  }
  supported(x,z) {
    // Boundary follows the authored gameplay surfaces, not a decorative rectangle.
    for(const mesh of this.config.surfaces) {
      const p=mesh.positions;
      for(let i=0;i<mesh.indices.length;i+=3) {
        const ids=mesh.indices.slice(i,i+3).map(k=>k*3),[a,b,c]=ids;
        const denominator=(p[b+2]-p[c+2])*(p[a]-p[c])+(p[c]-p[b])*(p[a+2]-p[c+2]);
        if(Math.abs(denominator)<1e-8)continue;
        const u=((p[b+2]-p[c+2])*(x-p[c])+(p[c]-p[b])*(z-p[c+2]))/denominator;
        const v=((p[c+2]-p[a+2])*(x-p[c])+(p[a]-p[c])*(z-p[c+2]))/denominator;
        if(u>=0&&v>=0&&u+v<=1)return true;
      }
    }
    return false;
  }
  update(dt) {
    if(this.keys.has('ArrowLeft'))this.camera.rotation.y+=dt*1.6;if(this.keys.has('ArrowRight'))this.camera.rotation.y-=dt*1.6;
    if(this.keys.has('ArrowUp'))this.camera.rotation.x=Math.min(1.2,this.camera.rotation.x+dt);if(this.keys.has('ArrowDown'))this.camera.rotation.x=Math.max(-1.2,this.camera.rotation.x-dt);
    const forward=new THREE.Vector3();this.camera.getWorldDirection(forward);forward.y=0;forward.normalize();const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0));this.move.set(0,0,0);
    if(this.keys.has('KeyW'))this.move.add(forward);if(this.keys.has('KeyS'))this.move.sub(forward);if(this.keys.has('KeyD'))this.move.add(right);if(this.keys.has('KeyA'))this.move.sub(right);this.move.normalize().multiplyScalar((this.keys.has('ShiftLeft')?5:3.8)*dt);
    const p=this.physics.body.translation();
    // Stop before the supported strip edge; no invisible floor outside the slice.
    if(!this.supported(p.x+this.move.x,p.z+this.move.z))this.move.set(0,0,0);
    if(this.grounded) {this.velocityY=-.5;if(this.keys.has('Space')){this.velocityY=4.2;this.keys.delete('Space');}}
    else this.velocityY=Math.max(-20,this.velocityY-9.81*dt);
    this.physics.controller.computeColliderMovement(this.physics.capsule,{x:this.move.x,y:this.velocityY*dt,z:this.move.z});
    const movement=this.physics.controller.computedMovement();this.grounded=this.physics.controller.computedGrounded();if(this.grounded&&this.velocityY<0)this.velocityY=-.5;
    this.physics.body.setNextKinematicTranslation({x:p.x+movement.x,y:p.y+movement.y,z:p.z+movement.z});this.distance+=Math.hypot(movement.x,movement.z);
    if(p.y<this.config.spawn[1]-20){this.falls++;this.reset();}
  }
  syncCamera() {const p=this.physics.body.translation();this.camera.position.set(p.x,p.y+.9,p.z);}
  get feet() {const p=this.physics.body.translation();return [p.x,p.y-.82,p.z];}
}
