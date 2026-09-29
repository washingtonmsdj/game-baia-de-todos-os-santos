from __future__ import annotations

import bpy

ROOT_NAME = "37 GAMEPLAY | NAV HINTS R30A11"
root = bpy.data.collections.get(ROOT_NAME)
if root is None:
    raise RuntimeError(f"Collection not found: {ROOT_NAME}")

if bpy.context.object and bpy.context.object.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="DESELECT")
selected = []
for obj in root.all_objects:
    if obj.type in {"CURVE", "EMPTY"}:
        obj.select_set(True)
        selected.append(obj)

if selected:
    bpy.context.view_layer.objects.active = selected[0]

window = bpy.context.window
screen = window.screen if window else None
area = next((item for item in screen.areas if item.type == "VIEW_3D"), None) if screen else None
region = next((item for item in area.regions if item.type == "WINDOW"), None) if area else None
if window and area and region and selected:
    with bpy.context.temp_override(window=window, area=area, region=region):
        space = area.spaces.active
        space.shading.color_type = "MATERIAL"
        bpy.ops.view3d.view_axis(type="TOP", align_active=False)
        bpy.ops.view3d.view_selected(use_all_regions=False)
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = None
