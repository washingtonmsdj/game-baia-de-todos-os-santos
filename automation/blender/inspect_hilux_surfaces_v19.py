"""Leitura da geometria de autoria para acabamento da Hilux, sem modificar a cena."""
import bpy,bmesh,json,collections,math
from pathlib import Path
from mathutils.kdtree import KDTree
r=Path(__file__).resolve().parents[2];o=bpy.context.scene.objects['HILUX | CARROCERIA PRINCIPAL']
assert not bpy.app.background and Path(bpy.data.filepath).name in {'hilux_portas_v18.blend','hilux_superficies_v19.blend'}
bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
bm.normal_update();fl=bm.faces.layers.int.get('boas_panel_id');labels=json.loads(o['boas_panel_id_map'])
points=KDTree(len(bm.verts))
for v in bm.verts:points.insert(v.co,v.index)
points.balance()
counts=collections.Counter();multi=[];inconsistent=[];tiny=[];wire=[];boundary=[];t_junctions=[];seen=set();duplicates=[]
for f in bm.faces:
    if f.calc_area()<1e-10:tiny.append(f.index)
    key=tuple(sorted(v.index for v in f.verts))
    if key in seen:duplicates.append(f.index)
    seen.add(key)
for e in bm.edges:
    ids=sorted(f[fl] for f in e.link_faces);counts[len(e.link_faces)]+=1
    if len(e.link_faces)>2:multi.append({'edge':e.index,'vertices':[v.index for v in e.verts],'panels':ids})
    if len(e.link_faces)==2 and not e.is_contiguous:inconsistent.append({'edge':e.index,'panels':ids})
    if not e.link_faces:wire.append(e.index)
    if len(e.link_faces)==1:
        boundary.append({'edge':e.index,'vertices':[v.index for v in e.verts],'panels':ids})
        a,b=e.verts;d=b.co-a.co;length=d.length
        if length<1e-7:continue
        for co,i,_ in points.find_range((a.co+b.co)/2,length/2+.00002):
            if i in {a.index,b.index}:continue
            t=(co-a.co).dot(d)/(length*length)
            if .00001<t<.99999 and (co-a.co-d*t).length<.00002:
                t_junctions.append({'edge':e.index,'vertex':i,'t':t,'panels':ids})
near=[]
for v in bm.verts:
    for _,i,d in points.find_range(v.co,.00002):
        if i>v.index:near.append([v.index,i,d])
components=[];unvisited=set(bm.faces)
while unvisited:
    seed=next(iter(unvisited));stack=[seed];unvisited.remove(seed);group=[]
    while stack:
        f=stack.pop();group.append(f)
        for e in f.edges:
            for linked in e.link_faces:
                if linked in unvisited:unvisited.remove(linked);stack.append(linked)
    components.append({'faces':len(group),'panels':dict(collections.Counter(f[fl] for f in group))})
report={'file':Path(bpy.data.filepath).relative_to(r).as_posix(),'vertices':len(bm.verts),'faces':len(bm.faces),
    'has_custom_normals':o.data.has_custom_normals,'edge_face_counts':dict(counts),'multi_edges':multi,
    'inconsistent_winding':inconsistent,'tiny_faces':tiny,'duplicate_faces':duplicates,'wire_edges':wire,
    'coincident_vertices':near,'t_junctions':t_junctions,'boundary_edges':boundary,
    'components':sorted(components,key=lambda p:-p['faces']),'panel_names':labels,
    'geometry':{'vertices':[list(v.co) for v in bm.verts],'faces':[[f[fl],*[v.index for v in f.verts]] for f in bm.faces]}}
name='v19-mesh-after.json' if Path(bpy.data.filepath).name=='hilux_superficies_v19.blend' else 'v19-mesh-before.json'
(r/'artifacts/vehicles/rondesp'/name).write_text(json.dumps(report,ensure_ascii=False),encoding='utf-8');bm.free()

print(json.dumps({'file':bpy.data.filepath,'frame':bpy.context.scene.frame_current,'dirty':bpy.data.is_dirty,'vertices':len(o.data.vertices),'smooth_faces':sum(p.use_smooth for p in o.data.polygons),'sharp_edges':sum(e.use_edge_sharp for e in o.data.edges)}))
