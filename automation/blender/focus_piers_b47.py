"""Foca os píeres OSM no viewport sem alterar geometria."""
import bpy
from pathlib import Path
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b47_coastline_sudoeste.blend"
for o in bpy.context.selected_objects:
    o.select_set(False)
piers=[o for o in bpy.context.scene.objects if o.name.startswith("PIER OSM |")]
assert len(piers)==4
for o in piers:
    o.hide_set(False); o.hide_viewport=False; o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in piers if o.type=="MESH")
framed=False
for win in bpy.context.window_manager.windows:
    screen=win.screen
    for area in screen.areas:
        if area.type=="VIEW_3D":
            region=next((r for r in area.regions if r.type=="WINDOW"),None)
            if region:
                with bpy.context.temp_override(window=win,area=area,region=region):
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                framed=True
                break
    if framed: break
print({"piers":[o.name for o in piers],"framed":framed,"geometry_changed":False})
