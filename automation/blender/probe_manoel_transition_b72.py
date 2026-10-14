"""B72: ensaio da chegada Manoel Vitórino, sem alterar a cena."""
import bpy,json,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
src=json.loads((r/'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))['validation_source'];assert src['revision']=='R30B.71'
assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve() and hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
report=json.loads((r/'docs/reports/blender/coastal_road_profiles_b72_probe.json').read_text(encoding='utf8'))
road=next(x for x in report['roads'] if x['osm_way_id']==456471269);contract=json.loads((r/'world/areas/mvp-centro-lacerda/coastal-gameplay-b51.json').read_text(encoding='utf8'));rec=next(x for x in contract['roads'] if x['osm_way_id']==456471269)
hq=s.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];core=s.objects['MVP | terreno corrigido | colisão estática'];hq.data.calc_loop_triangles();core.data.calc_loop_triangles()
xyz=np.array([list(v.co) for v in hq.data.vertices],float);z=xyz[:,2].copy();ff=np.array([list(t.vertices) for t in hq.data.loop_triangles],int)
ct=BVHTree.FromPolygons([core.matrix_world@v.co for v in core.data.vertices],[list(t.vertices) for t in core.data.loop_triangles],all_triangles=True)
seam=json.loads((r/'docs/reports/blender/coastal_seam_r30b58.json').read_text(encoding='utf8'))['physical_boundary_xy']
a=np.array(rec['blender_xy'][0]);b=np.array(rec['blender_xy'][1]);direction=(b-a)/np.linalg.norm(b-a);normal=np.array([-direction[1],direction[0]])
branch_direction=direction.copy();branch_normal=normal.copy()
rec2=next(x for x in contract['roads'] if x['osm_way_id']==154743329);a2=np.array(rec2['blender_xy'][0]);b2=np.array(rec2['blender_xy'][1]);d2=(b2-a2)/np.linalg.norm(b2-a2);n2=np.array([-d2[1],d2[0]])
assert np.linalg.norm(a-a2)<1e-8
direction=branch_direction+d2;direction/=np.linalg.norm(direction);normal=np.array([-direction[1],direction[0]])
half=float(rec['gameplay_width_m'])/2;half2=float(rec2['gameplay_width_m'])/2;end_station=(seam['x']-a[0])/direction[0];ramp_end=end_station-max(half,half2)*abs(normal[0])/direction[0]-.75
z0=road['samples'][0]['center']['z'];p=a+direction*end_station;hit=ct.ray_cast(Vector((float(p[0]+.01),float(p[1]),100)),Vector((0,0,-1)),200)[0];assert hit is not None
zend=float(hit.z);h=1.5;along=(xyz[:,:2]-a)@direction;lateral=(xyz[:,:2]-a)@normal
u=np.clip(along,0,ramp_end)
integral=np.where(u<h,u*u/(2*h),np.where(u<=ramp_end-h,u-h/2,ramp_end-h-(ramp_end-u)**2/(2*h)))
target=z0+(zend-z0)*integral/(ramp_end-h)
branch_lateral=(xyz[:,:2]-a)@branch_normal;branch2_lateral=(xyz[:,:2]-a2)@n2
distance=np.minimum(abs(branch_lateral)-half,abs(branch2_lateral)-half2);wside=np.clip(distance/3,0,1);weights=1-3*wside*wside+2*wside*wside*wside
start=np.clip(along/1.5,0,1);weights*=3*start*start-2*start*start*start
mask=(along>0)&(along<=end_station+2)&(distance<3)&(xyz[:,0]<seam['x']-1e-4)
roles=hq.data.attributes['boas_surface_role'];ids=hq.data.attributes['boas_osm_way_id'];locked=set()
for polygon in hq.data.polygons:
 if roles.data[polygon.index].value in (1,2) and ids.data[polygon.index].value not in (456471269,154743329):locked.update(polygon.vertices)
mask[list(locked)]=False;z[mask]=xyz[mask,2]+weights[mask]*(target[mask]-xyz[mask,2])
candidate=xyz.copy();candidate[:,2]=z;ht=BVHTree.FromPolygons([Vector(p) for p in candidate],[list(map(int,f)) for f in ff],all_triangles=True)
fill=s.objects['B63 | VISUAL | piso contínuo até o cais'];fill.data.calc_loop_triangles();ft=BVHTree.FromPolygons([fill.matrix_world@v.co for v in fill.data.vertices],[list(t.vertices) for t in fill.data.loop_triangles],all_triangles=True)
def support(xy):
 hh=ht.ray_cast(Vector((float(xy[0]),float(xy[1]),150)),Vector((0,0,-1)),300)[0];cc=ct.ray_cast(Vector((float(xy[0]),float(xy[1]),150)),Vector((0,0,-1)),300)[0]
 fh=ft.ray_cast(Vector((float(xy[0]),float(xy[1]),150)),Vector((0,0,-1)),300)[0]
 values=[float(p.z) for p in [hh,cc,fh] if p is not None];return max(values) if values else None
checks=[]
for rr in report['roads']:
 cross=[];missing=0;grades=[];previous=None;points=rr['samples']
 for k,entry in enumerate(points):
  xy=np.array(entry['xy']);center=support(xy)
  d=np.array(points[k+1]['xy'])-xy if k+1<len(points) else xy-np.array(points[k-1]['xy'])
  d=d/np.linalg.norm(d);n=np.array([-d[1],d[0]])
  left=support(xy-n*.825);right=support(xy+n*.825)
  if any(v is None for v in [center,left,right]):missing+=1;previous=None;continue
  cross.append(abs(left-right)/1.65)
  if previous:
   pz,pxy=previous;dist=math.dist(xy,pxy)
   if 1e-8<dist<=1:grades.append(abs(center-pz)/dist)
  previous=center,xy
 checks.append({'osm_way_id':rr['osm_way_id'],'max_grade_before':rr['max_grade'],'max_grade_after':max(grades,default=None),'max_crossfall_before':rr['max_crossfall'],'max_crossfall_after':max(cross,default=None),'missing_supports':missing})
out={'schema':'boas/manoel-transition-b72-candidate-v1','source':src,'osm_way_id':456471269,'classification':'ADAPT_LOCAL','source_reference':'artifacts/structural-pipeline/mvp-centro-lacerda/structural_reference.json','source_width_m':None,'existing_candidate_width_m':half*2,'width_changed':False,'axis_changed':False,'transition_end_station_m':end_station,'profile_flat_station_m':ramp_end,'design_blend_m':3,'design_slope_easing_m':h,'design_crossfall':None,'profile_direction':'bisector_of_shared_osm_branches','shared_osm_node_id':4527284526,'affected_osm_ids':[456471269,154743329],'controls':{'from':[*a,float(z0)],'to':[*p,float(zend)]},'changed_vertices':int(np.count_nonzero(abs(z-xyz[:,2])>1e-5)),'max_z_change_m':float(abs(z-xyz[:,2]).max()),'other_roads_walkable_locked_vertices':len(locked),'other_roads_walkable_max_change_m':float(abs(z[list(locked)]-xyz[list(locked),2]).max()),'profiles':checks,'finite':bool(np.isfinite(z).all()),'geometry_changed':False}
previous_path=r/'docs/reports/blender/manoel_transition_b72_candidate.json'
if previous_path.exists() and not (r/'docs/reports/blender/manoel_transition_b72_rejected.json').exists():(r/'docs/reports/blender/manoel_transition_b72_rejected.json').write_bytes(previous_path.read_bytes())
np.savez_compressed(r/'artifacts/waterfront/manoel_transition_b72.npz',xyz=xyz,z=z,locked=np.array(sorted(locked)))
(r/'docs/reports/blender/manoel_transition_b72_candidate.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(out))
