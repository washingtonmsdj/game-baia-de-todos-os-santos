"""Conecta a encosta à Ladeira em toda a extensão do corredor modelado."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b12_contencao_estrutural_ladeira.blend')
obj=bpy.data.objects['MVP | terreno corrigido | colisão estática'];mesh=obj.data
rot=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
inv_rot=rot.inverted();inv_obj=obj.matrix_world.inverted()
tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
direction=(inv_obj.to_3x3() @ Vector((0,0,-1))).normalized()
def h(x,y):
    p,n,face,d=tree.ray_cast(inv_obj @ (rot @ Vector((x,y,110))),direction,180)
    return (obj.matrix_world @ p).z if p else None
rows=json.loads((root/'artifacts/lacerda/r30b13_road_extent.json').read_text(encoding='utf8'))
rows=[r for r in rows if -140<=r['y']<=160]
profiles=[]
for r in rows:
    y=r['y'];outer=r['outer_x'];road=r['road_z'];crest=None
    for i in range(10,141):
        x=outer+i*.5;z=h(x,y);later=h(x+3,y)
        if z is not None and later is not None and z>=road+10 and abs(later-z)<=2:
            crest=(x,z);break
    if crest is None:raise RuntimeError(f'Patamar não identificado em y={y}')
    profiles.append((y,outer,road,crest[0],crest[1]))
def profile(y):
    if y<=profiles[0][0]:return profiles[0]
    if y>=profiles[-1][0]:return profiles[-1]
    for a,b in zip(profiles,profiles[1:]):
        if a[0]<=y<=b[0]:
            t=(y-a[0])/(b[0]-a[0]);return tuple(a[i]+t*(b[i]-a[i]) for i in range(5))
    raise RuntimeError('Fora da Ladeira')
original=next(i for i,m in enumerate(mesh.materials) if m and m.name=='MVP | terreno contínuo')
stone=next(i for i,m in enumerate(mesh.materials) if m and m.name=='LAC R30B09 | pedra irregular da contenção')
locked=set()
for p in mesh.polygons:
    if p.material_index not in (original,stone):locked.update(p.vertices)
changed=set();max_raise=0
for v in mesh.vertices:
    if v.index in locked:continue
    q=inv_rot @ (obj.matrix_world @ v.co)
    if not (-140<=q.y<=160):continue
    y,outer,road,crest,top=profile(q.y)
    if not (outer+.08<q.x<crest):continue
    u=(q.x-outer)/(crest-outer)
    target=road+(top-road)*min(1,u**.43)
    blend=min(1,(q.y+140)/10,(160-q.y)/10)
    target=q.z+max(0,blend)*(target-q.z)
    if target<=q.z+.03:continue
    dz=target-q.z;q.z=target
    v.co=inv_obj @ (rot @ q)
    changed.add(v.index);max_raise=max(max_raise,dz)
assert len(changed)>500
repaint=0
for p in mesh.polygons:
    if p.material_index==original and any(i in changed for i in p.vertices):
        p.material_index=stone;repaint+=1
mesh.update()
obj['r30b13_full_ladeira']=True
obj['r30b13_profile']='Perfis de seção da pista existente e primeiro patamar estável da encosta; pista/passeios preservados.'
bpy.context.scene['lacerda_revision']='R30B.13 | encosta contínua ao longo da Ladeira da Montanha'
dest=root/'blender/salvador_lacerda_r30b13_encosta_ladeira_continua.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'changed_terrain_vertices':len(changed),'repainted_faces':repaint,
        'max_raise_m':round(max_raise,2),'profiles':len(profiles),'road_vertices_changed':0,
        'road_width_m':'6.5-7.0 amostrado em secoes de 10 m','classification':'ADAPT_LOCAL',
        'profiles_file':'artifacts/lacerda/r30b13_road_extent.json',
        'note':'Corredor de -140 a 160 m local; base R30B12 preservada; sem deslocar asfalto e passeio.'}
(root/'artifacts/lacerda/r30b13_slope_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
