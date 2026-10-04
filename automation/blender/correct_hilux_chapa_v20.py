"""Espessura interna e normais ponderadas, na sessão MCP visível."""
import bpy,json,hashlib,os,struct
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_superficies_v19.blend'
target=r/'blender/assets/vehicles/rondesp-pickup/hilux_chapa_v20.blend'
assert not target.exists()
source=Path(bpy.data.filepath);parent_sha=hashlib.sha256(source.read_bytes()).hexdigest()
o=s.objects['HILUX | CARROCERIA PRINCIPAL']
def fingerprint(ob):
 h=hashlib.sha256()
 for v in ob.data.vertices:h.update(struct.pack('<3d',*v.co))
 for p in ob.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
protected={ob.name:fingerprint(ob) for ob in s.objects if ob.type=='MESH'}
checkpoint=r/'artifacts/vehicles/rondesp/v20-live-before.blend'
if not checkpoint.exists():bpy.data.libraries.write(str(checkpoint),{s},path_remap='RELATIVE',compress=True)
else:assert s.name=='HILUX | chapa e portas v20', 'Checkpoint de outra aplicação'
mods=[m for m in o.modifiers if m.type=='SOLIDIFY'];assert len(mods)==1
m=mods[0];before={'offset':0.,'thickness':m.thickness,'use_quality_normals':False,'use_even_offset':False,'solidify_mode':m.solidify_mode}
m.offset=-1.;m.use_quality_normals=True;m.use_even_offset=False
normal=o.modifiers.get('V20 | Normais da chapa por area e angulo') or o.modifiers.new('V20 | Normais da chapa por area e angulo','WEIGHTED_NORMAL')
normal.mode='FACE_AREA_WITH_ANGLE';normal.keep_sharp=True;normal.weight=50
normal.thresh=.01
s.name='HILUX | chapa e portas v20';s['boas_revision_parent']=source.relative_to(r).as_posix()
o['boas_v20_finish']='Espessura mantida inteiramente para dentro; superfície externa preservada; normais por área e ângulo.'
# Mesmo sombreamento neutro; aproximação traseira para revisão do usuário.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active
   sp.region_3d.view_rotation=(Vector((0,.72,1.5))-Vector((3.5,6,3.65))).to_track_quat('-Z','Y')
   sp.region_3d.view_location=(0,.72,1.5);sp.region_3d.view_distance=3.2
   sp.shading.type='SOLID';sp.shading.light='STUDIO';sp.shading.studio_light='paint.sl';sp.shading.color_type='OBJECT'
bpy.context.view_layer.update()
assert all(fingerprint(s.objects[n])==h for n,h in protected.items())
report={'asset_id':'vehicle-rondesp-pickup','file':target.relative_to(r).as_posix(),'scene':s.name,'parent':source.relative_to(r).as_posix(),'parent_sha256':parent_sha,'status':'candidate','authoring_mode':'body_and_doors','base_meshes_unchanged':True,'base_mesh_hashes':protected,'base_vertices':len(o.data.vertices),'base_faces':len(o.data.polygons),'thickness_before':before,'thickness_after':{'offset':m.offset,'thickness':m.thickness,'use_quality_normals':m.use_quality_normals,'use_even_offset':m.use_even_offset},'normal_modifier':{'name':normal.name,'mode':normal.mode,'keep_sharp':normal.keep_sharp,'weight':normal.weight},'live_session':{'pid':os.getpid(),'port':9876},'source_reopened':False,'runtime_exported':False,'visual_review':'pending','notes':['Comparação reversível confirmou marcas criadas pela espessura em offset 0.','A espessura de 2,5 mm é parâmetro candidato de autoria, não medida industrial.','Nenhuma alteração nos contornos, portas, pivôs ou malhas reservadas.','Nenhuma nova deformação ou bevel global.']}
(r/'docs/reports/blender/hilux_chapa_v20.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
print(json.dumps({'file':str(target),'base_meshes_unchanged':True,'offset':m.offset,'normals':normal.mode}))
