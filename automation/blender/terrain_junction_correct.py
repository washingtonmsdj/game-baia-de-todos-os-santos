"""Regulariza encontro confirmado, alterando somente Z e preservando todo XY.

Perfil local dos três eixos reais; raio de correção não define largura de pista.
Fonte R30B23 preservada. Apenas pavimento existente e seus vértices compartilhados.
"""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if c['world_source']['revision']!='R30B.23':raise RuntimeError('Aplicar uma única vez sobre R30B23')
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Fonte ativa incorreta')
scene=bpy.context.scene;o=scene.objects[c['export']['road_object']];mesh=o.data;mesh.calc_loop_triangles();positions=[o.matrix_world@v.co for v in mesh.vertices];before=[tuple(v.co) for v in mesh.vertices]
slots={i for i,m in enumerate(mesh.materials) if m and m.name in c['export']['road_materials']};roadids={i for f in mesh.polygons if f.material_index in slots for i in f.vertices}
tree=BVHTree.FromPolygons(positions,[list(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
graph=json.loads((root/c['staging']['roads']).read_text());nodes={n['id']:n for n in graph['nodes']};edges={e['id']:e for e in graph['edges']}
ids=['way-48846625-seg-9','way-231091555-seg-5','way-978481515-seg-0'];segments=[]
for id in ids:
    e=edges[id];a=Vector((*nodes[e['from']]['blender_xy'],0));b=Vector((*nodes[e['to']]['blender_xy'],0))
    for p in (a,b):
        q=tree.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),250)[0]
        if q is None:raise RuntimeError('Anchor sem suporte')
        p.z=q.z
    segments.append((a,b))
center=Vector((*nodes['2394997055']['blender_xy'],0));radius=18.0
def profile(p):
    candidates=[]
    for a,b in segments:
        d=b-a;length2=d.x*d.x+d.y*d.y;t=max(0,min(1,((p.x-a.x)*d.x+(p.y-a.y)*d.y)/length2));x=a.x+d.x*t;y=a.y+d.y*t;distance=math.hypot(p.x-x,p.y-y);candidates.append((distance,a.z+d.z*t))
    weights=[1/(.25+v[0])**4 for v in candidates]
    return sum(v[1]*w for v,w in zip(candidates,weights))/sum(weights)
targets={};maxdelta=0
for id in roadids:
    p=positions[id];distance=math.hypot(p.x-center.x,p.y-center.y)
    if distance>=radius or not 53<p.z<63:continue
    blend=max(0,min(1,(radius-distance)/5));blend=blend*blend*(3-2*blend);z=p.z+(profile(p)-p.z)*blend
    if abs(z-p.z)>1.5:raise RuntimeError('Correção local excede envelope; revisar manualmente')
    if abs(z-p.z)>1e-5:targets[id]=z;maxdelta=max(maxdelta,abs(z-p.z))
if not targets:raise RuntimeError('Sem alteração real')
# Original grid has repeated vertices at material seams: synchronize only exact
# XY coincidences at the same level, never cliff geometry or lower roads.
seams={}
for id,z in targets.items():
    p=positions[id];seams.setdefault((round(p.x,5),round(p.y,5)),[]).append((p.z,z))
inverse=o.matrix_world.inverted();changed=0
for id,p in enumerate(positions):
    z=targets.get(id)
    if z is None:
        options=seams.get((round(p.x,5),round(p.y,5)),[]);near=[q for q in options if abs(q[0]-p.z)<.02]
        if near:z=sum(q[1] for q in near)/len(near)
    if z is not None:
        original_xy=mesh.vertices[id].co.xy.copy();local=inverse@Vector((p.x,p.y,z));mesh.vertices[id].co.z=local.z
        if mesh.vertices[id].co.xy!=original_xy:raise RuntimeError('XY alterado')
        changed+=1
mesh.update()
assert all(v.co.x==before[i][0] and v.co.y==before[i][1] for i,v in enumerate(mesh.vertices))
o['boas_terrain_correction']='ERROR: encontro Montanha/Pau da Bandeira; regularização Z local sobre eixos OSM existentes, XY/materiais/topologia preservados'
# Sync the existing gameplay proxy at changed coordinates only, no global ray
# reprojection or dense visual-mesh collider replacement.
proxy=scene.objects[c['export']['terrain_proxy']];pinv=proxy.matrix_world.inverted();proxychanged=0
for v in proxy.data.vertices:
    p=proxy.matrix_world@v.co;distance=math.hypot(p.x-center.x,p.y-center.y)
    if distance>=radius or not 53<p.z<63:continue
    ground=tree.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),250)[0]
    if ground is None or abs(ground.z-p.z)>.4:continue
    # Apply the same delta where the old ground was classified as pavement.
    ray=tree.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),250);tri=mesh.loop_triangles[ray[2]]
    if tri.material_index not in slots:continue
    blend=max(0,min(1,(radius-distance)/5));blend=blend*blend*(3-2*blend);z=p.z+(profile(p)-p.z)*blend
    v.co.z=(pinv@Vector((p.x,p.y,z))).z;proxychanged+=1
proxy.data.update();proxy['boas_correction_source']=o.name
report={'source_before':c['world_source'].copy(),'classification':'ERROR','method':'perfil local dos três eixos sobre anchors da malha-fonte; apenas Z do pavimento existente','osm_edge_ids':ids,'junction_osm_node':'2394997055','radius_m':radius,'radius_is_road_width':False,'widths_changed':False,'xy_changed':False,'materials_changed':False,'topology_changed':False,'changed_vertices':changed,'changed_proxy_vertices':proxychanged,'max_height_change_m':maxdelta,'anchors':[{'a':list(a),'b':list(b)} for a,b in segments],'vehicle_retest':'pending','visual_review':'pending','runtime_exported':False}
output=root/'blender/salvador_lacerda_r30b24_encontro_montanha.blend';bpy.ops.wm.save_as_mainfile(filepath=str(output))
c['world_source'].update(file=output.relative_to(root).as_posix(),sha256=hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),revision='R30B.24',selection_reason='Derivada da R30B23 escolhida pelo usuário; correção Z local do encontro Montanha/Pau da Bandeira sem alterar limites XY ou larguras. Revisão parcial, reteste pendente.')
cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8');report['source_after']=c['world_source'];(root/'docs/reports/blender/terrain_junction_correction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
