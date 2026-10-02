import * as THREE from 'three';
import {PointerLockControls} from 'three/addons/controls/PointerLockControls.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {loadRuntimeManifest} from './runtime/assets.js';
import {loadOfficialCity} from './officialCity.js';
import {loadGroundSurface} from './groundSurface.js';
import {configureGroundSurface} from './terrain.js';
import {UrbanSimulation} from './simulation/urban.js';
import {createUrbanPhysics} from './physics/urbanWorld.js';
import {UrbanPlayer} from './urbanPlayer.js';
import {createUrbanView} from './render/urbanView.js';
import './styles.css';

const loading=document.querySelector('#loading');
try {
  const manifest=await loadRuntimeManifest();
  const config=await (await fetch('/data/urban_slice.json')).json();
  const carMetadata=await (await fetch('/assets/vehicles/car-v14.json')).json();
  const scene=new THREE.Scene();scene.background=new THREE.Color(0xbdd5e0);scene.fog=new THREE.Fog(0xbdd5e0,170,650);
  const camera=new THREE.PerspectiveCamera(68,innerWidth/innerHeight,.08,1100);
  const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,manifest.settings.render.max_pixel_ratio));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.shadowMap.enabled=false;document.querySelector('#app').appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xd6ebff,0x726954,2.5));const sun=new THREE.DirectionalLight(0xfff0d5,2.8);sun.position.set(-80,200,-100);scene.add(sun);
  const groundSurface=await loadGroundSurface();configureGroundSurface(groundSurface);
  const city=await loadOfficialCity({onProgress:p=>{loading.textContent=`Carregando cidade oficial · ${p.loaded}/${p.total} setores`;}});scene.add(city.object);
  const terrainReview=config.status==='terrain_review';
  const simulation=new UrbanSimulation(config,carMetadata.dimensions_m[2]);
  const physics=await createUrbanPhysics(config,carMetadata.dimensions_m);
  const controls=new PointerLockControls(camera,renderer.domElement);
  const player=new UrbanPlayer(camera,controls,physics,config);
  const view=terrainReview?{update(){}}:await createUrbanView(scene,simulation,config);
  const orbit=new OrbitControls(camera,renderer.domElement);orbit.enabled=false;orbit.enableDamping=true;orbit.minDistance=15;orbit.maxDistance=220;
  let overview=false,paused=false,accumulator=0,last=performance.now(),lastRender=0,frames=0,frameSeconds=0,fps=0,streamTimer=0;
  function enterOnFoot(lock=false) {overview=false;orbit.enabled=false;player.reset();if(lock)controls.lock();}
  document.querySelector('#play').onclick=()=>enterOnFoot(true);
  document.querySelector('#overview').onclick=()=>{if(overview){enterOnFoot();return;}controls.unlock();overview=true;orbit.enabled=true;orbit.target.fromArray(config.junction);camera.position.copy(orbit.target).add(new THREE.Vector3(-35,65,70));camera.lookAt(orbit.target);};
  document.querySelector('#reset').onclick=()=>enterOnFoot();
  renderer.domElement.addEventListener('click',()=>{if(!overview)controls.lock();});
  addEventListener('keydown',e=>{if(e.code==='KeyR') {overview=false;orbit.enabled=false;player.reset();}if(e.code==='KeyH')document.querySelector('#details').open=!document.querySelector('#details').open;});
  document.addEventListener('visibilitychange',()=>{paused=document.hidden;accumulator=0;last=performance.now();});
  let contextLost=false;renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();contextLost=true;loading.textContent='Renderização interrompida. Recarregue a página.';loading.classList.remove('hidden');});
  loading.classList.add('hidden');
  const stats=()=>({...simulation.snapshot(),player:{position:player.feet,grounded:player.grounded,falls:player.falls,distance:player.distance},streaming:city.controller.getStats(),source:manifest.source,render:{fps,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles},overview,contextLost});
  window.__ALL_SAINTS__={version:'urban-slice-v1',camera,player,traffic:simulation,simulation,physics,config,renderer,officialCity:city,groundSurface,view,enterOnFoot,reset:()=>enterOnFoot(),snapshot:stats};
  function animate(now) {
    requestAnimationFrame(animate);const elapsed=(now-last)/1000;last=now;if(paused||contextLost)return;
    accumulator+=Math.min(elapsed,.25);let steps=0;
    while(accumulator>=1/60 && steps++<15) {
      if(!overview)player.update(1/60);
      if(!terrainReview){simulation.update(1/60,overview?null:player.feet);physics.updateCars(simulation);}physics.world.step();accumulator-=1/60;
    }
    if(now-lastRender<1000/manifest.settings.render.max_fps)return;
    const dt=(now-lastRender)/1000;lastRender=now;if(!overview)player.syncCamera();else orbit.update();view.update(dt);
    streamTimer-=dt;if(streamTimer<=0){city.controller.update(camera.position);streamTimer=.5;}
    renderer.render(scene,camera);frames++;frameSeconds+=dt;
    if(frameSeconds>=1) {
      fps=frames/frameSeconds;frames=0;frameSeconds=0;
      document.querySelector('#status').textContent=terrainReview?'Revisão do terreno · tráfego pausado':simulation.pedestrianGreen?'Travessia liberada':'Aguarde o sinal de pedestres';
      document.querySelector('#world-stats').textContent=`${simulation.phase.name} · ${simulation.cars.length} carros · ${simulation.pedestrians.length} pedestres`;
      document.querySelector('#fps').textContent=`${fps.toFixed(0)} FPS · ${simulation.metrics.laps} voltas · ${simulation.metrics.pedestrianCrossings} travessias`;
      document.querySelector('#diagnostics').textContent=JSON.stringify(stats());
    }
  }
  requestAnimationFrame(animate);
  addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
} catch(error) {loading.classList.remove('hidden');loading.textContent=`Falha ao abrir o teste: ${error.message}`;console.error(error);}
