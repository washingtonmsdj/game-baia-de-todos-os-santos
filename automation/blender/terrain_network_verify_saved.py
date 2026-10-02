"""Reabre a revisão real e verifica os apoios da rede viária coberta."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if c['world_source']['revision']!='R30B.29':raise RuntimeError('R30B29 esperada')
bpy.ops.wm.open_mainfile(filepath=str(root/c['world_source']['file']));bpy.context.view_layer.update()
scene=bpy.context.scene;s=scene.objects[c['export']['road_object']];p=scene.objects[c['export']['terrain_proxy']]
def tree(o):
    o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
source=tree(s);proxy=tree(p)
g=json.loads((root/c['staging']['roads']).read_text());n={v['id']:v for v in g['nodes']};a=json.loads((root/'docs/reports/blender/terrain_vehicle_audit_r30b25.json').read_text())
covered={s['edge_id'] for s in a['segments'] if all(x[2] is not None for x in s['samples']) and sum(x[3] is not None for x in s['samples'])/len(s['samples'])>=.95}
seen=set();missing_source=[];missing_proxy=[];maxerror=0;above=0
for e in g['edges']:
    if e['id'] not in covered:continue
    av=Vector((*n[e['from']]['blender_xy'],0));bv=Vector((*n[e['to']]['blender_xy'],0));d=bv-av;f=d.normalized();side=Vector((-f.y,f.x,0));steps=max(1,math.ceil(d.length/1.5))
    for i in range(steps+1):
        center=av.lerp(bv,i/steps)
        for u,v in [(0,0),(-1.61,-.84),(-1.61,.84),(1.61,-.84),(1.61,.84)]:
            q=center+f*u+side*v;key=(round(q.x,5),round(q.y,5))
            if key in seen:continue
            seen.add(key);origin=Vector((q.x,q.y,160));direction=Vector((0,0,-1));z=source.ray_cast(origin,direction,350)[0];pz=proxy.ray_cast(origin,direction,350)[0]
            if z is None:missing_source.append({'edge_id':e['id'],'sample':i,'xy':list(q.to_2d())});continue
            if pz is None:missing_proxy.append({'edge_id':e['id'],'sample':i});continue
            err=abs(z.z-pz.z);maxerror=max(maxerror,err);above+=err>.05
columns=[]
for xy in [(-148.42085,-150.15419),(-148.70,-148.36),(-147.95,-148.76),(-146.267,-146.388)]:
    hits=[];z=160
    for j in range(6):
        q,nrm,index,dist=source.ray_cast(Vector((*xy,z)),Vector((0,0,-1)),350)
        if q is None:break
        hits.append(q.z);z=q.z-.002
    columns.append({'xy':xy,'source_column_hits_z':hits})
r={'source':c['world_source'],'reopened':True,'road_segments':len(covered),'unique_probes':len(seen),'source_missing_boundary_samples':missing_source,'missing_proxy_samples':missing_proxy,'max_visual_collision_delta_m':maxerror,'above_5cm':above,'status':'pass_geometric_agreement_only' if not missing_proxy and not above else 'needs_review','dynamic_physics_tested':False,'source_discontinuities_repaired':False,'conceicao_column_hits':columns}
(root/'docs/reports/blender/terrain_proxy_network_verify.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
rp=root/'docs/reports/blender/terrain_proxy_network_refinement.json';old=json.loads(rp.read_text());old['reopened']=True;old['verification_report']='docs/reports/blender/terrain_proxy_network_verify.json';rp.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(r,ensure_ascii=False))
