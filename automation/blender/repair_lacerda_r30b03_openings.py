"""Corrige orientação dos sólidos de corte e reaplica aberturas visuais."""
import bpy,bmesh,ast
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
col=bpy.data.collections['HERO | Lacerda | fachadas e acessos R30B03']
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
ivory=bpy.data.materials['LAC R30B | reboco marfim fino']
source=ast.parse((ROOT/'automation/blender/refine_lacerda_r30b03_exterior.py').read_text(encoding='utf8'))
for node in source.body:
    if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'<helpers>','exec'))
walls=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('SUPERIOR | lateral corpo elevado','SUPERIOR | parede lateral saguão','FACHADA SUPERIOR | corpo elevado'))]
for o in walls+list(col.objects):
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
for wall in walls:
    wb=bb(wall)
    if wall.name.startswith('FACHADA SUPERIOR'):
        for win in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('FACHADA SUPERIOR | janela')]:
            b=bb(win);y0,y1=b[1];z0,z1=b[2];cut(wall,(-.6,(y0+y1)/2,(z0+z1)/2),(2,y1-y0,z1-z0))
    elif 'corpo elevado' in wall.name:
        wy=sum(wb[1])/2
        for win in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('EDIFICIO | janela lateral')]:
            b=bb(win)
            if abs(sum(b[1])/2-wy)<.7:cut(wall,(sum(b[0])/2,wy,sum(b[2])/2),(b[0][1]-b[0][0],1,b[2][1]-b[2][0]))
    else:
        x0,x1=wb[0];y=sum(wb[1])/2;span=(x1-x0-.9)/3
        for j in range(3):
            a=x0+.45+j*span+.14;end=x0+.45+(j+1)*span-.14;cut(wall,((a+end)/2,y,72.65),(end-a,.8,2.7))
for o in col.objects:
    if 'degrau ' in o.name:
        b=bb(o);bottom,top=b[2]
        for v in o.data.vertices:
            if abs(v.co.z-bottom)<.01:v.co.z=86.8
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Normais corrigidas e vãos reaplicados.')
