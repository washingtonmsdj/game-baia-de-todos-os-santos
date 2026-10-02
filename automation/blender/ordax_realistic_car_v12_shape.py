import bpy, math
from pathlib import Path

scene = bpy.context.scene
old = bpy.data.collections.get("ORDAX_V12_SHAPE")
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
coll = bpy.data.collections.new("ORDAX_V12_SHAPE")
scene.collection.children.link(coll)

paint = bpy.data.materials.get("ORDAX_V9_Graphite")
black = bpy.data.materials.get("ORDAX_V9_Black")
chrome = bpy.data.materials.get("ORDAX_V9_Chrome")
red = bpy.data.materials.get("ORDAX_V9_Red")
white = bpy.data.materials.get("ORDAX_V9_White")
amber = bpy.data.materials.get("ORDAX_V9_Amber")

glass = bpy.data.materials.get("ORDAX_V12_DarkGlass") or bpy.data.materials.new("ORDAX_V12_DarkGlass")
glass.use_nodes = True
p = glass.node_tree.nodes.get("Principled BSDF")
if p:
    p.inputs["Base Color"].default_value = (0.004,0.009,0.016,1)
    p.inputs["Roughness"].default_value = 0.22
    if p.inputs.get("Transmission Weight"):
        p.inputs["Transmission Weight"].default_value = 0.035
# Retire elements superseded by this pass.
for obj in bpy.data.objects:
    n = obj.name
    if n.startswith(("ORDAX_V11_Windshield","ORDAX_V11_RearGlass",
                     "ORDAX_V11_FrontSideGlass","ORDAX_V11_RearSideGlass",
                     "ORDAX_V11_A_Pillar","ORDAX_V11_B_Pillar","ORDAX_V11_C_Pillar",
                     "ORDAX_V11_BeltTrim","ORDAX_V11_Roof",
                     "ORDAX_V11_Grille","ORDAX_V11_Headlamp",
                     "ORDAX_V11_LED","ORDAX_V11_SideMarker",
                     "ORDAX_V11_CenterIntake","ORDAX_V11_SideIntake",
                     "ORDAX_V11_Splitter","ORDAX_V11_Tail",
                     "ORDAX_V11_RearDiffuser","ORDAX_V11_Exhaust")):
        obj.hide_viewport = True
        obj.hide_render = True
    if n.startswith(("ORDAX_V9_MirrorCap","ORDAX_V9_HoodCrease",
                     "ORDAX_V9_ShoulderLine","ORDAX_V9_RockerLine")):
        obj.hide_viewport = True
        obj.hide_render = True

def mesh_obj(name, verts, faces, mat, smooth=False):
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    if mat:
        me.materials.append(mat)
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    return obj
def panel(name, pts, mat, thickness=0.008, bevel=0.004):
    obj = mesh_obj(name, pts, [tuple(range(len(pts)))], mat)
    solid = obj.modifiers.new("panel_thickness", "SOLIDIFY")
    solid.thickness = thickness
    edge = obj.modifiers.new("panel_softening", "BEVEL")
    edge.width = bevel
    edge.segments = 2
    return obj

def curve(name, pts, mat, radius=0.009):
    cu = bpy.data.curves.new(name + "_curve", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    spline = cu.splines.new("POLY")
    spline.points.add(len(pts)-1)
    for i, pt in enumerate(pts):
        spline.points[i].co = (*pt, 1.0)
    obj = bpy.data.objects.new(name, cu)
    coll.objects.link(obj)
    cu.materials.append(mat)
    return obj

def box(name, loc, dims, mat, bevel=0.015):
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
        mod = obj.modifiers.new("edge_softening", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    return obj
# Raked glasshouse with a gently arched roofline.
panel("ORDAX_V12_Windshield",
      [(-0.79,-0.91,0.890),(0.79,-0.91,0.890),
       (0.640,-0.35,1.390),(-0.640,-0.35,1.390)], glass, 0.010)
panel("ORDAX_V12_RearGlass",
      [(-0.640,0.58,1.400),(0.640,0.58,1.400),
       (0.755,1.18,0.900),(-0.755,1.18,0.900)], glass, 0.010)

for sign in (-1,1):
    panel("ORDAX_V12_FrontSideGlass",
          [(0.825*sign,-0.86,0.895),(0.830*sign,0.05,0.895),
           (0.685*sign,0.05,1.425),(0.640*sign,-0.35,1.390)], glass)
    panel("ORDAX_V12_RearSideGlass",
          [(0.830*sign,0.07,0.895),(0.785*sign,1.04,0.895),
           (0.675*sign,0.58,1.400),(0.685*sign,0.07,1.425)], glass)
    curve("ORDAX_V12_A_Pillar",
          [(0.805*sign,-0.88,0.895),(0.640*sign,-0.35,1.390)], black, 0.019)
    curve("ORDAX_V12_B_Pillar",
          [(0.830*sign,0.06,0.895),(0.685*sign,0.06,1.425)], black, 0.021)
    curve("ORDAX_V12_C_Pillar",
          [(0.675*sign,0.58,1.400),(0.785*sign,1.15,0.895)], black, 0.024)
    curve("ORDAX_V12_BeltTrim",
          [(0.83*sign,-0.86,0.880),(0.83*sign,0.07,0.880),
           (0.785*sign,1.04,0.880)], chrome, 0.005)
# Roof surface with visible crown in both axes.
ys = [-0.35,-0.18,0.02,0.23,0.43,0.58]
xs = [-1.0,-0.66,-0.33,0.0,0.33,0.66,1.0]
verts = []
for yi, y in enumerate(ys):
    ty = yi/(len(ys)-1)
    half = 0.645 - 0.012*abs(y-0.10)
    zc = 1.390 + 0.060*math.sin(math.pi*ty)
    for xn in xs:
        z = zc + 0.045*(1-xn*xn)
        verts.append((xn*half,y,z))
faces = []
nx = len(xs)
for iy in range(len(ys)-1):
    for ix in range(nx-1):
        a = iy*nx + ix
        faces.append((a,a+1,a+1+nx,a+nx))
roof = mesh_obj("ORDAX_V12_Roof", verts, faces, paint, True)
solid = roof.modifiers.new("roof_thickness","SOLIDIFY")
solid.thickness = 0.022
sub = roof.modifiers.new("roof_smooth","SUBSURF")
sub.levels = 2
sub.render_levels = 2

# Integrated compact mirrors.
for sign in (-1,1):
    x = 0.925*sign
    curve("ORDAX_V12_MirrorStalk",
          [(0.845*sign,-0.70,1.005),(0.925*sign,-0.72,1.025)], black, 0.022)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20,
        location=(x,-0.755,1.040))
    mirror = bpy.context.object
    mirror.name = "ORDAX_V12_Mirror"
    mirror.scale = (0.100,0.170,0.060)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for owner in list(mirror.users_collection):
        owner.objects.unlink(mirror)
    coll.objects.link(mirror)
    mirror.data.materials.append(paint)
    for poly in mirror.data.polygons:
        poly.use_smooth = True

front_y = -2.497

# Kidney-shaped grille polygons instead of rectangles.
def kidney(sign):
    cx = 0.188*sign
    pts = [
        (cx-0.160*sign,front_y-0.018,0.805),
        (cx+0.145*sign,front_y-0.018,0.805),
        (cx+0.155*sign,front_y-0.018,0.760),
        (cx+0.125*sign,front_y-0.018,0.625),
        (cx,front_y-0.018,0.605),
        (cx-0.125*sign,front_y-0.018,0.625),
        (cx-0.155*sign,front_y-0.018,0.760),
    ]
    core = panel("ORDAX_V12_KidneyCore", pts, black, 0.018, 0.006)
    curve("ORDAX_V12_KidneyOutline", pts+[pts[0]], chrome, 0.008)
    for dx in (-0.09,-0.045,0.0,0.045,0.09):
        x = cx + dx*sign
        curve("ORDAX_V12_KidneySlat",
              [(x,front_y-0.040,0.785),(x,front_y-0.040,0.640)], chrome, 0.004)
kidney(-1)
kidney(1)
# Angular slim headlights matching the reference proportions.
for sign in (-1,1):
    housing = [
        (0.335*sign,front_y-0.020,0.820),
        (0.565*sign,front_y-0.020,0.835),
        (0.885*sign,front_y-0.020,0.805),
        (0.865*sign,front_y-0.020,0.700),
        (0.570*sign,front_y-0.020,0.710),
        (0.350*sign,front_y-0.020,0.735),
    ]
    panel("ORDAX_V12_HeadlampHousing", housing, black, 0.016, 0.006)
    curve("ORDAX_V12_LED_Upper",
          [(0.845*sign,front_y-0.045,0.785),
           (0.640*sign,front_y-0.047,0.800),
           (0.505*sign,front_y-0.047,0.785),
           (0.360*sign,front_y-0.045,0.795)], white, 0.008)
    curve("ORDAX_V12_LED_Lower",
          [(0.845*sign,front_y-0.046,0.745),
           (0.640*sign,front_y-0.048,0.738),
           (0.505*sign,front_y-0.048,0.755),
           (0.360*sign,front_y-0.046,0.750)], white, 0.007)
    box("ORDAX_V12_Marker",
        (0.878*sign,front_y-0.046,0.755),(0.015,0.012,0.052),amber,0.002)

# Lower bumper openings as trapezoids.
panel("ORDAX_V12_CenterIntake",
      [(-0.39,front_y-0.014,0.415),(0.39,front_y-0.014,0.415),
       (0.34,front_y-0.014,0.285),(-0.34,front_y-0.014,0.285)], black, 0.018, 0.010)
for sign in (-1,1):
    side = [
        (0.555*sign,front_y-0.015,0.470),
        (0.860*sign,front_y-0.015,0.445),
        (0.850*sign,front_y-0.015,0.245),
        (0.620*sign,front_y-0.015,0.275),
    ]
    panel("ORDAX_V12_SideIntake", side, black, 0.018, 0.010)
    curve("ORDAX_V12_IntakeEdge",
          [(0.820*sign,front_y-0.042,0.290),
           (0.690*sign,front_y-0.044,0.255),
           (0.590*sign,front_y-0.042,0.280)], chrome, 0.007)

curve("ORDAX_V12_FrontSplitter",
      [(-0.80,front_y-0.020,0.210),(0,front_y-0.030,0.195),
       (0.80,front_y-0.020,0.210)], black, 0.020)

# Subtle hood sculpture, using body-color ridges rather than chrome.
for sign in (-1,1):
    curve("ORDAX_V12_HoodCrease",
          [(0.22*sign,-2.30,0.900),(0.38*sign,-1.62,0.945),
           (0.50*sign,-0.94,0.965)], paint, 0.006)
    curve("ORDAX_V12_Shoulder",
          [(0.91*sign,-1.80,0.790),(0.94*sign,-0.55,0.815),
           (0.94*sign,0.70,0.810),(0.90*sign,1.78,0.770)], paint, 0.006)

rear_y = 2.497
# Thin L-shaped rear lamps.
for sign in (-1,1):
    housing = [
        (0.285*sign,rear_y+0.018,0.825),
        (0.585*sign,rear_y+0.018,0.840),
        (0.890*sign,rear_y+0.018,0.815),
        (0.875*sign,rear_y+0.018,0.710),
        (0.610*sign,rear_y+0.018,0.720),
        (0.300*sign,rear_y+0.018,0.755),
    ]
    panel("ORDAX_V12_TailHousing", housing, black, 0.016, 0.006)
    curve("ORDAX_V12_TailUpper",
          [(0.865*sign,rear_y+0.045,0.802),
           (0.620*sign,rear_y+0.047,0.810),
           (0.620*sign,rear_y+0.048,0.775),
           (0.310*sign,rear_y+0.044,0.775)], red, 0.011)
    curve("ORDAX_V12_TailLower",
          [(0.865*sign,rear_y+0.046,0.760),
           (0.620*sign,rear_y+0.048,0.758),
           (0.310*sign,rear_y+0.044,0.738)], red, 0.007)

panel("ORDAX_V12_RearDiffuser",
      [(-0.79,rear_y+0.012,0.330),(0.79,rear_y+0.012,0.330),
       (0.69,rear_y+0.012,0.190),(-0.69,rear_y+0.012,0.190)], black, 0.018, 0.010)

for sign in (-1,1):
    box("ORDAX_V12_ExhaustOuter",
        (0.690*sign,rear_y+0.043,0.245),(0.255,0.045,0.095),chrome,0.024)
    box("ORDAX_V12_ExhaustInner",
        (0.690*sign,rear_y+0.066,0.245),(0.210,0.020,0.060),black,0.017)
# Replace the coarse previous wheels and oversized badges.
for obj in bpy.data.objects:
    n = obj.name
    if n.startswith("ORDAX_V9_Wheel_") or n.startswith("ORDAX_V9_Badge"):
        obj.hide_viewport = True
        obj.hide_render = True
    if n == "ORDAX_V9_SharkFin":
        obj.hide_viewport = True
        obj.hide_render = True

rubber = bpy.data.materials.get("ORDAX_V9_Rubber")
silver = bpy.data.materials.get("ORDAX_V9_WheelSilver")

def torus(name, loc, major, minor, mat, depth_scale=1.0):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major, minor_radius=minor,
        major_segments=72, minor_segments=18,
        location=loc, rotation=(0,math.pi/2,0))
    obj = bpy.context.object
    obj.name = name
    obj.scale.z = depth_scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    coll.objects.link(obj)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj

def cylinder(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=radius, depth=depth,
        location=loc, rotation=(0,math.pi/2,0))
    obj = bpy.context.object
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    coll.objects.link(obj)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj

wheel_x = 0.805
wheel_y = 1.490
wheel_z = 0.345
for side, x in (("L",-wheel_x),("R",wheel_x)):
    for axle, y in (("F",-wheel_y),("R",wheel_y)):
        prefix = "ORDAX_V12_Wheel_" + axle + side
        torus(prefix+"_Tire",(x,y,wheel_z),0.286,0.058,rubber,1.85)
        torus(prefix+"_Rim",(x,y,wheel_z),0.238,0.012,silver,1.40)
        cylinder(prefix+"_Disc",(x,y,wheel_z),0.192,0.026,chrome)
        cylinder(prefix+"_Hub",(x,y,wheel_z),0.050,0.046,black)
        for k in range(10):
            base_a = math.radians(k*36)
            for delta in (-4.0,4.0):
                a = base_a + math.radians(delta)
                sy = y + math.cos(a)*0.122
                sz = wheel_z + math.sin(a)*0.122
                spoke = box(prefix+"_Spoke",(x,sy,sz),(0.028,0.220,0.018),silver,0.004)
                spoke.rotation_euler[0] = a
        cal_x = x + (-0.050 if x > 0 else 0.050)
        box(prefix+"_Caliper",(cal_x,y-0.105,wheel_z+0.025),
            (0.038,0.050,0.130),red,0.010)
# Smaller emblems, shark fin and plate recesses.
def front_disc(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=radius, depth=depth,
        location=loc, rotation=(math.pi/2,0,0))
    obj = bpy.context.object
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    coll.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

front_disc("ORDAX_V12_HoodBadge",(0,-2.365,0.935),0.045,0.012,black)
front_disc("ORDAX_V12_TrunkBadge",(0,2.405,0.930),0.043,0.012,black)
box("ORDAX_V12_RearPlateRecess",(0,2.505,0.535),(0.500,0.025,0.130),black,0.018)
curve("ORDAX_V12_TrunkLip",
      [(-0.68,2.30,0.820),(0,2.325,0.830),(0.68,2.30,0.820)], paint,0.009)

bpy.ops.mesh.primitive_cone_add(
    vertices=4, radius1=0.050, radius2=0.014, depth=0.080,
    location=(0,0.50,1.475), rotation=(0,0,math.radians(45)))
fin = bpy.context.object
fin.name = "ORDAX_V12_SharkFin"
for owner in list(fin.users_collection):
    owner.objects.unlink(fin)
coll.objects.link(fin)
fin.data.materials.append(paint)

scene["ordax_realistic_car_revision"] = "v12-reference-shape-pass"
scene["ordax_reference_dimensions_m"] = [1.87,4.97,1.47]
scene["ordax_reference_wheelbase_m"] = 2.98
out = Path(bpy.path.abspath("//")) / "ordax_car_realistic_v12_reference_shape.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print({"ok":True,"revision":"v12","file":str(out),"objects":len(coll.objects)})
