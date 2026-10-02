import bpy, math
from pathlib import Path

scene = bpy.context.scene
old = bpy.data.collections.get("ORDAX_V14_CLEANUP")
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
coll = bpy.data.collections.new("ORDAX_V14_CLEANUP")
scene.collection.children.link(coll)

black = bpy.data.materials.get("ORDAX_V9_Black")
chrome = bpy.data.materials.get("ORDAX_V9_Chrome")

# Matte dark glazing avoids the white mirror-like windshield from the prior pass.
dark_glass = bpy.data.materials.get("ORDAX_V14_DarkGlazing") or bpy.data.materials.new("ORDAX_V14_DarkGlazing")
dark_glass.use_nodes = True
nodes = dark_glass.node_tree.nodes
links = dark_glass.node_tree.links
nodes.clear()
out = nodes.new("ShaderNodeOutputMaterial")
diff = nodes.new("ShaderNodeBsdfDiffuse")
diff.inputs["Color"].default_value = (0.004,0.010,0.017,1)
diff.inputs["Roughness"].default_value = 0.42
links.new(diff.outputs["BSDF"], out.inputs["Surface"])

for obj in bpy.data.objects:
    n = obj.name
    if n.startswith(("ORDAX_V12_Windshield","ORDAX_V12_RearGlass",
                     "ORDAX_V12_FrontSideGlass","ORDAX_V13_RearDoorGlass",
                     "ORDAX_V13_QuarterGlass","ORDAX_V13_RoofGlass")):
        if obj.type == "MESH":
            obj.data.materials.clear()
            obj.data.materials.append(dark_glass)
# Remove tubular guide curves that were reading as chrome trim.
for obj in bpy.data.objects:
    n = obj.name
    if n.startswith(("ORDAX_V10_ArchLip","ORDAX_V10_DoorSeam",
                     "ORDAX_V9_FenderVent","ORDAX_V10_FenderVent",
                     "ORDAX_V12_HoodCrease","ORDAX_V12_Shoulder",
                     "ORDAX_V12_IntakeEdge","ORDAX_V12_Kidney")):
        obj.hide_viewport = True
        obj.hide_render = True

def box(name, loc, dims, mat, bevel=0.020):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    coll.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("edge_softening","BEVEL")
        mod.width = bevel
        mod.segments = 5
        mod.limit_method = "ANGLE"
    return obj

def curve(name, pts, mat, radius=0.003):
    cu = bpy.data.curves.new(name+"_curve","CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts)-1)
    for i, pt in enumerate(pts):
        sp.points[i].co = (*pt,1.0)
    obj = bpy.data.objects.new(name,cu)
    coll.objects.link(obj)
    cu.materials.append(mat)
    return obj
front_y = -2.497

# Rounded twin grille, closer to the supplied front view.
for x in (-0.185,0.185):
    box("ORDAX_V14_GrilleFrame",(x,front_y-0.002,0.700),
        (0.340,0.030,0.205),chrome,0.050)
    box("ORDAX_V14_GrilleCore",(x,front_y-0.020,0.700),
        (0.300,0.024,0.165),black,0.043)
    for sx in (-0.090,-0.045,0.0,0.045,0.090):
        box("ORDAX_V14_GrilleSlat",(x+sx,front_y-0.038,0.700),
            (0.008,0.010,0.125),chrome,0.002)

# Door shut lines should read as seams, not tubes.
for sign in (-1,1):
    x = 0.946*sign
    for y in (-0.72,0.08,0.91):
        curve("ORDAX_V14_DoorSeam",
              [(x,y,0.245),(x,y,0.850)],black,0.0022)

    # Smaller front-fender air breather.
    box("ORDAX_V14_FenderVent",
        (0.950*sign,-1.035,0.555),(0.022,0.105,0.155),black,0.012)
    curve("ORDAX_V14_SideCharacter",
          [(0.945*sign,-1.82,0.775),
           (0.950*sign,-0.45,0.800),
           (0.945*sign,0.78,0.795),
           (0.910*sign,1.78,0.765)],black,0.002)

# Dark roof panel now reads like the reference panoramic glass.
roof_panel = bpy.data.objects.get("ORDAX_V13_RoofGlass")
if roof_panel and roof_panel.type == "MESH":
    roof_panel.data.materials.clear()
    roof_panel.data.materials.append(dark_glass)
scene["ordax_realistic_car_revision"] = "v14-reference-cleanup"
out = Path(bpy.path.abspath("//")) / "ordax_car_realistic_v14_reference_cleanup.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print({"ok":True,"revision":"v14","file":str(out),"objects":len(coll.objects)})
