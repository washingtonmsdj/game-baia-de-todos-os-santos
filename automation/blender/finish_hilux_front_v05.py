"""Recorte exato da máscara, continuidade de chapas e comparação da revisão V05."""
import bpy,bmesh,math,ast,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene;assert scene.name=='VIATURA | Rondesp Hilux marrom v05'
scope=dict(bpy=bpy,bmesh=bmesh,math=math,Vector=Vector)
tree=ast.parse((repo/'automation/blender/sculpt_hilux_front_v05.py').read_text(encoding='utf-8'))
for name in ['inside','nose']:
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<shape>','exec'),scope)
inside,nose=scope['inside'],scope['nose']
skin=next(o for o in scene.objects if 'HILUX05 | Nariz esculpido' in o.name)
shell=next(o for o in scene.objects if 'HILUX05 | Casca orgânica' in o.name)
outer=[Vector((v.co.x,v.co.z)) for v in list(shell.data.vertices)[:113]]
holes=[]
for side in (-1,1):
    ob=next(o for o in scene.objects if 'HILUX04 | Farol lente '+str(side) in o.name)
    holes.append([Vector((v.co.x,v.co.z)) for v in ob.data.vertices])
mask=next(o for o in scene.objects if 'Moldura envolvente STD' in o.name)
holes.append([Vector((v.co.x,v.co.z)) for v in list(mask.data.vertices)[len(mask.data.vertices)//2:]])
pts=[];edges=[]
for loop in [outer]+holes:
    base=len(pts);pts.extend(loop);edges.extend((base+i,base+(i+1)%len(loop)) for i in range(len(loop)))
pts.extend(Vector((v.co.x,v.co.z)) for v in skin.data.vertices)
coords,edges,faces,*_=delaunay_2d_cdt(pts,edges,[],0,1e-6)
def keep(f):
    p=sum((coords[k] for k in f),Vector((0,0)))/len(f)
    return inside(p,outer) and not any(inside(p,h) for h in holes)
faces=[f for f in faces if keep(f)]
me=bpy.data.meshes.new(skin.name+' recortes');me.from_pydata([(p.x,nose(p.x,p.y),p.y) for p in coords],[],faces);me.materials.append(skin.data.materials[0])
bm=bmesh.new();bm.from_mesh(me)
for f in bm.faces:
    if f.normal.y>0:f.normal_flip()
bm.to_mesh(me);bm.free();skin.data=me
for p in me.polygons:p.use_smooth=True
skin['boas_apertures']='Faróis e máscara STD com contornos explícitos, triangulação restrita e cavidades reais'

# Coloca as inscrições sobre as superfícies curvas definitivas, com distância física de decal.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
for o in scene.objects:
    if o.type!='MESH' or not any(c.name in ['RDP01 | CARROCERIA','RDP01 | PORTAS'] for c in o.users_collection):continue
    ev=o.evaluated_get(dg);m=ev.to_mesh();base=len(vs)
    vs.extend(ev.matrix_world@v.co for v in m.vertices);fs.extend(tuple(base+i for i in p.vertices) for p in m.polygons);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vs,fs)
for o in scene.objects:
    if o.type!='MESH' or not o.get('boas_inscription_text'):continue
    for v in o.data.vertices:
        p=o.matrix_world@v.co;side=1 if p.x>0 else -1
        hit,normal,index,d=bvh.ray_cast(Vector((side*2,p.y,p.z)),Vector((-side,0,0)),2)
        if hit is not None:v.co=o.matrix_world.inverted()@(hit+Vector((side*.0012,0,0)))
    o.data.update()
scene.render.engine='BLENDER_WORKBENCH';scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0
for label,pos in [('frente',(-7,-7,2.75)),('lateral',(-9,0,1.1)),('frontal',(0,-9,1.20))]:
    scene.camera.location=pos;scene.camera.rotation_euler=(Vector((0,.1,1.01))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.6 if label!='frontal' else 4.8
    scene.render.filepath=str(repo/f'artifacts/vehicles/rondesp/v05-{label}-geometria.png');bpy.ops.render.render(write_still=True)
scene.camera.location=(-7,-7,2.75);scene.camera.rotation_euler=(Vector((0,.1,1.01))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.6
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v05.blend'
bpy.context.view_layer.update();bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
path=repo/'docs/reports/blender/rondesp_marrom_v05.json';r=json.loads(path.read_text(encoding='utf-8'));r['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();r['visual_review']='Vistas frontal, lateral e oblíqua; candidata sem aprovação final';r['apertures']=skin['boas_apertures']
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
