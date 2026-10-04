"""Fecha correções visíveis da revisão candidata, sem promover para runtime."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.name=='VIATURA | Rondesp picape marrom v03'
root=scene.objects['RDP01_ROOT | viatura']
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v03.blend'
black=bpy.data.materials['RDP01 | Polímero preto'];brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp'];glass=bpy.data.materials['RDP01 | Vidro fumê']

def part(name,vs,fs,mat,group,thickness=0,parent=root):
    me=bpy.data.meshes.new('RDP03 | '+name);me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new('RDP03 | '+name,me);bpy.data.collections['RDP01 | '+group].objects.link(ob);me.materials.append(mat)
    ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_basis.inverted();ob.matrix_basis=Matrix.Identity(4)
    if thickness:
        mod=ob.modifiers.new('Espessura fabricação','SOLIDIFY');mod.thickness=thickness;mod.offset=0
    ob['boas_asset_id']='vehicle-rondesp-pickup'
    return ob

def tube(name,pts,mat,group,parent,rad=.01):
    cu=bpy.data.curves.new('RDP03 | '+name,'CURVE');cu.dimensions='3D';cu.bevel_depth=rad;cu.bevel_resolution=3
    s=cu.splines.new('POLY');s.points.add(len(pts)-1)
    for p,co in zip(s.points,pts):p.co=(*co,1)
    s.use_cyclic_u=True
    ob=bpy.data.objects.new(cu.name,cu);bpy.data.collections['RDP01 | '+group].objects.link(ob);cu.materials.append(mat)
    ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_basis.inverted();ob.matrix_basis=Matrix.Identity(4)

# Corrige orientação perdida pelos operadores na primeira geração.
for ob in scene.objects:
    if any(ob.name.startswith('RDP01 | '+p) for p in ('Cubo roda ','Disco freio ','Porca roda ')):
        ob.rotation_euler=(0,math.pi/2,0)

# Janelas com cantos arredondados e caixilhos reais, seguindo os limites fotografados.
polys={'dianteira':[(-.865,1.31),(-.37,1.845),(.065,1.86),(.065,1.31)],'traseira':[(.083,1.31),(.083,1.86),(.93,1.81),(1.035,1.31)]}
for side in (-1,1):
    for label,poly in polys.items():
        for prefix in ('Caixilho porta ','Vidro porta ','Vedação porta '):
            ob=scene.objects.get(f'RDP01 | {prefix}{label} {side:+}')
            if ob:bpy.data.objects.remove(ob,do_unlink=True)
        outer=[]
        for i,p in enumerate(poly):
            cur=Vector(p);prev=Vector(poly[i-1]);nxt=Vector(poly[(i+1)%len(poly)])
            a=cur+(prev-cur)*.065;b=cur+(nxt-cur)*.065
            for k in range(9):
                t=k/8;outer.append((1-t)**2*a+2*t*(1-t)*cur+t*t*b)
        cy=sum(p.x for p in outer)/len(outer);cz=sum(p.y for p in outer)/len(outer)
        inner=[Vector((cy+(p.x-cy)*.935,cz+(p.y-cz)*.89)) for p in outer]
        def point(p,offset=0):
            y,z=p;x=.923-max(0,z-1.31)*.267+offset
            return (side*x,y,z)
        verts=[point(p) for p in outer+inner];n=len(outer)
        pivot=scene.objects[f'RDP01 | Pivô porta {label} {side:+}']
        part(f'Caixilho curvo {label} {side:+}',verts,[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],brown,'PORTAS',.015,pivot)
        part(f'Vidro curvo {label} {side:+}',[point(p,-.004) for p in inner],[tuple(range(n))],glass,'VIDROS',.005,pivot)
        tube(f'Borracha janela {label} {side:+}',[point(p,.002) for p in inner],black,'VIDROS',pivot,.009)

# A frente passa a ter recortes próprios para os faróis, sem lentes sobre corpo opaco.
ob=scene.objects.get('RDP01 | Máscara dianteira')
if ob:bpy.data.objects.remove(ob,do_unlink=True)
verts=[];nx=48;nz=28
for j in range(nz+1):
    z=.555+.70*j/nz
    for i in range(nx+1):
        u=-1+2*i/nx
        x=.91*u
        y=-2.733+.10*abs(u)**3+.017*math.cos((z-.8)*5)
        verts.append((x,y,z))
faces=[]
for j in range(nz):
    for i in range(nx):
        ids=(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i)
        c=sum((Vector(verts[k]) for k in ids),Vector())/4
        if abs(c.x)>.585 and c.z>1.015:continue
        faces.append(ids)
nose=part('Frente para-choque curvo com recortes',verts,faces,brown,'CARROCERIA',.018)
for p in nose.data.polygons:p.use_smooth=True
for side in (-1,1):
    fender=scene.objects[f'RDP01 | Para-lama dianteiro {side:+}']
    bm=bmesh.new();bm.from_mesh(fender.data)
    cut=[f for f in bm.faces if f.calc_center_median().y<-2.275 and f.calc_center_median().z>1.07]
    bmesh.ops.delete(bm,geom=cut,context='FACES');bm.to_mesh(fender.data);bm.free()
    for x,delta in [(.735,.028),(.843,.065)]:
        ob=scene.objects['RDP01 | Refletor farol '+str(side)+str(x)]
        ob.location.y+=delta

# Material contínuo evita os degraus de cor do preview por faces.
paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata']
wave=next(n for n in paint.node_tree.nodes if n.type=='TEX_WAVE')
wave.inputs['Scale'].default_value=.20;wave.inputs['Distortion'].default_value=.17
for ob in scene.objects:
    if ob.type=='MESH' and any(ob.name.startswith(p) for p in ('RDP01 | Porta dianteira','RDP01 | Porta traseira','RDP01 | Para-lama dianteiro','RDP01 | Caçamba','RDP03 | Capô abaulado','RDP01 | Tampa traseira caçamba')):
        ob.data.materials.clear();ob.data.materials.append(paint)
        for p in ob.data.polygons:p.material_index=0

scene.camera.location=(-8,-5.6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=10;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1000;scene.render.resolution_y=665
scene.view_settings.exposure=.5
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            s=a.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL';s.overlay.show_overlays=False
            s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion();s.region_3d.view_location=(0,0,1);s.region_3d.view_distance=7;s.region_3d.view_perspective='ORTHO'
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
path=repo/'docs/reports/blender/rondesp_marrom_v03.json'
report=json.loads(path.read_text(encoding='utf-8'))
report.update({'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'vehicle_objects':len(scene.objects)-5,'corrections_finish':['normais/orientação cubos e porcas','cantos arredondados janelas','aberturas reais faróis','camuflagem contínua sem degraus de cor']})
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    return None
bpy.app.timers.register(reopen,first_interval=.5)
