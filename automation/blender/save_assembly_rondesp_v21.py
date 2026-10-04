"""Salvar e apresentar V21 montada sem sobrescrever a oficina V20."""
import bpy,hashlib,json,os,struct
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_chapa_v20.blend'
assert s.get('boas_v21_glazing_finish') and not bpy.app.is_job_running('RENDER')
out=r/'blender/assets/vehicles/rondesp-pickup/marrom_v21_montada.blend';assert not out.exists()
rp=r/'docs/reports/blender/rondesp_marrom_v21.json';report=json.loads(rp.read_text(encoding='utf8'))
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
assert all(fingerprint(s.objects[n])==h for n,h in report['protected_mesh_hashes'].items())
# Coleções restauradas saem da reserva; o legado permanece desabilitado.
stash=bpy.data.collections['RDP01 | PECAS RESERVADAS']
for col in list(stash.children):
 if col.name=='RDP01 | PORTAS':continue
 if col.name not in s.collection.children:s.collection.children.link(col)
 stash.children.unlink(col)
stash.hide_viewport=True;stash.hide_render=True
s.name='VIATURA | Rondesp Hilux marrom v21';s['boas_revision_parent']=report['parent'];s['boas_review_status']='candidate; complete material assembly review'
s['boas_authoring_notes']='V21: carroceria e quatro folhas V20 preservadas. Rodas, chassi, interior, capota, luzes e acessórios remontados. Vidros ajustados, adesivos conformados e separados nas portas. Materiais originais/procedurais candidatos, sem nova imagem raster. Não exportado ao runtime.'
s['boas_authoring_mode']='assembled_review'
s.frame_set(1)
for ob in s.objects:
 if ob.type=='EMPTY' and 'abertura_graus' in ob:ob['abertura_graus']=0.
# Motor leve para a vista traseira; a vista frontal usa Cycles com transmissão.
for engine in ['BLENDER_EEVEE_NEXT','BLENDER_EEVEE']:
 try:s.render.engine=engine;break
 except TypeError:continue
else:raise RuntimeError('Eevee indisponível')
if hasattr(s,'eevee'):
 if hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=32
 if hasattr(s.eevee,'use_raytracing'):s.eevee.use_raytracing=False
s.render.resolution_x=1280;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.exposure=.4
cam=s.camera;cam.location=(-7,-8,3.1);cam.rotation_euler=(Vector((0,.15,1.03))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.8
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.shading.type='MATERIAL';sp.shading.use_scene_lights=False;sp.shading.use_scene_world=False
   studio=bpy.context.preferences.studio_lights.get('studio.exr')
   if studio:sp.shading.studio_light=studio.name
   sp.shading.studiolight_rotate_z=.6;sp.overlay.show_overlays=False
   sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.region_3d.view_location=(0,.15,1.03);sp.region_3d.view_distance=7.;sp.region_3d.view_perspective='PERSP'
report.update({'file':out.relative_to(r).as_posix(),'scene':s.name,'base_body_and_doors_unchanged':True,'objects':len(s.objects),'visible_objects':sum(o.visible_get() for o in s.objects),'live_session':{'pid':os.getpid(),'port':9876},'preview_front':'artifacts/vehicles/rondesp/v21-frente-materiais.png','preview_rear':'artifacts/vehicles/rondesp/v21-traseira-materiais.png','visual_review':'front inspected; rear pending','render_note':'Frente: Cycles 20 amostras; traseira: Eevee 32, sem traçado de raios.','pending':['Fidelidade fina de carroceria/capota ainda candidata.','Brasão vetorial simplificado; microdetalhes e camuflagem exata pendentes.','Montagem de revisão, sem certificação física completa ou exportação.']})
# A fonte é salva antes da vista adicional, evitando dependência de um render longo.
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Fonte V21 salva: '+report['sha256'])
cam.location=(-7,8,3.25);cam.rotation_euler=(Vector((0,.25,1.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.7
s.render.filepath=str(r/report['preview_rear']);bpy.ops.render.render(write_still=True)
# Reabrir a fonte salva com o enquadramento frontal e pintura visível.
def reopen():
 bpy.ops.wm.open_mainfile(filepath=str(out));data=json.loads(rp.read_text(encoding='utf8'))
 data['source_reopened']=Path(bpy.data.filepath).resolve()==out.resolve()
 data['protected_meshes_verified_after_reopen']=all(fingerprint(bpy.context.scene.objects[n])==h for n,h in data['protected_mesh_hashes'].items())
 data['source_sha256_after_reopen']=hashlib.sha256(out.read_bytes()).hexdigest()
 rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return None
bpy.app.timers.register(reopen,first_interval=.5)
print(json.dumps({'file':str(out),'objects':len(s.objects),'body_and_doors_preserved':True,'rear_view':str(r/report['preview_rear'])}))
