"""QA estrutural e cápsula local na frente; sem liberar elevador histórico."""
import bpy,json,runpy,sys,math
from pathlib import Path
import numpy as np
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-completion-b98'
ns=runpy.run_path(str(Path(__file__).with_name('validate_lacerda_corridors_b94.py')),init_globals={'BOAS_ENCLOSURE_REVISION':98})
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());cfg=json.loads((out/'controls.json').read_text());scene=bpy.context.scene
sig=ns['sig'];wm=ns['wm'];inv=ns['inv'];bounds=ns['bounds']
for n,s in r['preserved_signatures'].items():assert sig(scene.objects[n])==s,n
for row in r['archived']:
 o=scene.objects[row['object']];assert sig(o)==row['before'] and o.hide_get() and o.hide_render,row['object']
contact=[];residual=[];floor='SUPERIOR | piso saguão';roof='SUPERIOR | cobertura saguão';z=cfg['levels']['floor'];zc=cfg['levels']['ceiling']
for row in r['added']:
 o=scene.objects[row['object']];p=[inv@wm(o)@v.co for v in o.data.vertices];poly=row['outline_local'];expected=[Vector((a,b,zv)) for zv in row['levels'] for a,b in poly]
 error=max((a-b).length for a,b in zip(p,expected));assert error<2e-5,(o.name,error)
 residual.append({'object':o.name,'max_document_control_residual_m':error,'source_control':row['source_control']})
 center=Vector((sum(a for a,b in poly)/len(poly),sum(b for a,b in poly)/len(poly)))
 ns['support_check'](floor,center,z,'FRONT_PILLAR_HEADER_OR_ROLLER_FLOOR_SUPPORT')
 ns['support_check'](roof,center,z+4.,'FRONT_COVERAGE')
 b=bounds(o.name);assert abs(b[2][1]-row['levels'][1])<1e-4
 if row['function']=='STRUCTURAL_PILLAR':assert abs(b[2][0]-z)<1e-4 and abs(b[2][1]-zc)<1e-4
 contact.append({'object':o.name,'bottom_z':b[2][0],'top_z':b[2][1],'document_or_candidate_levels':row['levels'],'contact_classification':'EXPECTED_CONTACT_NOT_PENETRATION'})
sys.path.insert(0,str(root/'tools/world'));from slice_geometry import capsule_distances
tri=[];names=[]
for row in r['added']:
 o=scene.objects[row['object']];T=inv@wm(o);o.data.calc_loop_triangles();v=np.asarray([tuple(T@p.co) for p in o.data.vertices],dtype=float);t=v[np.asarray([tuple(f.vertices) for f in o.data.loop_triangles],dtype=int)];tri.append(t);names.extend([o.name]*len(t))
tri=np.concatenate(tri);names=np.asarray(names);radius=.30;height=1.80;skin=.015
# Segmento estritamente interior do portal; não extrapola o piso do saguão
# nem cria conexão com a praça. CCD adaptativo com limite explícito.
start=np.asarray([3.80,0.,z]);end=np.asarray([5.15,0.,z]);sweep=[]
def interval(t0,t1,depth):
 middle=(t0+t1)/2;p=start+(end-start)*middle;d=capsule_distances(p,tri,radius,height);minimum=float(d.min());index=int(d.argmin())
 if minimum<radius+skin-1e-7:raise AssertionError(('FRONT_CAPSULE_CONTACT',str(names[index]),minimum,middle))
 if minimum-(radius+skin)>np.linalg.norm(end-start)*(t1-t0)/2:
  sweep.append({'t_interval':[t0,t1],'minimum_axis_triangle_distance':minimum,'limiting_object':str(names[index]),'classification':'LOCAL_CLEAR_CONSERVATIVE'});return
 assert depth<18,('NEEDS_REVIEW_CONVERGENCE',t0,t1)
 interval(t0,middle,depth+1);interval(middle,t1,depth+1)
interval(0.,1.,0)
for t in (0.,.25,.5,.75,1.):
 p=start+(end-start)*t
 for angle in [None]+[2*math.pi*k/8 for k in range(8)]:
  xy=Vector((p[0],p[1])) if angle is None else Vector((p[0]+(radius+skin)*math.cos(angle),p[1]+(radius+skin)*math.sin(angle)))
  ns['support_check'](floor,xy,z,'CAPSULE_DISC_LOCAL_FRONT_SUPPORT')
q.update(reopened=True,front_control_residuals=residual,front_contacts=contact,preserved_component_signatures=len(r['preserved_signatures']),archived_reference_count=len(r['archived']),local_capsule_ccd={'radius':radius,'height':height,'skin':skin,'step_candidate':.25,'gravity_controller_executed':False,'start':start.tolist(),'end':end.tolist(),'intervals':sweep,'status':'LOCAL_CLEAR_NEW_FRONT_COMPONENTS_ONLY','not_proven':['full scene sweep','exterior plaza connection','controller','elevator movement','traffic']},surface_checks=ns['support'],scope='Malha e interfaces dos corredores e frente superior; CCD conservativo somente contra as novas nove peças. Preserva bloqueios históricos e não aprova gameplay completo.')
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects_checked':q['objects_checked'],'visible':q['visible_objects_checked'],'preserved':q['preserved_component_signatures'],'front_controls':len(residual),'local_ccd_intervals':len(sweep),'reopened':True}))
