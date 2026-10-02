import bpy, math
from pathlib import Path

scene = bpy.context.scene
old = bpy.data.collections.get("ORDAX_V11_REFINEMENT")
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
coll = bpy.data.collections.new("ORDAX_V11_REFINEMENT")
scene.collection.children.link(coll)

paint = bpy.data.materials.get("ORDAX_V9_Graphite")
black = bpy.data.materials.get("ORDAX_V9_Black")
chrome = bpy.data.materials.get("ORDAX_V9_Chrome")
red = bpy.data.materials.get("ORDAX_V9_Red")
white = bpy.data.materials.get("ORDAX_V9_White")
amber = bpy.data.materials.get("ORDAX_V9_Amber")

glass = bpy.data.materials.get("ORDAX_V11_Glass") or bpy.data.materials.new("ORDAX_V11_Glass")
glass.use_nodes = True
p = glass.node_tree.nodes.get("Principled BSDF")
if p:
    p.inputs["Base Color"].default_value = (0.008,0.014,0.022,1)
    p.inputs["Roughness"].default_value = 0.12
    if p.inputs.get("Transmission Weight"):
        p.inputs["Transmission Weight"].default_value = 0.16

for obj in bpy.data.objects:
    n = obj.name
    if n.startswith(("ORDAX_V10_Windshield","ORDAX_V10_RearGlass","ORDAX_V10_FrontSideGlass",
                     "ORDAX_V10_RearSideGlass","ORDAX_V10_Roof","ORDAX_V10_A_Pillar",
                     "ORDAX_V10_B_Pillar","ORDAX_V10_C_Pillar","ORDAX_V10_WindowLowerTrim",
                     "ORDAX_V10_RoofTrim")):
        obj.hide_viewport = True
        obj.hide_render = True
    if n.startswith(("ORDAX_V9_Kidney","ORDAX_V9_Headlamp","ORDAX_V9_FrontIntake",
                     "ORDAX_V9_FrontSplitter","ORDAX_V9_TailHousing","ORDAX_V9_TailLED",
                     "ORDAX_V9_RearDiffuser","ORDAX_V9_Exhaust")):
        obj.hide_viewport = True
        obj.hide_render = True

def mesh_obj(name, verts, faces, mat):
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    if mat:
        me.materials.append(mat)
    return obj
def quad(name, pts, mat, thickness=0.008):
    obj = mesh_obj(name, pts, [(0,1,2,3)], mat)
    solid = obj.modifiers.new("thickness", "SOLIDIFY")
    solid.thickness = thickness
    bevel = obj.modifiers.new("edge_softening", "BEVEL")
    bevel.width = 0.004
    bevel.segments = 2
    return obj

def curve(name, pts, mat, radius=0.010):
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

def box(name, loc, dims, mat, bevel=0.020):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    coll.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("edge_softening", "BEVEL")
        mod.width = bevel
        mod.segments = 4
        mod.limit_method = "ANGLE"
    return obj

# Lower, more swept glasshouse.
quad("ORDAX_V11_Windshield",
     [(-0.79,-0.91,0.885),(0.79,-0.91,0.885),
      (0.655,-0.38,1.395),(-0.655,-0.38,1.395)], glass, 0.010)
quad("ORDAX_V11_RearGlass",
     [(-0.655,0.62,1.405),(0.655,0.62,1.405),
      (0.765,1.18,0.895),(-0.765,1.18,0.895)], glass, 0.010)

for sign in (-1,1):
    quad("ORDAX_V11_FrontSideGlass",
         [(0.83*sign,-0.87,0.89),(0.84*sign,0.06,0.89),
          (0.695*sign,0.06,1.435),(0.655*sign,-0.38,1.395)], glass)
    quad("ORDAX_V11_RearSideGlass",
         [(0.84*sign,0.08,0.89),(0.79*sign,1.05,0.89),
          (0.685*sign,0.62,1.405),(0.695*sign,0.08,1.435)], glass)
    curve("ORDAX_V11_A_Pillar",
          [(0.81*sign,-0.89,0.89),(0.655*sign,-0.38,1.395)], black, 0.022)
    curve("ORDAX_V11_B_Pillar",
          [(0.84*sign,0.07,0.89),(0.695*sign,0.07,1.435)], black, 0.024)
    curve("ORDAX_V11_C_Pillar",
          [(0.685*sign,0.62,1.405),(0.79*sign,1.15,0.89)], black, 0.027)
    curve("ORDAX_V11_BeltTrim",
          [(0.84*sign,-0.87,0.875),(0.84*sign,0.08,0.875),
           (0.79*sign,1.05,0.875)], chrome, 0.006)

# Curved roof grid.
ys = [-0.38,-0.18,0.08,0.36,0.62]
xs = [-1.0,-0.5,0.0,0.5,1.0]
verts = []
for yi, y in enumerate(ys):
    t = yi/(len(ys)-1)
    half = 0.665 - 0.010*abs(y-0.10)
    center_z = 1.395 + 0.045*math.sin(math.pi*t)
    for xn in xs:
        verts.append((xn*half, y, center_z + 0.018*(1-xn*xn)))
faces = []
nx = len(xs)
for iy in range(len(ys)-1):
    for ix in range(nx-1):
        a = iy*nx + ix
        faces.append((a,a+1,a+1+nx,a+nx))
roof = mesh_obj("ORDAX_V11_Roof", verts, faces, paint)
for poly in roof.data.polygons:
    poly.use_smooth = True
solid = roof.modifiers.new("roof_thickness","SOLIDIFY")
solid.thickness = 0.024
sub = roof.modifiers.new("roof_smoothing","SUBSURF")
sub.levels = 2
sub.render_levels = 2

front_y = -2.495
# Wider/lower twin grille.
for x in (-0.195,0.195):
    box("ORDAX_V11_GrilleFrame",(x,front_y,0.715),(0.350,0.032,0.205),chrome,0.038)
    box("ORDAX_V11_GrilleCore",(x,front_y-0.020,0.715),(0.310,0.026,0.165),black,0.032)
    for sx in (-0.09,-0.045,0.0,0.045,0.09):
        box("ORDAX_V11_GrilleSlat",(x+sx,front_y-0.038,0.715),(0.009,0.012,0.125),chrome,0.002)

# Slim light housings.
for sign in (-1,1):
    box("ORDAX_V11_HeadlampHousing",
        (0.605*sign,front_y-0.006,0.765),(0.555,0.036,0.135),black,0.030)
    outer = 0.865*sign
    mid = 0.650*sign
    inner = 0.355*sign
    curve("ORDAX_V11_LED_Upper",
          [(outer,front_y-0.038,0.797),(mid,front_y-0.042,0.790),(inner,front_y-0.039,0.790)],
          white, 0.009)
    curve("ORDAX_V11_LED_Lower",
          [(outer,front_y-0.039,0.760),(mid,front_y-0.043,0.750),(inner,front_y-0.040,0.770)],
          white, 0.008)
    box("ORDAX_V11_SideMarker",
        (0.878*sign,front_y-0.039,0.765),(0.016,0.014,0.055),amber,0.003)

box("ORDAX_V11_CenterIntake",
    (0,front_y,0.365),(0.760,0.042,0.135),black,0.040)
for sign in (-1,1):
    box("ORDAX_V11_SideIntake",
        (0.690*sign,front_y,0.360),(0.285,0.044,0.200),black,0.040)
box("ORDAX_V11_Splitter",
    (0,front_y+0.010,0.205),(1.570,0.060,0.040),black,0.015)
rear_y = 2.495
for sign in (-1,1):
    box("ORDAX_V11_TailHousing",
        (0.595*sign,rear_y,0.785),(0.600,0.036,0.135),black,0.030)
    outer = 0.885*sign
    mid = 0.620*sign
    inner = 0.305*sign
    curve("ORDAX_V11_TailLED",
          [(outer,rear_y+0.034,0.815),(mid,rear_y+0.040,0.815),
           (mid,rear_y+0.042,0.775),(inner,rear_y+0.038,0.775)],
          red,0.012)
    curve("ORDAX_V11_TailLower",
          [(outer,rear_y+0.036,0.775),(mid,rear_y+0.041,0.775),
           (inner,rear_y+0.038,0.752)], red,0.007)
box("ORDAX_V11_RearDiffuser",
    (0,rear_y-0.005,0.245),(1.500,0.055,0.145),black,0.038)
for sign in (-1,1):
    box("ORDAX_V11_ExhaustFrame",
        (0.690*sign,rear_y+0.035,0.245),(0.270,0.055,0.100),chrome,0.025)
    box("ORDAX_V11_ExhaustCore",
        (0.690*sign,rear_y+0.060,0.245),(0.225,0.020,0.064),black,0.018)

curve("ORDAX_V11_TrunkLip",
      [(-0.72,2.31,0.825),(0,2.335,0.835),(0.72,2.31,0.825)],
      paint,0.010)

scene["ordax_realistic_car_revision"] = "v11-cabin-face-refinement"
scene["ordax_reference_dimensions_m"] = [1.87,4.97,1.47]
scene["ordax_reference_wheelbase_m"] = 2.98
out = Path(bpy.path.abspath("//")) / "ordax_car_realistic_v11_reference_refined.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print({"ok":True,"revision":"v11","file":str(out),"objects":len(coll.objects)})
