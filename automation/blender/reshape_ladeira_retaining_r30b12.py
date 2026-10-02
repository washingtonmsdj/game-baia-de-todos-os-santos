"""Fecha o vale artificial entre Ladeira e Cidade Alta na malha estrutural."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b11_encontro_contecao_passeio.blend')
obj=bpy.data.objects['MVP | terreno corrigido | colisão estática']
mesh=obj.data
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
inv_rot=rot.inverted();inv_obj=obj.matrix_world.inverted()
tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
rows=json.loads((root/'artifacts/lacerda/r30b10_ladeira_edge.json').read_text(encoding='utf8'))
original=next(i for i,m in enumerate(mesh.materials) if m and m.name=='MVP | terreno contínuo')
stone=next(i for i,m in enumerate(mesh.materials) if m and m.name=='LAC R30B09 | pedra irregular da contenção')
def height(x,y):
    o=inv_obj @ (rot @ Vector((x,y,110)))
    d=(inv_obj.to_3x3() @ Vector((0,0,-1))).normalized()
    p,n,face,dist=tree.ray_cast(o,d,180)
    return (obj.matrix_world @ p).z if p else None
profiles=[]
for r in rows:
    y=float(r['y']);outer=float(r['edge_x']);road=float(r['road_z'])
    if not (-60<=y<=80):continue
    crest=None
    for i in range(20,501):
        x=outer+i*.1
        h=height(x,y)
        if h is not None and h>=69:
            crest=x;break
    if crest is None:raise RuntimeError(f'Sem crista em y={y}')
    profiles.append((y,outer,road,crest))
def profile(y):
    if y<=profiles[0][0]:return profiles[0]
    if y>=profiles[-1][0]:return profiles[-1]
    for a,b in zip(profiles,profiles[1:]):
        if a[0]<=y<=b[0]:
            t=(y-a[0])/(b[0]-a[0]);return tuple(a[i]+t*(b[i]-a[i]) for i in range(4))
    raise RuntimeError('Fora da faixa')
locked=set()
for p in mesh.polygons:
    if p.material_index not in (original,stone):locked.update(p.vertices)
changed=set();max_raise=0
for v in mesh.vertices:
    if v.index in locked:continue
    q=inv_rot @ (obj.matrix_world @ v.co)
    if not (-60<=q.y<=80):continue
    y,outer,road,crest=profile(q.y)
    if not (outer+.08<q.x<crest):continue
    u=(q.x-outer)/(crest-outer)
    target=road+(69.5-road)*min(1,u**.40)
    blend=min(1,(q.y+60)/12,(80-q.y)/12)
    target=q.z+(target-q.z)*max(0,blend)
    if target<=q.z+.03:continue
    dz=target-q.z;q.z=target
    v.co=inv_obj @ (rot @ q)
    changed.add(v.index)
    max_raise=max(max_raise,dz)
assert len(changed)>1000
repaint=0
for p in mesh.polygons:
    if p.material_index==original and any(i in changed for i in p.vertices):
        p.material_index=stone;repaint+=1
mesh.update()
obj['r30b12_terrain_reshaped']=True
obj['r30b12_method']='Perfil continuo entre limite externo do passeio existente e primeira cota de 69 m; vertices viarios preservados.'
bpy.context.scene['lacerda_revision']='R30B.12 | contenção estrutural da Ladeira junto à pista'
dest=root/'blender/salvador_lacerda_r30b12_contencao_estrutural_ladeira.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'changed_terrain_vertices':len(changed),'repainted_faces':repaint,
        'max_raise_m':round(max_raise,2),'profiles':len(profiles),'road_vertices_changed':0,
        'classification':'ADAPT_LOCAL','source_cross_sections':'artifacts/lacerda/r30b12_cross_sections.json',
        'reference':'Aleph Ladeira da Montanha, vistas h90 e h180',
        'note':'Malha do terreno e colisor original ajustados; corredor viario de 6.9-7.0 m preservado.'}
(root/'artifacts/lacerda/r30b12_reshape_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
