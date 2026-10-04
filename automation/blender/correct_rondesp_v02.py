"""Corrige bind dos pivôs e pintura da primeira versão; preserva v01."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
repo=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(repo/'blender/assets/vehicles/rondesp-pickup/marrom_v01.blend').resolve()
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v02.blend'
assert not out.exists(),'Não repetir uma revisão já salva.'
fixed=[]
global_parts=('Pneu ','Aro borda ','Relevo lateral pneu ','Braço aço aro ','Porta dianteira ','Porta traseira ','Caixilho porta ','Vidro porta ','Vedação porta ')
for o in scene.objects:
    if o.parent and o.name.startswith('RDP01 | ') and any(o.name.startswith('RDP01 | '+p) for p in global_parts):
        # Os vértices/pontos já estão em coordenadas de veículo. O inverse deve
        # neutralizar a posição inicial do pivô, mantendo rotação futura ao redor dele.
        o.matrix_parent_inverse=o.parent.matrix_basis.inverted()
        o.matrix_basis=Matrix.Identity(4)
        o['boas_bind_fix']='v02: coordenadas de veículo, inverse do pivô inicial'
        fixed.append(o.name)
# Maçanetas e pneus de tread têm geometria local e bind já derivado dos operadores.
# Mantê-los preserva seus centros e transformações corretos.
paint=bpy.data.materials['RDP01 | Camuflagem marrom candidata']
wave=next(n for n in paint.node_tree.nodes if n.type=='TEX_WAVE')
wave.inputs['Scale'].default_value=.26
wave.inputs['Distortion'].default_value=.25
for o in scene.objects:
    if o.name.startswith('RDP01 | Disco freio'):
        o.data.materials[0]=bpy.data.materials['RDP01 | Aço preto rodas']
# As inscrições acompanham as respectivas folhas, em vez de permanecerem na carroceria.
bpy.context.view_layer.update()
for side in (-1,1):
    piv=scene.objects[f'RDP01 | Pivô porta dianteira {side:+}']
    ob=scene.objects['RDP01 | POLÍCIA MILITAR '+str(side)]
    # Esta faixa cruza duas folhas; continua como inscrição própria estática até
    # divisão do UV/livery na preparação da animação, registrada como pendente.
    ob['boas_animation_detail_status']='pending; inscrição atravessa duas folhas'
wheel_check=[]
for side in (-1,1):
    for ai,y in enumerate((-1.43,1.655)):
        tire=scene.objects[f'RDP01 | Pneu {ai} {side:+}']
        points=[tire.matrix_world@v.co for v in tire.data.vertices]
        mins=[min(p[i] for p in points) for i in range(3)]
        maxs=[max(p[i] for p in points) for i in range(3)]
        center=Vector([(a+b)/2 for a,b in zip(mins,maxs)])
        target=Vector((side*.825,y,.415))
        assert (center-target).length<.0001,(tire.name,center,target)
        assert abs(mins[2]-.01)<.0001
        wheel_check.append({'name':tire.name,'center':list(center),'ground_clearance_m':mins[2]})
scene.name='VIATURA | Rondesp picape marrom v02'
scene['boas_revision']='v02'
scene['boas_revision_parent']='blender/assets/vehicles/rondesp-pickup/marrom_v01.blend'
scene['boas_revision_corrections']='bind das malhas a pivôs de rodas/portas; camuflagem de frequência corrigida'
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.show_specular_highlight=True
scene.display.shading.background_type='WORLD'
scene.render.resolution_x=1100;scene.render.resolution_y=730
scene.render.resolution_percentage=100
scene.camera.location=(-8,-5.6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale=6.65
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            s=a.spaces.active;s.shading.type='SOLID';s.shading.color_type='MATERIAL'
            s.region_3d.view_rotation=scene.camera.rotation_euler.to_quaternion()
            s.region_3d.view_location=(0,0,1);s.region_3d.view_distance=7;s.region_3d.view_perspective='ORTHO'
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
previous=json.loads((repo/'docs/reports/blender/rondesp_marrom_v01.json').read_text(encoding='utf-8'))
previous.update({'file':out.relative_to(repo).as_posix(),'scene':scene.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'revision_parent':'blender/assets/vehicles/rondesp-pickup/marrom_v01.blend','bind_fixed':fixed,'wheel_centers_verified':wheel_check,'visual_review':'pending','reopened':'pending'})
(repo/'docs/reports/blender/rondesp_marrom_v02.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Render de geometria: não depende de shaders transparentes/compilação da GPU.
folder=repo/'artifacts/vehicles/rondesp';folder.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(folder/'v02-frente-geometria.png')
bpy.ops.render.render(write_still=True)
scene.camera.location=(-7,6,3.15)
scene.camera.rotation_euler=(Vector((0,0,1.02))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(folder/'v02-traseira-geometria.png')
bpy.ops.render.render(write_still=True)
