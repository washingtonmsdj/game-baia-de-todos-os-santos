"""Corrige a precisão local do proxy em todas as vias já cobertas pela fonte.

Não deforma a cidade, não inventa largura e não aprova perfis incorretos.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if c['world_source']['revision']!='R30B.28' or Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Fonte R30B28 esperada')
s=bpy.context.scene.objects[c['export']['road_object']];p=bpy.context.scene.objects[c['export']['terrain_proxy']]
if p.parent or any(abs(p.matrix_basis[i][j]-(1 if i==j else 0))>1e-7 for i in range(4) for j in range(4)):raise RuntimeError('Transform proxy inválido')
s.data.calc_loop_triangles();ground=BVHTree.FromPolygons([s.matrix_world@v.co for v in s.data.vertices],[list(t.vertices) for t in s.data.loop_triangles],all_triangles=True)
def height(v):
    q=ground.ray_cast(Vector((v.x,v.y,160)),Vector((0,0,-1)),350)[0]
    if q:return q.z
    probes=[]
    for dx,dy in [(.002,0),(-.002,0),(0,.002),(0,-.002),(.002,.002),(-.002,.002),(.002,-.002),(-.002,-.002)]:
        q=ground.ray_cast(Vector((v.x+dx,v.y+dy,160)),Vector((0,0,-1)),350)[0]
        if q:probes.append(q)
    return min(probes,key=lambda q:abs(q.z-v.z)).z if probes else None
g=json.loads((root/c['staging']['roads']).read_text());n={v['id']:v for v in g['nodes']}
a=json.loads((root/'docs/reports/blender/terrain_vehicle_audit_r30b25.json').read_text())
covered={s['edge_id'] for s in a['segments'] if all(x[2] is not None for x in s['samples']) and sum(x[3] is not None for x in s['samples'])/len(s['samples'])>=.95}
points={};missing=[];edgecount=0
for e in g['edges']:
    if e['id'] not in covered:continue
    av=Vector((*n[e['from']]['blender_xy'],0));bv=Vector((*n[e['to']]['blender_xy'],0));d=bv-av;f=d.normalized();side=Vector((-f.y,f.x,0));steps=max(1,math.ceil(d.length/1.5));edgecount+=1
    for i in range(steps+1):
        center=av.lerp(bv,i/steps)
        for u,v in [(0,0),(-1.61,-.84),(-1.61,.84),(1.61,-.84),(1.61,.84)]:
            q=center+f*u+side*v;z=height(q)
            if z is None:missing.append({'edge_id':e['id'],'sample':i,'xy':list(q.to_2d())});continue
            points[(round(q.x,5),round(q.y,5))]=(q,z)
points=list(points.values());iterations=[];tol=.05;before_vertices=len(p.data.vertices);before_faces=len(p.data.polygons)
for it in range(12):
    p.data.calc_loop_triangles();tris=list(p.data.loop_triangles);tree=BVHTree.FromPolygons([v.co for v in p.data.vertices],[list(t.vertices) for t in tris],all_triangles=True);bad=set();maxerror=0;nohit=0
    for q,z in points:
        hit,normal,index,d=tree.ray_cast(Vector((q.x,q.y,160)),Vector((0,0,-1)),350)
        if hit is None:nohit+=1;continue
        error=abs(hit.z-z);maxerror=max(maxerror,error)
        if error>tol:bad.add(tris[index].polygon_index)
    row={'iteration':it,'bad_faces':len(bad),'maximum_error_m':maxerror,'missing_proxy_samples':nohit};iterations.append(row);print(json.dumps(row))
    if nohit:raise RuntimeError('Proxy sem apoio interno: não promover')
    if not bad:break
    if it==11:raise RuntimeError('Precisão não atingida: não promover')
    bm=bmesh.new();bm.from_mesh(p.data);bm.faces.ensure_lookup_table();edges={e for id in bad for e in bm.faces[id].edges};old=set(bm.verts)
    bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=True)
    for v in set(bm.verts)-old:
        z=height(v.co)
        if z is None:bm.free();raise RuntimeError('Vértice novo sem fonte: não promover')
        v.co.z=z
    bm.to_mesh(p.data);bm.free();p.data.update()
p['boas_refinement']='adaptive local source projection at existing road vehicle support samples; no road width or visual terrain modification'
p['boas_support_source']=s.name;p['boas_validation_scope']='geometric agreement only; Conceição height conflict and dynamic vehicle clearance pending'
r={'source_before':c['world_source'].copy(),'classification':'ERROR','method':'adaptive local collider refinement; source visual geometry unchanged','road_segments':edgecount,'samples':len(points),'source_missing_boundary_samples':missing,'tolerance_m':tol,'iterations':iterations,'vertices_before':before_vertices,'vertices_after':len(p.data.vertices),'faces_before':before_faces,'faces_after':len(p.data.polygons),'city_visual_geometry_changed':False,'road_widths_changed':False,'dynamic_physics_tested':False,'runtime_exported':False,'reopened':False}
out=root/'blender/salvador_lacerda_r30b29_colisao_rede_viaria.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));c['world_source'].update(file=out.relative_to(root).as_posix(),sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),revision='R30B.29',selection_reason='Derivada da R30B23; conserva geografia/larguras e corrige precisão local da colisão nas vias cobertas. Conflito de níveis da Conceição continua em revisão.');cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['source_after']=c['world_source'];(root/'docs/reports/blender/terrain_proxy_network_refinement.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in r.items() if k!='source_missing_boundary_samples'},ensure_ascii=False))
