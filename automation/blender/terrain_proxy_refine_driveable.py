"""Refino adaptativo local do collider onde ele atravessa as vias verificadas."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if c['world_source']['revision']!='R30B.27':raise RuntimeError('R30B27 esperada')
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Fonte ativa incorreta')
scene=bpy.context.scene;source=scene.objects[c['export']['road_object']];proxy=scene.objects[c['export']['terrain_proxy']]
if proxy.parent or any(abs(proxy.matrix_basis[i][j]-(1 if i==j else 0))>1e-7 for i in range(4) for j in range(4)):raise RuntimeError('Proxy precisa de transform aplicado')
source.data.calc_loop_triangles();ground=BVHTree.FromPolygons([source.matrix_world@v.co for v in source.data.vertices],[list(t.vertices) for t in source.data.loop_triangles],all_triangles=True)
def height(p):
    hit=ground.ray_cast(Vector((p.x,p.y,160)),Vector((0,0,-1)),350)[0]
    if hit is None:
        nearby=[]
        for dx,dy in [(.002,0),(-.002,0),(0,.002),(0,-.002),(.002,.002),(-.002,.002),(.002,-.002),(-.002,-.002)]:
            q=ground.ray_cast(Vector((p.x+dx,p.y+dy,160)),Vector((0,0,-1)),350)[0]
            if q:nearby.append(q)
        if nearby:hit=min(nearby,key=lambda q:abs(q.z-p.z))
    return hit.z if hit else None
graph=json.loads((root/c['staging']['roads']).read_text());nodes={n['id']:n for n in graph['nodes']};ways={w['osm_way_id']:w for w in graph['ways']};points=[]
for e in graph['edges']:
    if 'Montanha' not in (ways[e['osm_way_id']].get('name') or '') and e['id']!='way-231091555-seg-5':continue
    a=Vector((*nodes[e['from']]['blender_xy'],0));b=Vector((*nodes[e['to']]['blender_xy'],0));d=b-a;steps=max(1,math.ceil(d.length/1.5));n=Vector((-d.y,d.x,0)).normalized()
    for i in range(steps+1):
        for offset in [-.84,0,.84]:
            p=a.lerp(b,i/steps)+n*offset;z=height(p)
            if z is None:raise RuntimeError('Referência sem suporte')
            points.append((p,z))
before_vertices=len(proxy.data.vertices);before_faces=len(proxy.data.polygons);iterations=[];threshold=.05
for iteration in range(9):
    proxy.data.calc_loop_triangles();triangles=list(proxy.data.loop_triangles);tree=BVHTree.FromPolygons([v.co for v in proxy.data.vertices],[list(t.vertices) for t in triangles],all_triangles=True);bad=set();maxerror=0;missing=0
    for p,z in points:
        hit,n,index,d=tree.ray_cast(Vector((p.x,p.y,160)),Vector((0,0,-1)),350)
        if hit is None:missing+=1;continue
        error=abs(hit.z-z);maxerror=max(maxerror,error)
        if error>threshold:bad.add(triangles[index].polygon_index)
    iterations.append({'iteration':iteration,'bad_faces':len(bad),'maximum_error_m':maxerror,'missing_samples':missing})
    if missing:raise RuntimeError('Collider sem apoio; não preencher por aproximação')
    if not bad:break
    if iteration==8:raise RuntimeError('Refino ainda acima da tolerância; revisão não promovida')
    bm=bmesh.new();bm.from_mesh(proxy.data);bm.faces.ensure_lookup_table();edges={e for id in bad for e in bm.faces[id].edges};before=set(bm.verts)
    bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=1,use_grid_fill=True)
    for v in set(bm.verts)-before:
        z=height(v.co)
        if z is None:
            (root/'artifacts/terrain-vehicle/refinement-missing.json').write_text(json.dumps({'point':list(v.co),'iteration':iteration,'iterations':iterations}),encoding='utf8');bm.free();raise RuntimeError('Novo vértice sem fonte')
        v.co.z=z
    bm.to_mesh(proxy.data);bm.free();proxy.data.update()
proxy['boas_refinement']='local adaptive subdivision where verified driving route differs >5 cm from source; no visual mesh duplication';proxy['boas_support_source']=source.name
r={'source_before':c['world_source'].copy(),'city_visual_geometry_changed':False,'road_widths_changed':False,'classification':'ERROR','method':'adaptive subdivision of affected collision faces; project only new vertices to authored ground','samples':len(points),'tolerance_m':threshold,'iterations':iterations,'vertices_before':before_vertices,'vertices_after':len(proxy.data.vertices),'faces_before':before_faces,'faces_after':len(proxy.data.polygons),'runtime_exported':False,'dynamic_physics_tested':False}
out=root/'blender/salvador_lacerda_r30b28_colisao_viaria_refinada.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));c['world_source'].update(file=out.relative_to(root).as_posix(),sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),revision='R30B.28',selection_reason='Derivada da R30B23; encontro contínuo e colisor com transform aplicado/refino local nas vias da Montanha. Geometria visual, implantação e larguras preservadas; demais ruas ainda em revisão.');cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['source_after']=c['world_source'];(root/'docs/reports/blender/terrain_proxy_refinement.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r,ensure_ascii=False))
