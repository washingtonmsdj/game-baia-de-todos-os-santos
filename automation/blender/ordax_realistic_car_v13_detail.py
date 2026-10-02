import bpy, math
from pathlib import Path

scene = bpy.context.scene
old = bpy.data.collections.get("ORDAX_V13_DETAIL")
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
coll = bpy.data.collections.new("ORDAX_V13_DETAIL")
scene.collection.children.link(coll)

paint = bpy.data.materials.get("ORDAX_V9_Graphite")
black = bpy.data.materials.get("ORDAX_V9_Black")
chrome = bpy.data.materials.get("ORDAX_V9_Chrome")
glass = bpy.data.materials.get("ORDAX_V12_DarkGlass")

# Make the glazing read as the dark tinted reference, not white reflective panels.
if glass and glass.use_nodes:
    p = glass.node_tree.nodes.get("Principled BSDF")
    if p:
        p.inputs["Base Color"].default_value = (0.002,0.005,0.009,1)
        p.inputs["Roughness"].default_value = 0.32
        if p.inputs.get("Transmission Weight"):
            p.inputs["Transmission Weight"].default_value = 0.0
        if p.inputs.get("IOR Level"):
            p.inputs["IOR Level"].default_value = 0.22

# Darker gunmetal wheels.
silver = bpy.data.materials.get("ORDAX_V9_WheelSilver")
if silver and silver.use_nodes:
    p = silver.node_tree.nodes.get("Principled BSDF")
    if p:
        p.inputs["Base Color"].default_value = (0.12,0.14,0.17,1)
# Lower the lamps slightly and seat the rear lamps into the rear surface.
for obj in bpy.data.objects:
    n = obj.name
    if n.startswith(("ORDAX_V12_HeadlampHousing","ORDAX_V12_LED_","ORDAX_V12_Marker")):
        obj.location.z -= 0.025
    if n.startswith(("ORDAX_V12_TailHousing","ORDAX_V12_TailUpper","ORDAX_V12_TailLower")):
        obj.location.z -= 0.065
        obj.location.y -= 0.035

# Replace the single large rear side window with a rear-door pane + fixed quarter pane.
for obj in bpy.data.objects:
    if obj.name.startswith("ORDAX_V12_RearSideGlass"):
        obj.hide_viewport = True
        obj.hide_render = True

def panel(name, pts, mat, thickness=0.008):
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(pts, [], [tuple(range(len(pts)))])
    me.update()
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    me.materials.append(mat)
    solid = obj.modifiers.new("thickness", "SOLIDIFY")
    solid.thickness = thickness
    edge = obj.modifiers.new("soft_edges", "BEVEL")
    edge.width = 0.004
    edge.segments = 2
    return obj

def curve(name, pts, mat, radius=0.008):
    cu = bpy.data.curves.new(name + "_curve", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts)-1)
    for i, pt in enumerate(pts):
        sp.points[i].co = (*pt, 1.0)
    obj = bpy.data.objects.new(name, cu)
    coll.objects.link(obj)
    cu.materials.append(mat)
    return obj

for sign in (-1,1):
    # Rear door glass.
    panel("ORDAX_V13_RearDoorGlass",
          [(0.830*sign,0.08,0.900),
           (0.812*sign,0.745,0.905),
           (0.690*sign,0.565,1.390),
           (0.685*sign,0.08,1.425)], glass)
    # Small fixed quarter window with rising lower edge.
    panel("ORDAX_V13_QuarterGlass",
          [(0.812*sign,0.765,0.905),
           (0.785*sign,1.045,0.925),
           (0.675*sign,0.590,1.390),
           (0.690*sign,0.580,1.390)], glass)
    curve("ORDAX_V13_QuarterDivider",
          [(0.812*sign,0.750,0.900),(0.690*sign,0.575,1.390)],
          black,0.015)
    curve("ORDAX_V13_QuarterLowerTrim",
          [(0.812*sign,0.765,0.885),(0.785*sign,1.045,0.905)],
          chrome,0.005)

# Dark trim strip between rear lamps.
panel("ORDAX_V13_RearBlackBand",
      [(-0.55,2.455,0.770),(0.55,2.455,0.770),
       (0.55,2.455,0.710),(-0.55,2.455,0.710)], black,0.012)
# Panoramic roof panel visible in the supplied top view.
panel("ORDAX_V13_RoofGlass",
      [(-0.43,-0.16,1.458),(0.43,-0.16,1.458),
       (0.43,0.42,1.452),(-0.43,0.42,1.452)], glass,0.010)
curve("ORDAX_V13_RoofGlassFront",
      [(-0.43,-0.16,1.462),(0.43,-0.16,1.462)], black,0.008)
curve("ORDAX_V13_RoofGlassRear",
      [(-0.43,0.42,1.456),(0.43,0.42,1.456)], black,0.008)

# Trunk shut line and lower rear crease.
curve("ORDAX_V13_TrunkSeam",
      [(-0.72,2.275,0.815),(0,2.315,0.825),(0.72,2.275,0.815)],
      black,0.004)
curve("ORDAX_V13_RearLowerCrease",
      [(-0.72,2.455,0.420),(0,2.475,0.400),(0.72,2.455,0.420)],
      paint,0.005)

# Front hood shut line around the leading edge.
curve("ORDAX_V13_HoodLeadingEdge",
      [(-0.70,-2.265,0.845),(0,-2.305,0.855),(0.70,-2.265,0.845)],
      black,0.004)

scene["ordax_realistic_car_revision"] = "v13-reference-detail-pass"
out = Path(bpy.path.abspath("//")) / "ordax_car_realistic_v13_reference_detail.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print({"ok":True,"revision":"v13","file":str(out),"objects":len(coll.objects)})
