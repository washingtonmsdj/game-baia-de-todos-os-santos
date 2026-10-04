"""Estrutura dos batentes e painel curvo da capota; salva e reabre a fonte."""
import bpy,bmesh,math,ast,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
repo=Path(__file__).resolve().parents[2];scene=bpy.context.scene;assert scene.name=='VIATURA | Rondesp Hilux marrom v04'
root=scene.objects['RDP01_ROOT | viatura'];brown=bpy.data.materials['RDP01 | Pintura marrom Rondesp'];black=bpy.data.materials['RDP01 | Polímero preto']
scope=dict(bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,Matrix=Matrix,root=root,brown=brown,black=black,collections={k:bpy.data.collections['RDP01 | '+k] for k in ['CARROCERIA','PORTAS','CAPOTA','VIDROS','RODAS','CHASSIS','LUZES','ACABAMENTOS','INSCRICOES','APRESENTACAO']})
tree=ast.parse((repo/'automation/blender/create_rondesp_pickup_v01.py').read_text(encoding='utf-8'))
for name in ['mesh','box','tube']:
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),'<helper>','exec'),scope)
for side in (-1,1):
    # Batente e soleira são estrutura fixa; as portas continuam separadas.
    scope['box']('HILUX04 | Batente B '+str(side),(side*.833,.108,.90),(.075,.095,.73),brown,'CARROCERIA',.012)
    scope['box']('HILUX04 | Soleira interna '+str(side),(side*.822,.13,.565),(.085,1.98,.12),brown,'CARROCERIA',.012)
    # A tampa de acesso segue o raio da capota, sem triangulação plana atravessando a curva.
    ob=scene.objects.get('RDP01 | Acesso lateral capota '+str(side))
    if ob:
        pts=[v.co.copy() for v in ob.data.vertices]
        cy=sum(p.y for p in pts)/len(pts);cz=sum(p.z for p in pts)/len(pts)
        def point(y,z):
            r=min(.999,max(0,(z-1.195)/.685));x=.889*(1-r*r)**.125+.005
            return(side*x,y,z)
        n=len(pts);vs=[point(cy+(p.y-cy)*r,cz+(p.z-cz)*r) for r in [.12,.40,.70,1] for p in pts]
        fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)]+[tuple(range(n))]
        me=bpy.data.meshes.new(ob.name+' curva');me.from_pydata(vs,[],fs);me.materials.append(brown);me.update()
        bm=bmesh.new();bm.from_mesh(me)
        for f in bm.faces:
            if f.normal.x*side<0:f.normal_flip()
        bm.to_mesh(me);bm.free();ob.data=me
        for p in me.polygons:p.use_smooth=True
        seal=scene.objects.get('RDP01 | Junta acesso capota '+str(side))
        if seal:
            for sp in seal.data.splines:
                for p in sp.points:
                    q=point(p.co.y,p.co.z);p.co.x=q[0]+side*.003
paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata']
mapping=next(n for n in paint.node_tree.nodes if n.type=='MAPPING');mapping.inputs['Rotation'].default_value=(.62,0,0)
for o in scene.objects:
    if o.type=='LIGHT':o.visible_glossy=False
# Mantém geometria visível na janela sem recompilar shaders de viewport.
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1100;scene.render.resolution_y=700
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0
scene.camera.location=(-7,-7,3.0);scene.camera.rotation_euler=(Vector((0,.10,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=6.65
scene.render.filepath=str(repo/'artifacts/vehicles/rondesp/v04-frente-geometria.png');bpy.ops.render.render(write_still=True)
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v04.blend'
bpy.context.view_layer.update();bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
path=repo/'docs/reports/blender/rondesp_marrom_v04.json';r=json.loads(path.read_text(encoding='utf-8'))
r.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),objects=len(scene.objects),final_details=['batentes fixos e soleiras internas','tampa lateral conformada à curvatura','camuflagem diagonal candidata'],material_preview_note='Imagem de materiais anterior ao ajuste dos reflexos, camuflagem e batentes; não evidência da fonte final exata.')
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():bpy.ops.wm.open_mainfile(filepath=str(out));return None
bpy.app.timers.register(reopen,first_interval=.5)
