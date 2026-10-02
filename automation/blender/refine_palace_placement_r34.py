"""Corrige conversão local→mundo do corpo novo detectada na revisão visual."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];p=root/'docs/reports/blender/palacio_rio_branco_r30b34.json';r=json.loads(p.read_text(encoding='utf8'))
assert not r.get('body_transform_refinement'),'Correção já aplicada'
o=bpy.context.scene.objects[r['palace']['object']];T=Matrix(r['palace']['frame_world'])
zmin=min((o.matrix_world@v.co).z for v in o.data.vertices)
assert zmin<1,'Corpo já está no nível da praça; não transformar novamente'
o.data.transform(o.matrix_world.inverted()@T);o.data.update();bpy.context.view_layer.update()
r['body_transform_refinement']={'reason':'Render mostrou paredes fora das alas: mesh local precisava da matriz arquitetônica. Aplicada à mesh, mantendo matriz/origem do objeto anterior.','geographic_offset_added':False,'base_z_after_m':min((o.matrix_world@v.co).z for v in o.data.vertices),'photo_review':'frente/lateral antes do refinamento'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
r['source_after']['sha256']=hashlib.file_digest(Path(bpy.data.filepath).open('rb'),'sha256').hexdigest();p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(r['body_transform_refinement'],ensure_ascii=False))
