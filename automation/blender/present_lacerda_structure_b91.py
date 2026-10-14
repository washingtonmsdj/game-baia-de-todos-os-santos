"""Enquadramento da revisão ativa na mesma cena; sem mutação geométrica."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name in ('salvador_lacerda_r30b91_integridade_malha_e_apoios.blend','salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend','salvador_lacerda_r30b93_estrutura_inferior_documental.blend','salvador_lacerda_r30b94_fechamentos_passarela_tunel.blend','salvador_lacerda_r30b95_limites_circulacoes_superiores.blend','salvador_lacerda_r30b96_encontro_corpo_cobertura.blend','salvador_lacerda_r30b97_limites_vestibulos_superiores.blend','salvador_lacerda_r30b98_frente_superior_reconciliada.blend','salvador_lacerda_r30b99_subsolos_corpo_cidade_alta.blend','salvador_lacerda_r30b100_corpo_superior_cobertura.blend','salvador_lacerda_r30b101_pavimentos_estruturais.blend')
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame'])
window=next(w for w in bpy.context.window_manager.windows if w.screen);area=next(a for a in window.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active
mode=globals().get('BOAS_STRUCTURE_VIEW','exterior')
with bpy.context.temp_override(window=window,area=area,region=region):
 if mode=='map' and space.local_view:bpy.ops.view3d.localview(frame_selected=False)
 bpy.ops.object.select_all(action='DESELECT')
 if mode!='map' and not space.local_view:
  names=set()
  paths=['docs/reports/blender/lacerda-massing-b88/application.json','docs/reports/blender/lacerda-mesh-b91/application.json']
  if any(t in Path(bpy.data.filepath).name for t in ('b92_','b93_','b94_','b95_','b96_','b97_','b98_','b99_','b100_','b101_')):paths.append('docs/reports/blender/lacerda-bridge-b92/application.json')
  if any(t in Path(bpy.data.filepath).name for t in ('b93_','b94_','b95_','b96_','b97_','b98_','b99_','b100_','b101_')):paths.append('docs/reports/blender/lacerda-lower-structure-b93/application.json')
  if any(t in Path(bpy.data.filepath).name for t in ('b94_','b95_','b96_','b97_','b98_','b99_','b100_','b101_')):paths.append('docs/reports/blender/lacerda-closure-b94/application.json')
  if any(t in Path(bpy.data.filepath).name for t in ('b95_','b96_','b97_','b98_','b99_','b100_','b101_')):paths.append('docs/reports/blender/lacerda-enclosure-b95/application.json')
  if any(t in Path(bpy.data.filepath).name for t in ('b96_','b97_','b98_','b99_','b100_','b101_')):paths.append('docs/reports/blender/lacerda-body-b96/application.json')
  if any(t in Path(bpy.data.filepath).name for t in ('b97_','b98_','b99_','b100_','b101_')):paths.append('docs/reports/blender/lacerda-vestibules-b97/application.json')
  if any(t in Path(bpy.data.filepath).name for t in ('b98_','b99_','b100_','b101_')):paths.append('docs/reports/blender/lacerda-completion-b98/application.json')
  if any(t in Path(bpy.data.filepath).name for t in ('b99_','b100_','b101_')):paths.append('docs/reports/blender/lacerda-structure-b99/application.json')
  if any(t in Path(bpy.data.filepath).name for t in ('b100_','b101_')):paths.append('docs/reports/blender/lacerda-upper-body-b100/application.json')
  if 'b101_' in Path(bpy.data.filepath).name:paths.append('docs/reports/blender/lacerda-floors-b101/application.json')
  for path in paths:
   r=json.loads((root/path).read_text());names.update(v['object'] for v in r['changes']+r.get('added',[]))
  for n in names:
   o=bpy.context.scene.objects[n]
   if o.visible_get() and not any(t in n for t in ('COLLISION','COLISÃO')):o.select_set(True)
  bpy.context.view_layer.objects.active=bpy.context.scene.objects['CASCA | parede lateral']
  bpy.ops.view3d.localview(frame_selected=False)
 space.shading.type='SOLID';space.shading.color_type='MATERIAL';space.overlay.show_overlays=mode=='map'
 space.region_3d.view_location=M@Vector((-28.,3.,47.))
 space.region_3d.view_rotation=(M.to_3x3()@Vector((-1.2,-1.7,.75))).to_track_quat('Z','Y')
 space.region_3d.view_distance=115. if mode=='exterior' else 125.
 space.region_3d.view_perspective='ORTHO';space.region_3d.update();area.tag_redraw();bpy.ops.object.select_all(action='DESELECT')
print(json.dumps({'file':bpy.data.filepath,'scene':bpy.context.scene.name,'mode':mode,'local_view':bool(space.local_view)}))
