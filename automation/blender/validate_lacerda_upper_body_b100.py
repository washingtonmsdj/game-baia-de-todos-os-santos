"""Malha, persistência, vãos e pavimentos B100; sem aprovação da instalação."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-upper-body-b100'
ns=runpy.run_path(str(Path(__file__).with_name('validate_lacerda_corridors_b94.py')),init_globals={'BOAS_ENCLOSURE_REVISION':100})
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());cfg=json.loads((out/'controls.json').read_text());before=json.loads((out/'before.json').read_text());scene=bpy.context.scene
sig=ns['sig'];wm=ns['wm'];inv=ns['inv'];rows={v['object']:v for v in before['rows']}
for n,s in r['preserved_signatures'].items():assert sig(scene.objects[n])==s,n
for row in r['archived']:
 o=scene.objects[row['object']];assert sig(o)==row['before'] and o.hide_get() and o.hide_render,row['object']
rigid=[]
for group,control in cfg['facade_transforms'].items():
 R=control['rotation'];t=control['translation']
 for name in control['objects']:
  o=scene.objects[name];actual=[inv@wm(o)@v.co for v in o.data.vertices];old=rows[name];shift=cfg['second_window_row_shift'] if sum(old['bounds'][2])/2>70.12300872802734+8 else 0.
  expected=[Vector((R[0][0]*p[0]+R[0][1]*p[1]+t[0],R[1][0]*p[0]+R[1][1]*p[1]+t[1],p[2]+shift)) for p in old['vertices_local']]
  assert len(actual)==len(expected)
  error=max((p-v).length for p,v in zip(actual,expected));assert error<3e-5,(name,error)
  edges={tuple(sorted((a,b))) for f in old['faces'] for a,b in zip(f,f[1:]+f[:1])}
  distortion=max(abs((actual[a]-actual[b]).length-(Vector(old['vertices_local'][a])-Vector(old['vertices_local'][b])).length) for a,b in edges)
  assert distortion<3e-5,(name,distortion)
  rigid.append({'object':name,'facade':group,'control_residual_m':error,'max_edge_length_change_m':distortion,'z_shift':shift})
body='B100 | cidade alta | corpo superior contínuo';bt=ns['tree'](body);outer=[Vector(p) for p in cfg['body_contour_local']];heights=[cfg['levels']['body_bottom']+.15,cfg['levels']['floor1']-.1,cfg['levels']['floor2']-.1,cfg['levels']['roof_bottom']-.12]
wall_probes=[];roof_probes=[];apertures=[];floor_probes=[]
for i,(a,b) in enumerate(zip(outer,outer[1:]+outer[:1])):
 u=(b-a).normalized();normal=Vector((-u.y,u.x));length=(b-a).length
 for fraction in (.05,.25,.5,.75,.95):
  p=a.lerp(b,fraction)
  for z in heights:
   hole=any(v['edge']==i and v['u'][0]<fraction<v['u'][1] and v['z'][0]<z<v['z'][1] for v in r['window_openings'])
   start=Vector((p.x-normal.x*.1,p.y-normal.y*.1,z));hit=bt.ray_cast(start,Vector((normal.x,normal.y,0)),.6)
   assert (hit[0] is None)==hole,(i,fraction,z,hole,hit)
   wall_probes.append({'edge':i,'fraction':fraction,'z':z,'expected':'WINDOW_APERTURE' if hole else 'WALL','hit_distance':hit[3] if hit[0] else None})
  xy=p+normal*.22;actual=ns['surface_height']('SUPERIOR | cobertura corpo elevado',xy,cfg['levels']['roof_top'])
  assert actual is not None and abs(actual-cfg['levels']['roof_top'])<1e-4,(i,fraction,actual)
  roof_probes.append({'edge':i,'fraction':fraction,'xy':list(xy),'z':actual})
for v in r['window_openings']:
 a=outer[v['edge']];b=outer[(v['edge']+1)%len(outer)];p=a.lerp(b,sum(v['u'])/2);u=(b-a).normalized();normal=Vector((-u.y,u.x));z=sum(v['z'])/2
 assert bt.ray_cast(Vector((p.x-normal.x*.12,p.y-normal.y*.12,z)),Vector((normal.x,normal.y,0)),.6)[0] is None,v
 # Esquadria efetivamente ligada à face, não só um vão vazio.
 wt=ns['tree'](v['window']);hit=wt.ray_cast(Vector((p.x-normal.x*.35,p.y-normal.y*.35,z)),Vector((normal.x,normal.y,0)),.7)
 assert hit[0] is not None,('GLAZING_NOT_AT_APERTURE',v['window'],list(p),z)
 glass=ns['bounds'](v['window']);floor=cfg['levels']['floor1'] if z<cfg['levels']['floor2'] else cfg['levels']['floor2']
 assert glass[2][0]>floor,('GLAZING_BELOW_FLOOR',v['window'],glass,floor)
 apertures.append({'window':v['window'],'body_aperture_clear':True,'glass_present':True,'glazing_bottom_z':glass[2][0],'floor_z':floor,'sill_candidate_m':glass[2][0]-floor})
for label,key in [('01','floor1'),('02','floor2')]:
 name='B100 | cidade alta | laje administrativa '+label;o=scene.objects[name];T=inv@wm(o);points=[T@v.co for v in o.data.vertices];o.data.calc_loop_triangles();level=cfg['levels'][key]
 for tri in o.data.loop_triangles:
  p=[points[i] for i in tri.vertices]
  if max(abs(v.z-level) for v in p)>1e-4:continue
  mid=sum(p,Vector())/3;actual=ns['surface_height'](name,Vector((mid.x,mid.y)),level)
  assert actual is not None and abs(actual-level)<1e-4
  floor_probes.append({'object':name,'xy':[mid.x,mid.y],'top_z':actual,'offset_from_upper_floor':actual-70.12300872802734})
 # Todos os vértices da laje ficam do lado administrativo, sem preencher
 # a caixa antiga, área técnica ou escada.
 assert min(p.x for p in points)>-10.2,name
roof_vertices=[inv@wm(scene.objects['SUPERIOR | cobertura corpo elevado'])@v.co for v in scene.objects['SUPERIOR | cobertura corpo elevado'].data.vertices]
roof_residual=max(min((Vector((p.x,p.y))-Vector(control)).length for p in roof_vertices) for control in cfg['roof_contour_local'])
assert roof_residual<2e-5
q.update(reopened=True,preserved_component_signatures=len(r['preserved_signatures']),archived_reference_count=len(r['archived']),rigid_facade_checks=rigid,body_wall_probes=wall_probes,body_roof_contacts=roof_probes,window_apertures=apertures,admin_floor_probes=floor_probes,roof_document_residual_m=roof_residual,vertical_floor_difference_m=cfg['levels']['floor2']-cfg['levels']['floor1'],absolute_ssot_registration_accepted=False,scope='Corpo superior, cobertura, lajes administrativas e esquadrias herdadas em migração rígida; preserva mapa/torres/instalação/proxyB82. Não certifica implantação absoluta, layout das janelas, instalação ou controller.')
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects_checked':q['objects_checked'],'visible':q['visible_objects_checked'],'rigid_parts':len(rigid),'wall_probes':len(wall_probes),'roof_contacts':len(roof_probes),'window_apertures':len(apertures),'floor_probes':len(floor_probes),'reopened':True}))
