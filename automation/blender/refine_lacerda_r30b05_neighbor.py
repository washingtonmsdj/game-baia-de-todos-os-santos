"""Sobrado azul adjacente; leitura fotográfica candidata sobre footprint existente."""
import bpy,bmesh,ast,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2]
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
col=bpy.data.collections['ENVIRONMENT_FINAL | comercio Lacerda R30B05'];before=set(col.objects)
ivory=bpy.data.materials['LAC R30B | reboco marfim fino'];dark=bpy.data.materials['LAC R30B | sombra veneziana']
blue=bpy.data.materials.new('ENTORNO LAC | azul sobrado adjacente');blue.diffuse_color=(.49,.65,.73,1);blue.use_nodes=True
next(n for n in blue.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=blue.diffuse_color
base=next(o for o in bpy.data.objects if str(o.get('osm_way_id',''))=='1220650665');base.data.materials.clear();base.data.materials.append(blue)
a=Vector((-76.243,26.987,0));b=Vector((-74.685,33.998,0));t=(b-a).normalized();normal=Vector((-t.y,t.x,0));L=(b-a).length
tree=ast.parse((ROOT/'automation/blender/refine_lacerda_r30b05_commerce.py').read_text(encoding='utf8'))
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name=='parts':exec(compile(ast.Module(body=[node],type_ignores=[]),'<parts>','exec'))
parts('Sobrado azul | cornijas',[(L/2,16.14,L+.16,.24,.24,.08),(L/2,13.55,L,.13,.16,.08),(L/2,10.25,L,.16,.19,.08)],ivory)
parts('Sobrado azul | portais terreo',[((j+.5)*L/3,8.7,1.45,2.6,.07,.05) for j in range(3)],dark)
verts=[];faces=[];rings=[];ringfaces=[]
for z in [10.85,13.75]:
    for j in range(3):
        s=(j+.5)*L/3;w=1.2;h=1.9
        def contour(width,height):
            rad=width/2
            return [(s-rad,z),(s+rad,z)]+[(s+rad*math.cos(i*math.pi/12),z+height-rad+rad*math.sin(i*math.pi/12)) for i in range(13)]
        inner=contour(w,h);outer=[(s+(ss-s)*(w+.18)/w,z-.08+(zz-z)*(h+.16)/h) for ss,zz in inner]
        k=len(verts);verts.extend(tuple(R@(a+t*ss+normal*.055+Vector((0,0,zz)))) for ss,zz in inner);faces.append(tuple(range(k,k+len(inner))))
        k=len(rings);rings.extend(tuple(R@(a+t*ss+normal*.105+Vector((0,0,zz)))) for ss,zz in outer+inner);n=len(inner)
        for q in range(n):r=(q+1)%n;ringfaces.append((k+q,k+r,k+n+r,k+n+q))
for name,vv,ff,mat in [('Sobrado azul | janelas arqueadas',verts,faces,dark),('Sobrado azul | molduras de arco',rings,ringfaces,ivory)]:
    me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.materials.append(mat);o=bpy.data.objects.new('ENTORNO LAC | '+name,me);col.objects.link(o)
for o in set(col.objects)-before:
    o['osm_way_id']='1220650665';o['boas_role']='visual_environment';o['classification']='ADAPT_LOCAL';o['reference_status']='candidate';o['identity_note']='Correspondência arquitetônica candidata ao sobrado azul contíguo da foto; identidade comercial não atribuída.'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Sobrado azul refinado; footprint e altura preservados.')
