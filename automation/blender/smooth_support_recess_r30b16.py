"""Suaviza o recorte da escarpa ao redor do apoio sem tocar na via."""
import bpy,json
from pathlib import Path
from mathutils import Matrix

root=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b15_apoio_original_encosta_recortada.blend')
obj=bpy.data.objects['MVP | terreno corrigido | colisão estática'];mesh=obj.data
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z').inverted()
rows=json.loads((root/'artifacts/lacerda/r30b10_ladeira_edge.json').read_text(encoding='utf8'))
edges=[(float(r['y']),float(r['edge_x'])) for r in rows]
def edge(y):
    for (a,x),(b,z) in zip(edges,edges[1:]):
        if a<=y<=b:return x+(z-x)*(y-a)/(b-a)
    return edges[0][1] if y<edges[0][0] else edges[-1][1]
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
original=next(i for i,m in enumerate(mesh.materials) if m and m.name=='MVP | terreno contínuo')
stone=next(i for i,m in enumerate(mesh.materials) if m and m.name=='LAC R30B09 | pedra irregular da contenção')
locked=set()
for p in mesh.polygons:
    if p.material_index not in (original,stone):locked.update(p.vertices)
adj=[set() for _ in mesh.vertices]
for e in mesh.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a)
weights={};core=set()
for v in mesh.vertices:
    if v.index in locked:continue
    p=rot @ obj.matrix_world @ v.co
    if not (-32<p.y<40 and -36<p.x<-2):continue
    if -27.5<p.x<-12 and -2<p.y<11:
        core.add(v.index);continue
    w=smooth((p.y+32)/12)*smooth((40-p.y)/12)
    w*=smooth((p.x-edge(p.y)-.5)/2)*smooth((-2-p.x)/6)
    if w>.001:weights[v.index]=w
assert len(weights)>100
for _ in range(18):
    old=[v.co.z for v in mesh.vertices]
    updates={}
    for i,w in weights.items():
        ns=adj[i]
        if not ns:continue
        average=sum(old[j] for j in ns)/len(ns)
        updates[i]=old[i]+.48*w*(average-old[i])
    for i,z in updates.items():mesh.vertices[i].co.z=z
mesh.update()
obj['r30b16_smoothing']='Laplace local com base do apoio e vertices viarios fixos; nao altera objetos separados.'
bpy.context.scene['lacerda_revision']='R30B.16 | apoio original e escarpa sem serrilhado'
dest=root/'blender/salvador_lacerda_r30b16_apoio_encosta_suavizada.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'smoothed_vertices':len(weights),'pinned_support_vertices':len(core),
        'iterations':18,'road_vertices_changed':0,'classification':'ADAPT_LOCAL',
        'note':'Suavização estrutural local da malha; apoio mantém implantação original.'}
(root/'artifacts/lacerda/r30b16_smoothing_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
