"""Prova ao vivo dos quatro ciclos na mesma cena, com passos de1/60s."""
import bpy,json,runpy,time,os
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-exterior-b102'
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b102_corpo_encosta_quatro_elevadores.blend'
ns=runpy.run_path(str(root/'automation/blender/play_lacerda_four_lifts.py'))
state=ns['initialize']();sync=ns['sync'];cfg=ns['CONFIG'];Lift=ns['Lift']
assert all(s['movement_enabled'] for s in cfg['equipment'])
started=time.monotonic();phase='OPEN_UPPER';ticks=0;counts={s['id']:0 for s in cfg['equipment']};maxdelta={k:0. for k in counts};events=[]
for lift in state['lifts'].values():assert lift.request('upper')
def advance():
 global phase,ticks
 try:
  for _ in range(8):
   for lift in state['lifts'].values():
    old=lift.z;lift.update(1/60);counts[lift.id]+=1;maxdelta[lift.id]=max(maxdelta[lift.id],abs(lift.z-old))
    if lift.state=='MOVING':assert lift.openness==0. and lift.station is None
    if lift.passenger_z is not None:assert abs(lift.passenger_z-lift.z-.015)<1e-7
   if phase=='OPEN_UPPER' and all(l.state=='OPEN' for l in state['lifts'].values()):
    # Sensor de portal ocupado impede fechar, testado também nesta sessão.
    for lift in state['lifts'].values():
     lift.portal_occupied=True;assert lift.depart();lift.update(1/60);assert lift.state=='OPEN'
     lift.portal_occupied=False;lift.passenger_z=lift.z+.015;assert lift.depart()
    phase='DESCENDING';events.append('ALL_UPPER_OPEN_PORTAL_INTERLOCK_PASSED')
   elif phase=='DESCENDING' and all(l.state=='OPEN' and l.station=='lower' for l in state['lifts'].values()):
    events.append('ALL_LOWER_OPEN');phase='ASCENDING'
    for lift in state['lifts'].values():assert lift.depart()
   elif phase=='ASCENDING' and all(l.state=='OPEN' and l.station=='upper' for l in state['lifts'].values()):
    phase='FINISHED';events.append('ALL_UPPER_RETURNED')
  sync(state);ticks+=1
  if phase!='FINISHED':return .02
  final={'status':'FOUR_LIFTS_LIVE_ROUND_TRIP_PASSED','file':Path(bpy.data.filepath).relative_to(root).as_posix(),'scene':bpy.context.scene.name,
    'pid':os.getpid(),'visible_session':True,'real_elapsed_s':time.monotonic()-started,'viewport_updates':ticks,'events':events,
    'equipment':[{'id':k,'physics_steps':counts[k],'max_continuous_displacement_m':maxdelta[k],'rider_offset_m':l.passenger_z-l.z,'station':l.station,'state':l.state} for k,l in state['lifts'].items()],
    'historical_gate':'BLOCKED_EXTERNAL_EVIDENCE','pedestrian_route_status':'NOT_TESTED_BY_THIS_PROOF','production_ready':False}
  (out/'live-proof.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  # Estado salvo sempre é fechado no alto, não uma animação parcial.
  for l in state['lifts'].values():l.state='CLOSED';l.openness=0.;l.passenger_z=None
  sync(state);print('B102: quatro ciclos ao vivo concluídos; estados restaurados.')
  return None
 except Exception as exc:
  (out/'live-proof.json').write_text(json.dumps({'status':'FAILED','error':str(exc),'phase':phase,'production_ready':False},indent=2)+'\n')
  return None
bpy.app.timers.register(advance,first_interval=.05)
print('Prova ao vivo iniciada na B102; quatro equipamentos simultâneos, sem deslocar o personagem por teleporte.')
