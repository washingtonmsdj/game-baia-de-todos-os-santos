"""Aplica o transform controlado ao proxy oculto para eliminar cache world stale."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text())
if c['world_source']['revision']!='R30B.26':raise RuntimeError('Fonte R30B26 esperada')
if Path(bpy.data.filepath).resolve()!=(root/c['world_source']['file']).resolve():raise RuntimeError('Abrir fonte selecionada')
o=bpy.context.scene.objects[c['export']['terrain_proxy']];source=bpy.context.scene.objects[c['export']['road_object']]
if o.parent or o.constraints or o.modifiers:raise RuntimeError('Normalização exige proxy sem ancestrais/constraints/modifiers')
matrix=o.matrix_basis.copy()
if max(abs(matrix[i][j]-source.matrix_basis[i][j]) for i in range(4) for j in range(4))>1e-6:raise RuntimeError('Binding não coincide com transform registrado da fonte')
old_world=[list(row) for row in o.matrix_world];o.data.transform(matrix);o.data.update();o.matrix_basis=Matrix.Identity(4);o.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update()
o['boas_applied_source_transform']=json.dumps([list(row) for row in matrix]);o['boas_transform_binding']='source transform baked into collision vertex coordinates; identity object matrix, safe when excluded/hidden'
r={'source_before':c['world_source'].copy(),'classification':'ERROR','city_visual_geometry_changed':False,'road_widths_changed':False,'applied_matrix':[list(row) for row in matrix],'stale_hidden_world_matrix_before':old_world,'matrix_basis_after':[list(row) for row in o.matrix_basis],'method':'bake recorded source transform in proxy vertices; identity transforms, no guessed offset','reopen_validation':'pending','runtime_exported':False}
out=root/'blender/salvador_lacerda_r30b27_colisao_transform_aplicado.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));c['world_source'].update(file=out.relative_to(root).as_posix(),sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),revision='R30B.27',selection_reason='Derivada da R30B23: encontro contínuo Montanha/Pau da Bandeira; proxy atualizado com transform da fonte aplicado aos vértices para leitura estável mesmo oculto. Larguras e implantação visual preservadas.');cp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['source_after']=c['world_source'];(root/'docs/reports/blender/terrain_proxy_applied_transform.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r,ensure_ascii=False))
