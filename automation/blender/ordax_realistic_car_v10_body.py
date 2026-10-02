import bpy, math
from pathlib import Path
from mathutils import Vector

scene = bpy.context.scene

# Clean only prior v10 shell.
old = bpy.data.collections.get("ORDAX_V10_BODY")
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
coll = bpy.data.collections.new("ORDAX_V10_BODY")
scene.collection.children.link(coll)

def get_mat(name, fallback=(0.02,0.025,0.032,1)):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.diffuse_color = fallback
    return m

paint = get_mat("ORDAX_V9_Graphite")
paint_hi = get_mat("ORDAX_V9_Graphite_Highlight")
black = get_mat("ORDAX_V9_Black")
chrome = get_mat("ORDAX_V9_Chrome")
glass = bpy.data.materials.get("glass.001") or bpy.data.materials.get("glass")
if glass is None:
    glass = bpy.data.materials.new("ORDAX_V10_Glass")
    glass.use_nodes = True
    p = glass.node_tree.nodes.get("Principled BSDF")
    if p:
        if p.inputs.get("Base Color"):
            p.inputs["Base Color"].default_value=(0.008,0.015,0.024,1)
        if p.inputs.get("Roughness"):
            p.inputs["Roughness"].default_value=.08
        if p.inputs.get("Transmission Weight"):
            p.inputs["Transmission Weight"].default_value=.42

# Hide old imported exterior, keep interior/steering.
hide_names = {
    "saloon_0","saloon_1","saloon_2","saloon_4","saloon_6",
    "door-front-right.001","door-rear-right.001","door-front-left.001","door-rear-left.001",
    "bonnet.001","boot.001","saloon_21","saloon_22"
}
for name in hide_names:
    o = bpy.data.objects.get(name)
    if o:
        o.hide_viewport = True
        o.hide_render = True

def add_mesh(name, verts, faces, material, smooth=True):
    me = bpy.data.meshes.new(name+"_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    if material:
        me.materials.append(material)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return o

def add_bevel_subsurf(obj, bevel=0.012, levels=1):
    if bevel > 0:
        b = obj.modifiers.new("Body bevel","BEVEL")
        b.width = bevel
        b.segments = 3
        b.limit_method = "ANGLE"
    if levels > 0:
        s = obj.modifiers.new("Body subdivision","SUBSURF")
        s.subdivision_type = "CATMULL_CLARK"
        s.levels = levels
        s.render_levels = levels

# Smooth lower body loft using superellipse cross-sections.
stations = [
    (-2.485,0.86,0.47,0.30),
    (-2.300,0.92,0.50,0.35),
    (-1.900,0.95,0.51,0.40),
    (-1.500,0.96,0.50,0.43),
    (-0.900,0.96,0.49,0.44),
    ( 0.000,0.96,0.49,0.44),
    ( 0.900,0.96,0.49,0.43),
    ( 1.500,0.95,0.50,0.42),
    ( 1.950,0.93,0.50,0.39),
    ( 2.300,0.90,0.49,0.34),
    ( 2.485,0.86,0.47,0.29),
]
segments = 28
verts=[]
for y,w,cz,rz in stations:
    for j in range(segments):
        a=2*math.pi*j/segments
        c=math.cos(a); s=math.sin(a)
        # Squarer belt, rounder lower body.
        x = w * math.copysign(abs(c)**0.72, c)
        z = cz + rz * math.copysign(abs(s)**0.82, s)
        verts.append((x,y,z))
faces=[]
rings=len(stations)
for i in range(rings-1):
    for j in range(segments):
        nj=(j+1)%segments
        faces.append((i*segments+j,i*segments+nj,(i+1)*segments+nj,(i+1)*segments+j))
faces.append(tuple(reversed([j for j in range(segments)])))
base=(rings-1)*segments
faces.append(tuple(base+j for j in range(segments)))
body=add_mesh("ORDAX_V10_BodyShell",verts,faces,paint,True)

# Wheel arch booleans: local side cuts, not a full tunnel.
for side,x in (("L",-0.93),("R",0.93)):
    for axle,y in (("F",-1.49),("R",1.49)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=0.405,depth=0.60,
            location=(x,y,0.355),rotation=(0,math.pi/2,0))
        cut=bpy.context.object
        cut.name=f"__V10_ARCH_{axle}{side}"
        mod=body.modifiers.new(f"WheelArch_{axle}{side}","BOOLEAN")
        mod.operation="DIFFERENCE"
        mod.solver="EXACT"
        mod.object=cut
        bpy.context.view_layer.objects.active=body
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass
        bpy.data.objects.remove(cut,do_unlink=True)
add_bevel_subsurf(body,0.010,1)

# Helper for four-corner glass/panel surfaces.
def quad(name, pts, material, solidify=0.008, bevel=0.006):
    o=add_mesh(name,pts,[(0,1,2,3)],material,False)
    if solidify:
        s=o.modifiers.new("Panel thickness","SOLIDIFY")
        s.thickness=solidify
    if bevel:
        b=o.modifiers.new("Panel bevel","BEVEL")
        b.width=bevel
        b.segments=2
    return o

# Modern windshield and rear glass slopes.
quad("ORDAX_V10_Windshield",
     [(-0.78,-0.96,0.885),(0.78,-0.96,0.885),(0.675,-0.54,1.435),(-0.675,-0.54,1.435)],
     glass,0.010,0.004)
quad("ORDAX_V10_RearGlass",
     [(-0.675,0.80,1.435),(0.675,0.80,1.435),(0.765,1.22,0.895),(-0.765,1.22,0.895)],
     glass,0.010,0.004)

# Side windows split by B-pillar.
for sign in (-1,1):
    x0=sign*0.835
    xt=sign*0.710
    quad("ORDAX_V10_FrontSideGlass",
         [(x0,-0.91,0.890),(x0,0.02,0.890),(xt,0.02,1.475),(sign*0.675,-0.54,1.435)],
         glass,0.008,0.004)
    quad("ORDAX_V10_RearSideGlass",
         [(x0,0.05,0.890),(sign*0.810,1.08,0.885),(sign*0.675,0.80,1.435),(xt,0.05,1.475)],
         glass,0.008,0.004)

# Gently crowned roof patch.
roof_ys=[-0.55,-0.20,0.20,0.55,0.82]
roof_xs=[-0.70,-0.35,0.0,0.35,0.70]
rverts=[]
for y in roof_ys:
    width=0.70 - 0.035*abs(y-0.15)
    for xn in roof_xs:
        x=xn*(width/0.70)
        dome=0.030*(1-(x/max(width,0.001))**2)
        z=1.455 + dome - 0.020*((y-0.18)/0.70)**2
        rverts.append((x,y,z))
rfaces=[]
nx=len(roof_xs); ny=len(roof_ys)
for iy in range(ny-1):
    for ix in range(nx-1):
        a=iy*nx+ix
        rfaces.append((a,a+1,a+1+nx,a+nx))
roof=add_mesh("ORDAX_V10_Roof",rverts,rfaces,paint,True)
sol=roof.modifiers.new("Roof thickness","SOLIDIFY"); sol.thickness=.025
bev=roof.modifiers.new("Roof bevel","BEVEL"); bev.width=.010; bev.segments=3
sub=roof.modifiers.new("Roof smooth","SUBSURF"); sub.levels=1; sub.render_levels=1

# Hood and trunk upper panels flatten the capsule and match the reference.
def top_patch(name, y0,y1,w0,w1,z0,z1):
    ys=[y0,(2*y0+y1)/3,(y0+2*y1)/3,y1]
    xs=[-1,-0.5,0,0.5,1]
    vv=[]
    for iy,y in enumerate(ys):
        t=iy/(len(ys)-1)
        w=w0*(1-t)+w1*t
        zc=z0*(1-t)+z1*t
        for xn in xs:
            crown=0.018*(1-xn*xn)
            vv.append((xn*w,y,zc+crown))
    ff=[]
    nx=len(xs)
    for iy in range(len(ys)-1):
        for ix in range(nx-1):
            a=iy*nx+ix
            ff.append((a,a+1,a+1+nx,a+nx))
    o=add_mesh(name,vv,ff,paint,True)
    so=o.modifiers.new("Panel thickness","SOLIDIFY"); so.thickness=.018
    be=o.modifiers.new("Panel bevel","BEVEL"); be.width=.008; be.segments=2
    su=o.modifiers.new("Panel smooth","SUBSURF"); su.levels=1; su.render_levels=1
    return o

top_patch("ORDAX_V10_Hood",-2.28,-0.92,0.78,0.82,0.835,0.925)
top_patch("ORDAX_V10_Trunk",1.20,2.30,0.78,0.74,0.900,0.805)

# Pillars and trim curves.
def curve(name, pts, material, bevel=0.012):
    cu=bpy.data.curves.new(name+"_curve","CURVE")
    cu.dimensions="3D"; cu.bevel_depth=bevel; cu.bevel_resolution=3
    sp=cu.splines.new("POLY"); sp.points.add(len(pts)-1)
    for i,p in enumerate(pts): sp.points[i].co=(*p,1)
    o=bpy.data.objects.new(name,cu); coll.objects.link(o); cu.materials.append(material)
    return o

for sign in (-1,1):
    x=sign
    curve("ORDAX_V10_A_Pillar",[(0.81*x,-0.94,0.89),(0.69*x,-0.54,1.44)],black,.024)
    curve("ORDAX_V10_B_Pillar",[(0.84*x,0.03,0.89),(0.71*x,0.03,1.47)],black,.026)
    curve("ORDAX_V10_C_Pillar",[(0.70*x,0.80,1.43),(0.80*x,1.18,0.90)],black,.027)
    curve("ORDAX_V10_WindowLowerTrim",[(0.84*x,-0.91,0.875),(0.84*x,1.08,0.875)],chrome,.009)
    curve("ORDAX_V10_RoofTrim",[(0.69*x,-0.54,1.44),(0.71*x,0.03,1.48),(0.69*x,0.80,1.44)],chrome,.008)

# Door shut lines and handles.
for sign in (-1,1):
    x=0.965*sign
    for y in (-0.78,0.10,1.08):
        curve("ORDAX_V10_DoorSeam",[(x,y,0.245),(x,y,0.865)],black,.006)
    for y in (-0.28,0.62):
        bpy.ops.mesh.primitive_cube_add(location=(x,y,0.715))
        h=bpy.context.object
        h.name="ORDAX_V10_DoorHandle"
        h.dimensions=(0.025,0.155,0.032)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(h.users_collection): c.objects.unlink(h)
        coll.objects.link(h)
        h.data.materials.append(chrome)
        b=h.modifiers.new("Handle bevel","BEVEL"); b.width=.010; b.segments=3

# Wheel arch lips following the new cut-outs.
for sign in (-1,1):
    x=0.972*sign
    for y0 in (-1.49,1.49):
        pts=[]
        for i in range(17):
            a=math.pi*i/16
            pts.append((x,y0+math.cos(a)*0.405,0.355+math.sin(a)*0.405))
        curve("ORDAX_V10_ArchLip",pts,paint_hi,.010)

# Subtle side sill.
for sign in (-1,1):
    curve("ORDAX_V10_SideSill",[(0.965*sign,-1.20,0.205),(0.970*sign,0.0,0.190),(0.960*sign,1.22,0.205)],black,.020)

# Ensure existing v9 details remain visible and fit the new body.
v9=bpy.data.collections.get("ORDAX_V9_REFERENCE")
if v9:
    for o in v9.objects:
        o.hide_render=False
        o.hide_viewport=False

scene["ordax_realistic_car_revision"]="v10-procedural-modern-body"
scene["ordax_reference_target"]="user supplied multi-view modern dark sport sedan"
scene["ordax_reference_dimensions_m"]=[1.87,4.97,1.47]
scene["ordax_reference_wheelbase_m"]=2.98

out=Path(bpy.path.abspath("//"))/"ordax_car_realistic_v10_reference_body.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print({"ok":True,"revision":"v10","file":str(out),"body_objects":len(coll.objects)})
