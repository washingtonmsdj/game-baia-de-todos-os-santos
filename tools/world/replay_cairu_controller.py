"""Prova numérica de controller com gravidade/step/slide; não é física de engine."""
import json
from pathlib import Path
import numpy as np
from slice_geometry import capsule_distances,support_hits
from elevator_controller import crossing_allowed
from character_slide import lateral_contact,project_slide
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/cairu-market-b81'

def main(geometry=None, output_name='controller_replay.json', initial_connector=False):
 d=json.loads((geometry or ROOT/'artifacts/lacerda-controller/external_route_physics_b80.json').read_text(encoding='utf8'))
 design=d['qa']['character_design'];radius=design['radius'];height=design['height'];skin=design['contact_tolerance'];step=design['maximum_step']
 ts=[];ns=[];fs=[]
 for row in d['objects']:
  g=d['states']['closed_lower']['objects'].get(row['name'],row['geometry']);t=np.asarray(g['vertices'])[np.asarray(g['triangles'],dtype=int)]
  ts.append(t);ns.extend([row['name']]*len(t));fs.extend([row['walkable']]*len(t))
 tri=np.concatenate(ts);names=np.asarray(ns);floors=np.asarray(fs);lo=tri.min(axis=1);hi=tri.max(axis=1)
 def selection(a,b):
  return np.flatnonzero(np.all(hi>=np.minimum(a,b)-[radius,radius,0],axis=1)&np.all(lo<=np.maximum(a,b)+[radius,radius,height],axis=1))
 checks=[]
 def clear(a,b,label='walk'):
  ids=selection(a,b);local=tri[ids]
  if not len(ids):return True
  witness=None
  def interval(t0,t1,depth):
   nonlocal witness
   p=a+(b-a)*(t0+t1)/2;dist=capsule_distances(p,local,radius,height)
   # Skin é separação de contato, não licença para ignorar penetração profunda.
   if dist.min()<radius-skin:
    k=int(np.argmin(dist));witness={'object':str(names[ids[k]]),'triangle_index':int(ids[k]),'parameter':(t0+t1)/2,'position':p.tolist(),'penetration':float(radius-dist[k]),'classification':'SOLID_PENETRATION'}
    return False
   if dist.min()-(radius-skin)>np.linalg.norm(b-a)*(t1-t0)/2+1e-8:return True
   if depth==12:
    k=int(np.argmin(dist));witness={'object':str(names[ids[k]]),'triangle_index':int(ids[k]),'parameter':(t0+t1)/2,'position':p.tolist(),'penetration':float(radius-dist[k]),'classification':'NEEDS_REVIEW_CONVERGENCE'}
    return False
   return interval(t0,(t0+t1)/2,depth+1) and interval((t0+t1)/2,t1,depth+1)
  result=interval(0,1,0);checks.append({'phase':label,'from':a.tolist(),'to':b.tolist(),'clear':result,'witness':witness});return result
 def ground(p,maximum):
  ids=np.flatnonzero(floors&(hi[:,0]>=p[0])&(lo[:,0]<=p[0])&(hi[:,1]>=p[1])&(lo[:,1]<=p[1])&(hi[:,2]>=p[2]-.3)&(lo[:,2]<=maximum))
  ind,z=support_hits(p[0],p[1],tri[ids],p[2]-.3,maximum)
  if not len(ind):return None
  best=int(np.argmax(z));return float(z[best]),str(names[ids[ind[best]]])
 targets=d['qa']['routes']['external']['points'];p=np.asarray(targets[0]);velocity_z=0.;dt=1/60;events=[];stop=None
 crossing_xy=np.array([-57.93100311374292,65.21665694145486])
 if initial_connector:
  terminus=min(range(len(targets)),key=lambda i:np.linalg.norm(np.asarray(targets[i])[:2]-crossing_xy))
  if np.linalg.norm(np.asarray(targets[terminus])[:2]-crossing_xy)>1e-5:raise ValueError('Nó OSM 3178050253 não encontrado na rota existente')
  targets=targets[:terminus+1]
 for index,target in enumerate(targets[1:],1):
  checks.clear();step_attempt=None;slide_attempt=None
  desired=np.asarray(target);old=p.copy();reason='walk';velocity_z-=9.81*dt
  nextp=p.copy();nextp[:2]=desired[:2];nextp[2]+=velocity_z*dt
  support=ground(nextp,p[2]+skin)
  if support and nextp[2]<=support[0]+skin:
   nextp[2]=support[0]+skin;velocity_z=0
  if not clear(p,nextp):
   raised=p+[0,0,step];across=raised.copy();across[:2]=desired[:2];support=ground(across,raised[2])
   dropped=across.copy()
   if support:dropped[2]=support[0]+skin
   step_attempt={'raise':raised.tolist(),'forward':across.tolist(),'drop':dropped.tolist(),'support':support,'maximum_step':step,'strategy':'up/forward/drop; falha interrompe fases seguintes'}
   if support and clear(p,raised,'step_raise') and clear(raised,across,'step_forward') and clear(across,dropped,'step_drop'):
    nextp=dropped;velocity_z=0.;reason='step_up_forward_gravity_drop'
   else:
    ids=selection(p,nextp)
    if len(ids):
     blocked=next((check['witness'] for check in checks if check['phase']=='walk' and not check['clear']),None)
     contact=lateral_contact(p,nextp,np.asarray(blocked['position']) if blocked else nextp,tri[ids],radius,height,skin)
     slide_attempt={'normal_selection':'CCD witness; nearest lateral contact with opposing motion','attempted':False,'contact_found':contact is not None}
     if contact is not None:
      normal=contact['normal'];slide=project_slide(p,nextp,normal)
      slide_attempt.update({'normal_triangle_source':str(names[ids[contact['index']]]),'normal_triangle_index':int(ids[contact['index']]),'normal':normal.tolist(),'contact_distance':contact['distance'],'selection_point':contact['selection_point'].tolist()})
      # A projeção muda XY: apoio do alvo original não vale para o slide.
      slide_support=ground(slide,p[2]+skin)
      if slide_support and slide[2]<=slide_support[0]+skin:
       slide[2]=slide_support[0]+skin
      slide_attempt['support_at_slide']=slide_support
      slide_attempt.update({'attempted':True,'target':slide.tolist()})
      if clear(p,slide,'slide') and np.linalg.norm(slide[:2]-p[:2])>1e-4:
       nextp=slide;reason='slide_collision_normal'
       if slide_support and abs(slide[2]-slide_support[0]-skin)<1e-8:velocity_z=0.
      else:stop={'point':index,'reason':'BODY_COLLISION_STEP_SLIDE_BLOCKED'};break
     else:stop={'point':index,'reason':'BODY_COLLISION_STEP_BLOCKED'};break
    else:stop={'point':index,'reason':'NUMERICAL_CLEARANCE_UNRESOLVED'};break
  support=ground(nextp,nextp[2]+skin)
  gap=None if support is None else nextp[2]-support[0]
  if support is None or gap>.03 or gap<-.002:
   stop={'point':index,'reason':'GRAVITY_SUPPORT_NOT_CERTIFIED','support_gap':gap};break
  if np.linalg.norm(nextp[:2]-crossing_xy)<radius and not crossing_allowed(source_crossing_confirmed=True,traffic_permission=None,capsule_clear=False):
   stop={'point':index,'reason':'UNKNOWN_TRAFFIC_PERMISSION'};break
  p=nextp;events.append({'point':index,'position':p.tolist(),'previous':old.tolist(),'mode':reason,'support_source':support[1],'support_gap':gap,'vertical_velocity':velocity_z,'slide_attempt':slide_attempt,'ccd_attempts':list(checks) if slide_attempt else []})
 if stop is None:
  stop={'point':len(targets)-1,'reason':'CANDIDATE_SEQUENCE_EXHAUSTED_NO_ROUTE_APPROVAL','distance_to_terminus_xy':float(np.linalg.norm(p[:2]-np.asarray(targets[-1])[:2]))}
 report={'source':d['source'],'shape':{'radius':radius,'height':height,'skin':skin,'maximum_step':step},'gravity':9.81,'dt':dt,'steps':events,'stop':stop,'arrived':False,'movement_enabled':False,'engine_physics_verified':False,'method':'Cápsula com CCD Lipschitz; integração de gravidade, tentativa up/forward/drop e slide pela normal; apoio central real obrigatório. Prova numérica candidata, não substitui adapter de engine.','traffic_unknown_blocks':not crossing_allowed(source_crossing_confirmed=True,traffic_permission=None,capsule_clear=True),'market_entrance_verified':False,'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE'}
 if stop:
  stop.update({'previous_position':old.tolist(),'proposed_position':nextp.tolist(),'ccd_attempts':checks,'step_attempt':step_attempt,'slide_attempt':slide_attempt,'support_at_previous':ground(old,old[2]+skin),'support_at_proposal':ground(nextp,nextp[2]+skin),'witness_semantics':'Testemunha detectada por subdivisão, não tempo exato do primeiro contato.'})
 report['solver_revision']='lateral-contact-v3-support-at-projected-position'
 report['scope']='INITIAL_CONNECTOR_EXISTING_CANDIDATE_ONLY' if initial_connector else 'EXTERNAL_ROUTE'
 report['new_connector_created']=False
 destination=Path(output_name)
 if not destination.is_absolute():destination=OUT/destination
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'accepted_moves':len(events),'stop':stop,'arrived':False,'engine_verified':False}))
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--geometry',type=Path);parser.add_argument('--output-name',default='controller_replay.json');parser.add_argument('--initial-connector',action='store_true');args=parser.parse_args()
 main(args.geometry,args.output_name,args.initial_connector)
