"""Persistência, topologia e superfície da envoltória B99; sem liberar instalação."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-structure-b99'
ns=runpy.run_path(str(Path(__file__).with_name('validate_lacerda_corridors_b94.py')),init_globals={'BOAS_ENCLOSURE_REVISION':99})
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());cfg=json.loads((out/'controls.json').read_text());scene=bpy.context.scene
sig=ns['sig'];wm=ns['wm'];inv=ns['inv']
for n,s in r['preserved_signatures'].items():assert sig(scene.objects[n])==s,n
for row in r['archived']:
 o=scene.objects[row['object']];assert sig(o)==row['before'] and o.hide_get() and o.hide_render,row['object']
def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
def intersect(a,b,c,d):
 def side(a,b,c):return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
 return side(a,b,c)*side(a,b,d)<-1e-10 and side(c,d,a)*side(c,d,b)<-1e-10
wall=r['added'][0];o=scene.objects[wall['object']];v=[inv@wm(o)@p.co for p in o.data.vertices];n=len(v)//4
outer=[Vector((p.x,p.y)) for p in v[:n]];inner=[Vector((p.x,p.y)) for p in v[n:2*n]]
for loop in (outer,inner):
 for i,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
  for j,(c,d) in enumerate(zip(loop,loop[1:]+loop[:1])):
   if j<=i+1 or (i==0 and j==len(loop)-1):continue
   assert not intersect(a,b,c,d),('SELF_INTERSECTION',i,j)
assert all(inside(p,outer) for p in inner)
control_residual=max(min((p-Vector(x)).length for x in cfg['contour_local']) for p in outer)
assert control_residual<2e-5
thickness=[];closure=[];roof_contacts=[];z0,z1=wall['levels'];tree=ns['tree'](wall['object'])
for i,(a,b) in enumerate(zip(outer,outer[1:]+outer[:1])):
 u=(b-a).normalized();normal=Vector((-u.y,u.x));ai=inner[i];bi=inner[(i+1)%n]
 for t in (.15,.5,.85):
  p=a.lerp(b,t);distance=abs((ai-p).cross(u));thickness.append(distance)
  assert abs(distance-cfg['wall_thickness_candidate'])<2e-5
  for f in (.05,.33,.66,.95):
   z=z0+(z1-z0)*f;start=Vector((p.x-normal.x*.08,p.y-normal.y*.08,z));hit=tree.ray_cast(start,Vector((normal.x,normal.y,0)),.4)
   assert hit[0] is not None,(i,t,z)
   closure.append({'edge':i,'fraction':t,'z':z,'hit_distance_m':hit[3]})
  # Contato arquitetônico: algumas quinas são balanços ou bordas do núcleo.
  # Não fechar automaticamente a cobertura se não houver apoio nesta sondagem.
  xy=p+normal*.075;level=ns['surface_height']('SUPERIOR | piso saguão',xy, cfg['levels']['upper_floor'])
  roof_contacts.append({'edge':i,'fraction':t,'xy':list(xy),'upper_floor_top_z':level,'status':'CONTACT_WITH_EXISTING_UPPER_SLAB' if level is not None else 'NEEDS_REVIEW_NO_SLAB_AT_PROBE'})
floor=r['added'][1];fo=scene.objects[floor['object']];ftree=ns['tree'](floor['object']);zf=cfg['levels']['floor_subsolo01']
floor_support=[];T=inv@wm(fo);fo.data.calc_loop_triangles();fv=[T@p.co for p in fo.data.vertices]
for tri in fo.data.loop_triangles:
 pts=[fv[i] for i in tri.vertices]
 if max(abs(p.z-zf) for p in pts)>1e-4:continue
 p=sum(pts,Vector())/3;hit=ftree.ray_cast(p+Vector((0,0,.1)),Vector((0,0,-1)),.2)
 # Mesma verificação em double usada nas lajes compridas B94–B98.
 # BVH single conserva seu resultado no diagnóstico, sem aumentar skin.
 actual=ns['surface_height'](floor['object'],Vector((p.x,p.y)),zf)
 assert actual is not None and abs(actual-zf)<1e-4,('FLOOR_TRIANGLE_SUPPORT',tri.index,list(p),actual,hit)
 floor_support.append({'xy':[p.x,p.y],'z':actual,'bvh_float_z':hit[0].z if hit[0] else None,'method':'DOUBLE_BARYCENTRIC_TRIANGLE_SURFACE'})
core=scene.objects['LAC R30B08 | apoio oposto | corpo estrutural afunilado'];cb=ns['bounds'](core.name);cx=sum(cb[0])/2;cy=sum(cb[1])/2
assert ftree.ray_cast(Vector((cx,cy,zf+.1)),Vector((0,0,-1)),.4)[0] is None,'Piso não deve preencher núcleo hachurado'
# Distância de superfícies, não interpretar mero contato como penetração.
coretree=ns['tree'](core.name);overlap=tree.overlap(coretree)
q.update(reopened=True,preserved_component_signatures=len(r['preserved_signatures']),archived_reference_count=len(r['archived']),basement_contour_residual_m=control_residual,wall_thickness_range_m=[min(thickness),max(thickness)],wall_closure_rays=closure,floor_support_probes=floor_support,hatched_core_not_filled=True,existing_core_surface_overlap_pairs=len(overlap),existing_core_surface_overlap_classification='NEEDS_REVIEW' if overlap else 'NO_SURFACE_CROSSING_DETECTED',upper_slab_contacts=roof_contacts,absolute_ssot_registration_accepted=False,lower_extrusion_accuracy='APPROXIMATE_16_ENVELOPE_CROSSCHECKED_15',installed_shaft_dimensions_known=False,scope='Envoltória exterior dos subsolos e laje cinza da16. Não mede folgas de instalação, não aprova controller nem implantação absoluta; CCD histórico não repetido porque núcleo/cabine preservados.')
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects_checked':q['objects_checked'],'preserved':len(r['preserved_signatures']),'closure_rays':len(closure),'floor_probes':len(floor_support),'core_surface_overlap_pairs':len(overlap),'reopened':True}))
