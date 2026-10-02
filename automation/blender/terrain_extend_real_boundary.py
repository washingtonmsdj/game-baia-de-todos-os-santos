"""Completa chão cortado pelo recorte, na conexão OSM da Praça Castro Alves.

Extensão integrada às malhas existentes. Não cria via, não muda largura,
não resolve por este passe o conflito de níveis da Conceição.
"""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text());before=c['world_source'].copy()
if before['revision']!='R30B.29' or Path(bpy.data.filepath).resolve()!=(root/before['file']).resolve():raise RuntimeError('Fonte R30B29 esperada')
bpy.context.view_layer.update();s=bpy.context.scene.objects[c['export']['road_object']];p=bpy.context.scene.objects[c['export']['terrain_proxy']]
s.data.calc_loop_triangles();tree=BVHTree.FromPolygons([s.matrix_world@v.co for v in s.data.vertices],[list(t.vertices) for t in s.data.loop_triangles],all_triangles=True)
south=min((s.matrix_world@v.co).y for v in s.data.vertices)
def height(x,y):
    q=tree.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),350)[0]
    if q is None:raise RuntimeError('Seção existente sem apoio')
    return q.z
# Margem de quatro metros: crop corta 1,30 m do nó real; sobra para a
# sondagem do carro V14 (meia distância entre eixos 1,61 m). Não é largura.
extent=4.;xmin=-234.;xmax=-210.;changes=[]
for o in (s,p):
    bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();inv=o.matrix_world.inverted()
    boundary=[e for e in bm.edges if len(e.link_faces)==1 and all(abs((o.matrix_world@v.co).y-south)<.003 for v in e.verts) and xmin<=(sum((o.matrix_world@v.co).x for v in e.verts)/2)<=xmax]
    if not boundary:bm.free();raise RuntimeError('Borda aberta de origem não identificada: '+o.name)
    oldverts=len(bm.verts);oldfaces=len(bm.faces);rings={};newfaces=0
    for v in {v for e in boundary for v in e.verts}:
        q=o.matrix_world@v.co
        z0=height(q.x,south+.005);z1=height(q.x,south+2.)
        grade=(z0-z1)/1.995
        row=[v]
        for j in range(1,5):
            row.append(bm.verts.new(inv@Vector((q.x,south-j,z0+grade*j))))
        rings[v]=row
    for e in boundary:
        a,b=e.verts;mat=e.link_faces[0].material_index
        # A face antiga determina a ordem da aresta: continuidade normal/topológica.
        loop=next(l for l in e.link_faces[0].loops if l.edge==e)
        a=loop.vert;b=loop.link_loop_next.vert
        for j in range(4):
            face=bm.faces.new((rings[b][j],rings[a][j],rings[a][j+1],rings[b][j+1]));face.material_index=mat;newfaces+=1
    bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
    o['boas_boundary_extension_osm_ids']='1075624458,421206045; shared node 619722483'
    o['boas_boundary_extension_classification']='ADAPT_LOCAL'
    o['boas_boundary_extension_method']='Recorte ampliado 4 m; seção e materiais autorais continuados, sem deslocar vértices anteriores ou alterar larguras. Altimetria extrapolada local, não medida.'
    o['boas_boundary_extension_report']='docs/reports/blender/terrain_real_boundary_extension.json'
    changes.append({'object':o.name,'vertices_before':oldverts,'vertices_after':len(o.data.vertices),'faces_before':oldfaces,'faces_after':len(o.data.polygons),'boundary_edges':len(boundary),'new_faces':newfaces})
scene=bpy.context.scene;scene['boas_terrain_revision']='R30B.30 | recorte da conexão real Praça Castro Alves / Conceição'
report={'source_before':before,'classification':'ADAPT_LOCAL','source_capture_id':'aleph-20260924T205631Z-aqqo7pkx','osm_way_ids':[1075624458,421206045],'shared_osm_node':'619722483','source_road_width_m':None,'width_status':'author_mesh_preserved; not a measured real-world width','extent_south_m':extent,'x_range_m':[xmin,xmax],'existing_vertices_moved':0,'new_road_graph_edges':0,'road_widths_changed':False,'method':'Integrate strips into existing boundary edges of visual terrain and separate simplified collider; continue authored section height tangents/materials. Local height is adaptation, not surveyed altitude.','changes':changes,'conceicao_height_conflict_repaired':False,'closed_circuit_approved':False,'bus_clearance_tested':False,'runtime_exported':False,'reopened':False}
text=bpy.data.texts.new('R30B30 | TERRENO | recorte real e limites');text.write(json.dumps(report,ensure_ascii=False,indent=2))
dest=root/'blender/salvador_lacerda_r30b30_conexao_real_recorte.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report['candidate_file']=dest.relative_to(root).as_posix();report['candidate_sha256']=hashlib.file_digest(dest.open('rb'),'sha256').hexdigest()
(root/'docs/reports/blender/terrain_real_boundary_extension.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
