"""Mantém apoio no lugar original e reconstitui o recorte real da encosta ao redor."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector

root=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b14_apoio_encosta_ladeira.blend')
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
inv=rot.inverted()
names=[
    'LAC R30B08 | apoio oposto | corpo estrutural afunilado',
    'LAC R30B08 | apoio oposto | capitel sob passarela',
    'LAC R30B08 | apoio oposto | ressalto transversal',
]
for name in names:
    obj=bpy.data.objects[name]
    obj.data=obj.data.copy()
    for v in obj.data.vertices:
        q=inv @ (obj.matrix_world @ v.co)
        q.x+=25
        if name==names[0] and abs(q.z-7.26)<.05:q.z=21
        v.co=obj.matrix_world.inverted() @ (rot @ q)
    obj.data.update()
    obj['r30b15_placement']='Implantação original do apoio, mantida; encosta recortada em torno dele.'
support=bpy.data.objects[names[0]]
support['ground_sample_min_z']=21.0
support['design_note']='Local original preservado, com corpo parcialmente engastado na encosta e face exposta.'

terrain=bpy.data.objects['MVP | terreno corrigido | colisão estática']
source=root/'blender/salvador_lacerda_r30b11_encontro_contecao_passeio.blend'
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
    dst.objects=[terrain.name]
baseline=dst.objects[0]
assert baseline and len(baseline.data.vertices)==len(terrain.data.vertices)
rows=json.loads((root/'artifacts/lacerda/r30b10_ladeira_edge.json').read_text(encoding='utf8'))
edges=[(float(r['y']),float(r['edge_x'])) for r in rows]
def edge(y):
    if y<=edges[0][0]:return edges[0][1]
    if y>=edges[-1][0]:return edges[-1][1]
    for (a,x),(b,z) in zip(edges,edges[1:]):
        if a<=y<=b:return x+(z-x)*(y-a)/(b-a)
    raise RuntimeError('fora da faixa')
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
original=next(i for i,m in enumerate(terrain.data.materials) if m and m.name=='MVP | terreno contínuo')
stone=next(i for i,m in enumerate(terrain.data.materials) if m and m.name=='LAC R30B09 | pedra irregular da contenção')
locked=set()
for p in terrain.data.polygons:
    if p.material_index not in (original,stone):locked.update(p.vertices)
changed=0;max_cut=0
for v in terrain.data.vertices:
    if v.index in locked:continue
    q=inv @ (terrain.matrix_world @ v.co)
    if not (-25<q.y<32):continue
    outer=edge(q.y)
    if not (outer+.7<q.x<-2):continue
    wx=smooth((q.x-(outer+.7))/2.8)*smooth((-2-q.x)/8)
    wy=smooth((q.y+25)/18)*smooth((32-q.y)/18)
    weight=wx*wy
    if weight<.001:continue
    source_z=baseline.data.vertices[v.index].co.z
    dz=(source_z-v.co.z)*weight
    if abs(dz)<.02:continue
    v.co.z+=dz;changed+=1;max_cut=max(max_cut,-dz)
assert changed>100
terrain.data.update()
bpy.data.objects.remove(baseline,do_unlink=True)
terrain['r30b15_support_recess']='Relevo original restaurado ao redor do apoio; transição suave para contenção junto ao passeio.'
bpy.context.scene['lacerda_revision']='R30B.15 | apoio original exposto por recorte da encosta'
dest=root/'blender/salvador_lacerda_r30b15_apoio_original_encosta_recortada.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'support_moved_from_original':False,'terrain_vertices_cut':changed,
        'max_cut_m':round(max_cut,2),'road_vertices_changed':0,'source_terrain':source.name,
        'classification':'ADAPT_LOCAL','note':'Recorte local na malha original da encosta; pista e passeio preservados.'}
(root/'artifacts/lacerda/r30b15_support_cut_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
