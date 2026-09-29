from __future__ import annotations

import bpy
from mathutils import Vector

if bpy.context.object and bpy.context.object.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    if obj.type == "CAMERA" or obj.name.startswith("R27 |") or obj.name.startswith("APOIO TERRENO |"):
        obj.hide_set(True)
for name in ("34 GAMEPLAY | COLLISION CHUNKS R30A6", "33.1 RUNTIME | TERRAIN COLLISION"):
    collection = bpy.data.collections.get(name)
    if collection:
        collection.hide_viewport = True
window = bpy.context.window
screen = window.screen if window else None
area = next((a for a in screen.areas if a.type == "VIEW_3D"), None) if screen else None
region = next((r for r in area.regions if r.type == "WINDOW"), None) if area else None
if window and area and region:
    space = area.spaces.active
    space.shading.type = "SOLID"
    space.shading.color_type = "MATERIAL"
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.view3d.view_axis(type="TOP", align_active=False)
        region3d = space.region_3d
        region3d.view_location = Vector((-85.0, 135.0, 20.0))
        region3d.view_distance = 150.0
