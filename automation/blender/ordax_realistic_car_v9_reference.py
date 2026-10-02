import bpy, math
from pathlib import Path
from mathutils import Vector

# OrdaX sedan reference pass v9 — preserves v8b and creates a new revision.
scene = bpy.context.scene
root = bpy.data.objects.get("saloon")
if root is None:
    raise RuntimeError("saloon root not found")

# Clean only a prior v9 reference pass, never the imported source.
old = bpy.data.collections.get("ORDAX_V9_REFERENCE")
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)

coll = bpy.data.collections.new("ORDAX_V9_REFERENCE")
scene.collection.children.link(coll)

def link_to_v9(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj

def mat(name, color, metallic=0.0, roughness=0.35, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    if p:
        if p.inputs.get("Base Color"):
            p.inputs["Base Color"].default_value = color
        if p.inputs.get("Metallic"):
            p.inputs["Metallic"].default_value = metallic
        if p.inputs.get("Roughness"):
            p.inputs["Roughness"].default_value = roughness
        if emission is not None:
            if p.inputs.get("Emission Color"):
                p.inputs["Emission Color"].default_value = emission
            if p.inputs.get("Emission Strength"):
                p.inputs["Emission Strength"].default_value = 5.0
    return m

paint = mat("ORDAX_V9_Graphite", (0.018, 0.024, 0.032, 1), 0.82, 0.16)
paint_hi = mat("ORDAX_V9_Graphite_Highlight", (0.055, 0.065, 0.078, 1), 0.72, 0.20)
black = mat("ORDAX_V9_Black", (0.004, 0.005, 0.006, 1), 0.25, 0.28)
rubber = mat("ORDAX_V9_Rubber", (0.006, 0.007, 0.008, 1), 0.0, 0.72)
chrome = mat("ORDAX_V9_Chrome", (0.48, 0.52, 0.56, 1), 0.96, 0.10)
silver = mat("ORDAX_V9_WheelSilver", (0.20, 0.23, 0.27, 1), 0.93, 0.16)
red = mat("ORDAX_V9_Red", (0.34, 0.002, 0.001, 1), 0.25, 0.18, (1.0, 0.005, 0.002, 1))
white = mat("ORDAX_V9_White", (0.85, 0.92, 1.0, 1), 0.05, 0.12, (1.0, 1.0, 1.0, 1))
amber = mat("ORDAX_V9_Amber", (0.55, 0.12, 0.01, 1), 0.05, 0.18, (1.0, 0.20, 0.01, 1))
tan = mat("ORDAX_V9_TanInterior", (0.16, 0.095, 0.055, 1), 0.0, 0.55)

# Match the reference sedan envelope: ~4.97m x 1.87m x 1.47m.
root.scale = (0.935, 1.030, 1.050)

# Remove visibly crude imported light bars/wheels from the review render.
for obj in bpy.data.objects:
    lname = obj.name.lower()
    if obj.name == "saloon_4" or (obj.type == "MESH" and "wheel-" in lname):
        obj.hide_render = True
        obj.hide_viewport = True

# Dark metallic paint and reference-like cabin colors.
for name in ("paintB", "paint", "body"):
    m = bpy.data.materials.get(name)
    if m and m.use_nodes:
        p = m.node_tree.nodes.get("Principled BSDF")
        if p and p.inputs.get("Base Color"):
            p.inputs["Base Color"].default_value = (0.018, 0.024, 0.032, 1)
        if p and p.inputs.get("Metallic"):
            p.inputs["Metallic"].default_value = 0.82
        if p and p.inputs.get("Roughness"):
            p.inputs["Roughness"].default_value = 0.16
interior = bpy.data.materials.get("interior")
if interior:
    interior.diffuse_color = (0.16, 0.095, 0.055, 1)
    if interior.use_nodes:
        p = interior.node_tree.nodes.get("Principled BSDF")
        if p and p.inputs.get("Base Color"):
            p.inputs["Base Color"].default_value = (0.16, 0.095, 0.055, 1)
        if p and p.inputs.get("Roughness"):
            p.inputs["Roughness"].default_value = 0.55

def box(name, loc, dims, material, bevel=0.025, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_to_v9(o)
    if material:
        o.data.materials.append(material)
    if bevel > 0:
        mod = o.modifiers.new("Reference bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 4
        mod.limit_method = "ANGLE"
    return o

def cyl(name, loc, radius, depth, material, rot=(math.pi/2,0,0), vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    link_to_v9(o)
    if material:
        o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def torus(name, loc, major, minor, material, width_scale=1.0):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major, minor_radius=minor,
        major_segments=72, minor_segments=20,
        location=loc, rotation=(0, math.pi/2, 0)
    )
    o = bpy.context.object
    o.name = name
    o.scale.z = width_scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_to_v9(o)
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    return o

def curve(name, pts, material, bevel=0.012):
    cu = bpy.data.curves.new(name + "_curve", "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = 2
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts)-1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1.0)
    obj = bpy.data.objects.new(name, cu)
    coll.objects.link(obj)
    cu.materials.append(material)
    return obj

# New 19/20-inch-style wheels: 2.98 m wheelbase, broader track, red calipers.
wheel_x = 0.805
wheel_y = 1.490
wheel_z = 0.345
for side, x in (("L", -wheel_x), ("R", wheel_x)):
    for axle, y in (("F", -wheel_y), ("R", wheel_y)):
        prefix = f"ORDAX_V9_Wheel_{axle}{side}"
        torus(prefix+"_Tire", (x,y,wheel_z), 0.286, 0.058, rubber, 2.05)
        torus(prefix+"_RimOuter", (x,y,wheel_z), 0.242, 0.013, silver, 1.55)
        torus(prefix+"_RimInner", (x,y,wheel_z), 0.205, 0.010, black, 1.25)
        cyl(prefix+"_Disc", (x,y,wheel_z), 0.205, 0.026, chrome, rot=(0,math.pi/2,0))
        cyl(prefix+"_Hub", (x,y,wheel_z), 0.060, 0.050, black, rot=(0,math.pi/2,0))
        for i in range(10):
            a = math.radians(i*36 + (8 if i%2 else -8))
            r = 0.125
            sy = y + math.cos(a)*r
            sz = wheel_z + math.sin(a)*r
            spoke = box(prefix+f"_Spoke_{i:02d}", (x,sy,sz), (0.034,0.245,0.030), silver, 0.008, rotation=(a,0,0))
        cal_x = x + (-0.055 if x > 0 else 0.055)
        box(prefix+"_Caliper", (cal_x, y-0.11, wheel_z+0.03), (0.045,0.055,0.145), red, 0.012)

# Front reference face.
front_y = -2.485
# Kidney grille chrome shells and black cores.
for x in (-0.195, 0.195):
    box("ORDAX_V9_Kidney_Chrome", (x, front_y, 0.705), (0.345,0.035,0.295), chrome, 0.050)
    box("ORDAX_V9_Kidney_Black", (x, front_y-0.023, 0.705), (0.305,0.030,0.255), black, 0.045)
    for sx in (-0.095,-0.057,-0.019,0.019,0.057,0.095):
        box("ORDAX_V9_Kidney_Slat", (x+sx, front_y-0.043, 0.705), (0.010,0.020,0.210), chrome, 0.004)

# Slim headlamp housings and dual LED signatures.
for sign in (-1, 1):
    hx = sign*0.600
    box("ORDAX_V9_HeadlampHousing", (hx, front_y-0.008, 0.785), (0.565,0.045,0.165), black, 0.040)
    inner = 0.340*sign
    outer = 0.855*sign
    mid = 0.610*sign
    curve("ORDAX_V9_HeadlampLED_Upper",
          [(outer,front_y-0.038,0.825),(mid,front_y-0.045,0.840),(inner,front_y-0.040,0.815)], white, 0.013)
    curve("ORDAX_V9_HeadlampLED_Lower",
          [(outer,front_y-0.040,0.770),(mid,front_y-0.048,0.760),(inner,front_y-0.043,0.790)], white, 0.010)
    box("ORDAX_V9_HeadlampAmber", (sign*0.865, front_y-0.040, 0.790), (0.025,0.016,0.075), amber, 0.006)

# M-sport-like lower bumper.
box("ORDAX_V9_FrontIntakeCenter", (0,front_y-0.010,0.365), (0.930,0.045,0.205), black, 0.055)
for sign in (-1,1):
    box("ORDAX_V9_FrontIntakeSide", (sign*0.715,front_y-0.008,0.370), (0.300,0.050,0.280), black, 0.050)
    curve("ORDAX_V9_FrontIntakeBlade",
          [(sign*0.855,front_y-0.050,0.280),(sign*0.670,front_y-0.050,0.235),(sign*0.575,front_y-0.048,0.245)], chrome, 0.014)
box("ORDAX_V9_FrontSplitter", (0,front_y+0.010,0.205), (1.680,0.090,0.055), black, 0.020)

# Hood creases and front badge.
curve("ORDAX_V9_HoodCrease_L", [(-0.24,-2.34,0.945),(-0.38,-1.65,0.990),(-0.52,-0.92,1.020)], paint_hi, 0.008)
curve("ORDAX_V9_HoodCrease_R", [(0.24,-2.34,0.945),(0.38,-1.65,0.990),(0.52,-0.92,1.020)], paint_hi, 0.008)
cyl("ORDAX_V9_BadgeFront_Ring", (0,front_y-0.035,0.970), 0.060, 0.018, chrome)
cyl("ORDAX_V9_BadgeFront_Core", (0,front_y-0.047,0.970), 0.048, 0.014, black)

# Rear reference face.
rear_y = 2.485
for sign in (-1,1):
    box("ORDAX_V9_TailHousing", (sign*0.590,rear_y+0.005,0.785), (0.610,0.045,0.190), black, 0.045)
    inner = 0.300*sign
    outer = 0.885*sign
    mid = 0.620*sign
    curve("ORDAX_V9_TailLED",
          [(outer,rear_y+0.040,0.835),(mid,rear_y+0.048,0.835),(mid,rear_y+0.052,0.785),(inner,rear_y+0.045,0.785)], red, 0.017)
    curve("ORDAX_V9_TailLED_Inner",
          [(outer,rear_y+0.043,0.790),(mid,rear_y+0.050,0.790),(inner,rear_y+0.046,0.755)], red, 0.010)

box("ORDAX_V9_RearDiffuser", (0,rear_y-0.005,0.245), (1.600,0.070,0.210), black, 0.055)
for sign in (-1,1):
    box("ORDAX_V9_ExhaustFrame", (sign*0.685,rear_y+0.045,0.245), (0.340,0.080,0.145), chrome, 0.035)
    box("ORDAX_V9_ExhaustBlack", (sign*0.685,rear_y+0.086,0.245), (0.285,0.035,0.095), black, 0.028)
cyl("ORDAX_V9_BadgeRear_Ring", (0,rear_y+0.040,0.985), 0.058, 0.018, chrome, rot=(math.pi/2,0,0))
cyl("ORDAX_V9_BadgeRear_Core", (0,rear_y+0.052,0.985), 0.046, 0.014, black, rot=(math.pi/2,0,0))

# Side character lines, rockers and mirror caps.
for sign in (-1,1):
    x = sign*0.944
    curve("ORDAX_V9_ShoulderLine",
          [(x,-1.90,0.785),(x,-0.90,0.805),(x,0.10,0.800),(x,1.15,0.785),(x,1.95,0.765)], paint_hi, 0.010)
    curve("ORDAX_V9_RockerLine",
          [(sign*0.935,-1.35,0.235),(sign*0.940,0.10,0.220),(sign*0.930,1.30,0.235)], black, 0.018)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, location=(sign*1.015,-0.720,1.030))
    mirror = bpy.context.object
    mirror.name = "ORDAX_V9_MirrorCap"
    mirror.scale = (0.120,0.195,0.075)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_to_v9(mirror)
    mirror.data.materials.append(paint)
    for p in mirror.data.polygons:
        p.use_smooth = True
    box("ORDAX_V9_FenderVent", (sign*0.948,-1.045,0.545), (0.030,0.180,0.300), black, 0.020)

# Roof shark fin.
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.070, radius2=0.018, depth=0.120, location=(0,0.685,1.515), rotation=(0,0,math.radians(45)))
fin = bpy.context.object
fin.name = "ORDAX_V9_SharkFin"
link_to_v9(fin)
fin.data.materials.append(paint)

# Presentation and metadata.
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene["ordax_realistic_car_revision"] = "v9-reference-faithful-pass"
scene["ordax_reference_target"] = "user supplied multi-view dark sport sedan reference"
scene["ordax_reference_dimensions_m"] = [1.87, 4.97, 1.47]
scene["ordax_reference_wheelbase_m"] = 2.98

# Save as a new file; v8b remains untouched on disk.
out = Path(bpy.path.abspath("//")) / "ordax_car_realistic_v9_reference.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print({"ok": True, "revision": "v9-reference", "file": str(out), "v9_objects": len(coll.objects)})
