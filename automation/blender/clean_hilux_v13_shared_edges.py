"""Remove faces antigas que sobreviveram em vértices compartilhados."""
import bpy, bmesh, json, hashlib, collections, math
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;o=s.objects['HILUX | CARROCERIA PRINCIPAL']
out=r/'blender/assets/vehicles/rondesp-pickup/hilux_carroceria_v13.blend'
assert not bpy.app.background and Path(bpy.data.filepath).resolve()==out.resolve()
assert s.get('boas_v13_finish_applied') and not s.get('boas_v13_shared_cleanup')
rp=r/'docs/reports/blender/hilux_carroceria_v13.json';report=json.loads(rp.read_text(encoding='utf-8'))
fragments=report['replaced_components']+report['finish']['removed_components']
retired={g.index for g in o.vertex_groups if not g.name.startswith('HILUX13 |') and any(f in g.name for f in fragments)}
new={g.index for g in o.vertex_groups if g.name.startswith('HILUX13 |')}
tags=[{a.group for a in v.groups if a.weight>.001} for v in o.data.vertices]
to_remove=[];distribution=collections.Counter()
for p in o.data.polygons:
    vv=[tags[i] for i in p.vertices]
    old_count=sum(bool(g&retired) for g in vv)
    new_count=sum(bool(g&new) for g in vv)
    votes=collections.Counter(g for vi in vv for g in vi)
    # Faces novas usam identificadores novos, incluindo o contorno soldado.
    # Faces mistas antigas são removidas pela união das chapas já substituídas.
    if old_count>=math.ceil(len(vv)*.70) and new_count<=len(vv)/2:
        to_remove.append(p.index)
        owner=max((g for g in votes if g in retired),key=lambda g:votes[g])
        distribution[o.vertex_groups[owner].name]+=1
bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in to_remove],context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
# Registrar identidade nas faces; grupos de vértices compartilhados não são
# uma identificação suficiente para remover um painel em edições futuras.
attr=o.data.attributes.get('boas_panel_id') or o.data.attributes.new('boas_panel_id','INT','FACE')
tags=[{a.group for a in v.groups if a.weight>.001} for v in o.data.vertices]
gn={g.index:g.name for g in o.vertex_groups}
for p in o.data.polygons:
    votes=collections.Counter(g for i in p.vertices for g in tags[i])
    if votes:
        owner=max(votes,key=lambda g:(votes[g],gn[g].startswith('HILUX13 |')))
        attr.data[p.index].value=owner+1
    else:attr.data[p.index].value=0
o['boas_panel_id_map']=json.dumps({str(g.index+1):g.name for g in o.vertex_groups},ensure_ascii=False)
s['boas_v13_shared_cleanup']=True
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
report['shared_edge_cleanup']={'removed_faces':len(to_remove),'components':dict(distribution),'panel_face_attribute':'boas_panel_id'}
report['base_vertices']=len(o.data.vertices);report['base_faces']=len(o.data.polygons)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();report['source_reopened']=False
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf-8'));data['source_reopened']=True
    rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return None
bpy.app.timers.register(reopen,first_interval=.5)
