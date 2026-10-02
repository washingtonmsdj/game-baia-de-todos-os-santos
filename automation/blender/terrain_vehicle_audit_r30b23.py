"""Auditoria de terreno e passagem veicular na composição R30B.23, via MCP.

Sonda um veículo nominal de 2,05 m (asset V14), sem alterar larguras de ruas.
Cobertura geométrica não equivale a simulação dinâmica nem validação cadastral.
"""
import bpy,json,math,time
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
c=json.loads((root/'world/areas/mvp-centro-lacerda/production.json').read_text())
if c['world_source']['revision'] not in ('R30B.23','R30B.24','R30B.25','R30B.29') or Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Auditoria exige a composição selecionada')
bpy.context.view_layer.update();o=bpy.context.scene.objects[c['export']['road_object']]
mesh=o.data;mesh.calc_loop_triangles();ps=[o.matrix_world@v.co for v in mesh.vertices]
road_slots={i for i,m in enumerate(mesh.materials) if m and m.name in c['export']['road_materials']}
if len(road_slots)!=len(c['export']['road_materials']):raise RuntimeError('Binding de pavimento incorreto')
alltris=list(mesh.loop_triangles);roadtris=[t for t in alltris if t.material_index in road_slots]
tree=BVHTree.FromPolygons(ps,[list(t.vertices) for t in alltris],all_triangles=True)
roads=BVHTree.FromPolygons(ps,[list(t.vertices) for t in roadtris],all_triangles=True)
def hit(bvh,x,y):
    result=bvh.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),350)
    return result[0]
graph=json.loads((root/c['staging']['roads']).read_text());nodes={n['id']:n for n in graph['nodes']};ways={w['osm_way_id']:w for w in graph['ways']}
skip={'footway','pedestrian','steps','path','cycleway','bridleway','corridor','construction','proposed'}
results=[];total=0;seen=set()
for edge in graph['edges']:
    way=ways[edge['osm_way_id']]
    if way.get('highway') in skip:continue
    key=tuple(sorted((edge['from'],edge['to'])))
    if key in seen:continue
    seen.add(key)
    a=Vector((*nodes[edge['from']]['blender_xy'],0));b=Vector((*nodes[edge['to']]['blender_xy'],0));delta=b-a;length=delta.length
    if length<.01:continue
    forward=delta.normalized();side=Vector((-forward.y,forward.x,0));steps=max(1,math.ceil(length/1.5));samples=[];issues=[]
    for i in range(steps+1):
        p=a.lerp(b,i/steps);center=hit(tree,p.x,p.y);support=hit(roads,p.x,p.y)
        wheels=[]
        for offset in (-.84,.84):
            q=p+side*offset;w=hit(roads,q.x,q.y);wheels.append(w.z if w else None)
        z=center.z if center else None;sz=support.z if support else None
        samples.append([round(p.x,5),round(p.y,5),z,sz,*wheels]);total+=1
        if not center:issues.append({'sample':i,'type':'missing_ground'})
        elif not support:issues.append({'sample':i,'type':'center_not_on_authored_pavement'})
        elif any(z is None for z in wheels):issues.append({'sample':i,'type':'wheel_outside_authored_pavement'})
        elif abs(wheels[0]-wheels[1])>.18:issues.append({'sample':i,'type':'crossfall_review','delta_m':round(abs(wheels[0]-wheels[1]),4)})
        if i and z is not None and samples[i-1][2] is not None:
            grade=(z-samples[i-1][2])/(length/steps)
            if abs(grade)>.20:issues.append({'sample':i,'type':'grade_review','grade':round(grade,5)})
            if i>1 and samples[i-2][2] is not None:
                previous=(samples[i-1][2]-samples[i-2][2])/(length/steps)
                if abs(grade-previous)>.10:issues.append({'sample':i,'type':'profile_kink_review','grade_delta':round(abs(grade-previous),5)})
    results.append({'edge_id':edge['id'],'osm_way_id':edge['osm_way_id'],'name':way.get('name'),'highway':way.get('highway'),'width_verified_m':way.get('width_m_tagged'),'length_m':length,'issues':issues,'samples':samples})
degenerate=sum((ps[t.vertices[1]]-ps[t.vertices[0]]).cross(ps[t.vertices[2]]-ps[t.vertices[0]]).length<1e-9 for t in alltris)
counts=Counter(issue['type'] for r in results for issue in r['issues'])
vehicles=[{'name':x.name,'type':x.type} for x in bpy.context.scene.objects if any(s in x.name.lower() for s in ('carro','veicul','ordax car','car v14'))][:12]
report={'source':c['world_source'],'terrain_vertices':len(ps),'terrain_triangles':len(alltris),'degenerate_triangles':degenerate,'road_triangles':len(roadtris),'unique_road_segments':len(results),'samples':total,'spacing_max_m':1.5,'wheel_track_probe_m':1.68,'vehicle_width_nominal_m':2.05,'widths_changed':False,'xy_changed':False,'issue_counts':dict(counts),'vehicle_candidates':vehicles,'classification':'NEEDS_REVIEW','test_kind':'static wheel support sweep; not a dynamic driving test','segments':results}
suffix=c['world_source']['revision'].lower().replace('.','')
path=root/f'docs/reports/blender/terrain_vehicle_audit_{suffix}.json';path.write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='segments'},ensure_ascii=False))
