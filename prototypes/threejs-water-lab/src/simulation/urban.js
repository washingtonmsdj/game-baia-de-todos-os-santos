// Regras independentes do renderizador. Distâncias em metros, tempo em segundos.
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[2]-b[2]);
const lerp=(a,b,t)=>a.map((v,i)=>v+(b[i]-v)*t);
const modulo=(s,length)=>(s%length+length)%length;

export class Route {
  constructor(record) {
    Object.assign(this,record);
    const points=record.points.slice(0,-1),curve=[];
    for(let i=0;i<points.length;i++) {
      const p=points[i],prev=points[(i+points.length-1)%points.length],next=points[(i+1)%points.length];
      const trim=Math.min(2.1,distance(prev,p)*.28,distance(p,next)*.28);
      const a=lerp(p,prev,trim/distance(prev,p)),b=lerp(p,next,trim/distance(p,next));
      for(let k=0;k<=6;k++) { const t=k/6;curve.push(lerp(lerp(a,p,t),lerp(p,b,t),t)); }
    }
    curve.push(curve[0]);this.samples=[{p:curve[0],s:0}];let s=0;
    for(let i=1;i<curve.length;i++) {
      const a=curve[i-1],b=curve[i],n=Math.max(1,Math.ceil(distance(a,b)/.8));
      for(let j=1;j<=n;j++) {const p=lerp(a,b,j/n);s+=distance(this.samples.at(-1).p,p);this.samples.push({p,s});}
    }
    this.length=s;
  }
  at(position) {
    const s=modulo(position,this.length);let low=0,high=this.samples.length-1;
    while(high-low>1) {const mid=(high+low)>>1;if(this.samples[mid].s<s)low=mid;else high=mid;}
    const a=this.samples[low],b=this.samples[high],p=lerp(a.p,b.p,(s-a.s)/Math.max(.0001,b.s-a.s));
    const direction=lerp([0,0,0],b.p,1).map((v,i)=>v-a.p[i]);const l=Math.hypot(...direction);
    return {p,direction:direction.map(v=>v/l)};
  }
  project(p,around=null,range=Infinity) {
    let best=null;
    for(let i=0;i<this.samples.length-1;i++) {
      const a=this.samples[i],b=this.samples[i+1];
      if(around!==null && modulo(a.s-around,this.length)>range)continue;
      const dx=b.p[0]-a.p[0],dz=b.p[2]-a.p[2],len=dx*dx+dz*dz;
      const t=Math.max(0,Math.min(1,((p[0]-a.p[0])*dx+(p[2]-a.p[2])*dz)/Math.max(.0001,len)));
      const q=lerp(a.p,b.p,t),d=distance(p,q),s=a.s+(b.s-a.s)*t;
      if(!best || d<best.distance)best={s,distance:d};
    }
    return best;
  }
  ahead(s,target) {return modulo(target-s,this.length);}
}

export class UrbanSimulation {
  constructor(config,carLength=4.8) {
    this.config=config;this.routes=config.routes.map(r=>new Route(r));this.carLength=carLength;
    for(const r of this.routes)r.stop=r.project(config.signals.find(s=>s.group===r.signal_group).stop_position).s;
    this.time=0;this.phaseIndex=0;this.phaseTime=0;this.reservation=null;
    this.metrics={steps:0,laps:0,stoppedRed:0,releasedGreen:0,pedestrianCrossings:0,overlaps:0,redViolations:0,maxQueue:0,phaseChanges:0};
    this.cars=Array.from({length:8},(_,i)=>{const route=this.routes[i%2];const s=26+i*34;return {id:i,route,s,speed:0,laps:0,wait:0,wasStopped:false,...route.at(s)};});
    this.pedestrians=Array.from({length:6},(_,i)=>({id:i,stage:0,t:0,wait:i*2,side:i%2===0?0:1,p:config.crossing.points[i%2].slice(),crossing:false,walked:0}));
  }
  get phase() {return this.config.phases[this.phaseIndex];}
  get pedestrianGreen() {return this.phase.group==='ped';}
  permits(group) {return this.phase.group===group;}
  crossingOccupied(player) {
    const [a,b]=this.config.crossing.points,center=lerp(a,b,.5);
    return this.cars.some(c=>distance(c.p,center)<this.carLength/2+3.2) || this.pedestrians.some(p=>p.crossing) || (player && distance(player,center)<5.3);
  }
  update(dt,player=null) {
    this.time+=dt;this.metrics.steps++;this.phaseTime+=dt;
    if(this.phaseTime>=this.phase.seconds) {
      const next=(this.phaseIndex+1)%this.config.phases.length,group=this.config.phases[next].group;
      // All-red clearance lasts until the crossing/intersection is actually clear.
      const blocked=group==='ped' ? this.cars.some(c=>distance(c.p,this.config.junction)<18) : (group==='main'||group==='side') && this.crossingOccupied(player);
      if(!blocked) {this.phaseIndex=next;this.phaseTime=0;this.metrics.phaseChanges++;}
    }
    const owner=this.cars.find(c=>c.id===this.reservation);
    if(owner && owner.entered && distance(owner.p,this.config.junction)>17) {owner.entered=false;this.reservation=null;}
    const candidates=this.cars.filter(c=>this.permits(c.route.signal_group) && c.route.ahead(c.s,c.route.stop)<17).sort((a,b)=>b.wait-a.wait||a.id-b.id);
    if(this.reservation===null && candidates.length)this.reservation=candidates[0].id;
    const previous=this.cars.map(c=>({id:c.id,p:c.p.slice()}));
    for(const car of this.cars) {
      let remaining=Infinity;const stopGap=car.route.ahead(car.s,car.route.stop);const owns=car.id===this.reservation;
      if(stopGap<35 && !owns)remaining=Math.min(remaining,stopGap);
      for(const other of previous) {
        if(other.id===car.id)continue;
        const projection=car.route.project(other.p,car.s,32);
        if(projection && projection.distance<3.5) {
          const gap=car.route.ahead(car.s,projection.s);
          if(gap>.2)remaining=Math.min(remaining,gap-this.carLength-2.2);
        }
      }
      for(const p of [player,...this.pedestrians.map(p=>p.p)].filter(Boolean)) {
        const projection=car.route.project(p,car.s,30);
        if(projection && projection.distance<1.55 && Math.abs(p[1]-car.p[1])<2.5) {
          const gap=car.route.ahead(car.s,projection.s);
          if(gap>.1)remaining=Math.min(remaining,gap-this.carLength/2-1.4);
        }
      }
      const desired=Math.min(car.route.speed_m_s,Math.sqrt(2*3*Math.max(0,remaining)));
      car.speed=Math.max(0,car.speed+Math.max(-5*dt,Math.min(2*dt,desired-car.speed)));
      const move=Math.max(0,Math.min(car.speed*dt,remaining));
      if(remaining<.015) {car.speed=0;car.wait+=dt;if(!car.wasStopped && !this.permits(car.route.signal_group) && stopGap<1){this.metrics.stoppedRed++;car.wasStopped=true;}}
      else {if(car.wasStopped){this.metrics.releasedGreen++;car.wasStopped=false;}car.wait=0;}
      const s=car.s+move;if(s>=car.route.length){car.laps++;this.metrics.laps++;}
      car.s=modulo(s,car.route.length);Object.assign(car,car.route.at(car.s));
      if(owns && distance(car.p,this.config.junction)<7)car.entered=true;
    }
    const queue=this.cars.filter(c=>c.speed<.1).length;this.metrics.maxQueue=Math.max(queue,this.metrics.maxQueue);
    this.updatePedestrians(dt,player);
    for(let i=0;i<this.cars.length;i++)for(let j=i+1;j<this.cars.length;j++)if(distance(this.cars[i].p,this.cars[j].p)<this.carLength*.85)this.metrics.overlaps++;
  }
  updatePedestrians(dt,player) {
    const [a,b]=this.config.crossing.points;
    const crossingDirection=[b[0]-a[0],0,b[2]-a[2]],l=Math.hypot(...crossingDirection),f=[crossingDirection[2]/l,0,-crossingDirection[0]/l];
    for(const ped of this.pedestrians) {
      if(ped.wait>0){ped.wait-=dt;continue;}
      const start=ped.side===0?a:b,end=ped.side===0?b:a,offset=ped.side===0?.48:-.48;
      const lateral=ped.stage===0?.4:ped.stage===1?-.4:0;
      const shift=p=>[p[0]+f[0]*offset+crossingDirection[0]/l*lateral,p[1]+.12,p[2]+f[2]*offset+crossingDirection[2]/l*lateral];
      let from,to;
      if(ped.stage===0) {from=shift(start);to=shift(start.map((v,i)=>v+f[i]*10));}
      else if(ped.stage===1) {from=shift(start.map((v,i)=>v+f[i]*10));to=shift(start);}
      else {from=shift(start);to=shift(end);if(ped.t===0 && !this.pedestrianGreen)continue;}
      const length=distance(from,to);const next=Math.min(1,ped.t+dt*1.35/length),p=lerp(from,to,next);
      if(this.pedestrians.some(other=>other.id!==ped.id && other.crossing===ped.crossing && distance(other.p,p)<.65 && distance(other.p,to)<distance(ped.p,to)) || (player && distance(player,p)<.75))continue;
      ped.t=next;ped.p=p;ped.crossing=ped.stage===2;ped.walked+=dt*1.35;
      if(next===1){ped.t=0;ped.stage++;if(ped.stage>2){ped.stage=0;ped.side=1-ped.side;ped.crossing=false;ped.wait=1+ped.id*.3;this.metrics.pedestrianCrossings++;}}
    }
  }
  snapshot() {return {time:this.time,phase:this.phase.name,group:this.phase.group,phaseTime:this.phaseTime,reservation:this.reservation,metrics:{...this.metrics},cars:this.cars.map(c=>({id:c.id,route:c.route.id,s:c.s,speed:c.speed,position:c.p.slice(),laps:c.laps,wait:c.wait})),pedestrians:this.pedestrians.map(p=>({id:p.id,position:p.p.slice(),crossing:p.crossing,walked:p.walked}))};}
}
