"""Enquadra costa expandida e píeres na B50 sem alterar geometria."""
import bpy
from pathlib import Path
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b50_encosta_sem_blockouts.blend"
for o in bpy.context.selected_objects:o.select_set(False)
names=[
"EXPANSAO B49 | terra emersa costeira | candidata",
"EXPANSAO B49 | faixa de transicao costeira | candidata",
"EXPANSAO B49 | fundo submerso DEM relativo | candidato"
]
objs=[bpy.context.scene.objects[n] for n in names]
objs += [o for o in bpy.context.scene.objects if o.name.startswith("PIER OSM |")]
for o in objs:o.hide_set(False);o.hide_viewport=False;o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
framed=False
for win in bpy.context.window_manager.windows:
  for area in win.screen.areas:
    if area.type=="VIEW_3D":
      region=next((r for r in area.regions if r.type=="WINDOW"),None)
      if region:
        with bpy.context.temp_override(window=win,area=area,region=region):
          bpy.ops.view3d.view_selected(use_all_regions=False)
        framed=True;break
  if framed:break
print({"framed":framed,"selected":[o.name for o in objs],"geometry_changed":False})
