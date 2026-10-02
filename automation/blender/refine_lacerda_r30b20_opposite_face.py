"""Completa na face oposta os grupos de venezianas da torre principal."""
import bpy, bmesh, json
from pathlib import Path
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parents[2]
assert bpy.data.filepath.endswith('salvador_lacerda_r30b19_torre_venezianas.blend')
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
col=bpy.data.collections.new('HERO | Lacerda | venezianas opostas R30B20')
bpy.context.scene.collection.children.link(col)
shadow=bpy.data.materials['LAC R30B19 | fundo escuro veneziana']
slat=bpy.data.materials['LAC R30B19 | veneziana metal grafite']

def boxes(name,items,mat):
    verts=[];faces=[]
    for (cx,cy,cz),(sx,sy,sz) in items:
        n=len(verts);x=sx/2;y=sy/2;z=sz/2
        verts += [R@Vector((cx+dx,cy+dy,cz+dz)) for dx,dy,dz in [(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]]
        faces += [tuple(n+i for i in q) for q in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new('LAC R30B20 | '+name,mesh);col.objects.link(ob)
    mesh.materials.append(mat)
    ob['boas_location_id']='elevador-lacerda';ob['boas_role']='visual_architecture'
    return ob

slots=[];backs=[];blades=[]
for z,h in [(16.0,2.8),(27.2,3.2),(39.0,3.1),(51.0,3.0),(62.4,2.8)]:
    for yc in [2.20,6.20]:
        for j in [-1,0,1]:
            y=yc+j*.49
            slots.append(((-66.90,y,z),(.8,.34,h)))
            backs.append(((-66.995,y,z),(.016,.34,h)))
            n=round(h/.105)
            for k in range(n):blades.append(((-66.785,y,z-h/2+(k+.5)*h/n),(.065,.325,.038)))

wall=bpy.data.objects['CASCA | fachada poço.002']
cutter=boxes('cortador temporario face oposta',slots,shadow)
mod=wall.modifiers.new('Venezianas opostas R30B20','BOOLEAN')
mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.context.view_layer.objects.active=wall
bpy.ops.object.modifier_apply(modifier=mod.name)
me=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(me)
boxes('torre | fundos recuados opostos',backs,shadow)
boxes('torre | laminas venezianas opostas',blades,slat)

bpy.context.scene['lacerda_revision']='R30B.20 | venezianas torre nas duas faces'
dest=ROOT/'blender/salvador_lacerda_r30b20_torre_duas_faces.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
report={'revision':dest.name,'source':'salvador_lacerda_r30b19_torre_venezianas.blend','openings_added':len(slots),'road_or_support_moved':False,'status':'partial'}
(ROOT/'artifacts/lacerda/r30b20_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
