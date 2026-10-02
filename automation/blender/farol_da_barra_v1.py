import bpy, math, json
from pathlib import Path
from mathutils import Vector

# Farol da Barra / Forte de Santo Antonio da Barra
# Scale: meters. Current masonry lighthouse tower: 22 m total.
# References: IALA heritage, HPIP, Wikimedia aerial photographs.
OUT_DIR = Path(bpy.path.abspath("//")).resolve()
OUT_FILE = OUT_DIR / "farol_da_barra_v1.blend"

# Start clean without restarting Blender/companion.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
    for block in list(datablocks):
        if block.users == 0:
            datablocks.remove(block)

scene = bpy.context.scene
scene.name = "FAROL DA BARRA | SALVADOR"
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

# Collections
for c in list(bpy.data.collections):
    if c.name != "Collection" and c.users == 0:
        bpy.data.collections.remove(c)
root = bpy.data.collections.get("Collection")
root.name = "FAROL_DA_BARRA"

def new_collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

COL_FORT = new_collection("01_FORTE")
COL_BUILD = new_collection("02_EDIFICIOS")
COL_TOWER = new_collection("03_FAROL")
COL_DETAIL = new_collection("04_DETALHES")
COL_SITE = new_collection("05_TERRENO")

def relink(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj

def mat_principled(name, color, rough=0.45, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    return m

STONE = mat_principled("FAB_Pedra", (0.24,0.22,0.18,1), 0.88, 0.0)
WHITE = mat_principled("FAB_CalBranca", (0.86,0.84,0.77,1), 0.72, 0.0)
BLACK = mat_principled("FAB_Preto", (0.008,0.009,0.010,1), 0.38, 0.05)
TILE = mat_principled("FAB_TelhaCeramica", (0.34,0.11,0.045,1), 0.82, 0.0)
WOOD = mat_principled("FAB_MadeiraEscura", (0.12,0.055,0.025,1), 0.72, 0.0)
IRON = mat_principled("FAB_Ferro", (0.018,0.020,0.022,1), 0.30, 0.72)
GLASS = mat_principled("FAB_VidroLanterna", (0.16,0.24,0.27,1), 0.12, 0.0)
GRASS = mat_principled("FAB_Grama", (0.11,0.20,0.07,1), 0.95, 0.0)
PATH = mat_principled("FAB_Calcada", (0.48,0.43,0.34,1), 0.90, 0.0)
DARK = mat_principled("FAB_AberturaEscura", (0.012,0.014,0.014,1), 0.60, 0.0)

# Procedural stone relief.
p = STONE.node_tree.nodes.get("Principled BSDF")
noise = STONE.node_tree.nodes.get("FAB_StoneNoise") or STONE.node_tree.nodes.new("ShaderNodeTexNoise")
noise.name = "FAB_StoneNoise"
noise.inputs["Scale"].default_value = 6.5
noise.inputs["Detail"].default_value = 6.0
noise.inputs["Roughness"].default_value = 0.75
bump = STONE.node_tree.nodes.get("FAB_StoneBump") or STONE.node_tree.nodes.new("ShaderNodeBump")
bump.name = "FAB_StoneBump"
bump.inputs["Strength"].default_value = 0.38
bump.inputs["Distance"].default_value = 0.16
STONE.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
STONE.node_tree.links.new(bump.outputs["Normal"], p.inputs["Normal"])

def box(name, loc, dims, material, coll, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    relink(o, coll)
    if material:
        o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    return o

def cylinder(name, loc, radius, depth, material, coll, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    relink(o, coll)
    o.data.materials.append(material)
    for poly in o.data.polygons:
        poly.use_smooth = True
    return o

def frustum(name, z0, h, r0, r1, material, coll, segments=72):
    verts, faces = [], []
    for z, r in ((z0,r0),(z0+h,r1)):
        for i in range(segments):
            a = 2*math.pi*i/segments
            verts.append((math.cos(a)*r, math.sin(a)*r, z))
    for i in range(segments):
        j = (i+1)%segments
        faces.append((i,j,segments+j,segments+i))
    faces.append(tuple(reversed(range(segments))))
    faces.append(tuple(segments+i for i in range(segments)))
    me = bpy.data.meshes.new(name+"_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    me.materials.append(material)
    for poly in me.polygons:
        poly.use_smooth = True
    return o

def ring_segment(name, p1, p2, z, width, height, material, coll):
    x1,y1 = p1; x2,y2 = p2
    dx,dy = x2-x1,y2-y1
    L = math.hypot(dx,dy)
    o = box(name, ((x1+x2)/2,(y1+y2)/2,z), (L,width,height), material, coll, 0.06)
    o.rotation_euler[2] = math.atan2(dy,dx)
    return o

def polygon_prism(name, pts, z0, z1, material, coll, bottom_scale=1.0):
    cx = sum(p[0] for p in pts)/len(pts)
    cy = sum(p[1] for p in pts)/len(pts)
    top = [(x,y,z1) for x,y in pts]
    bot = [(cx+(x-cx)*bottom_scale, cy+(y-cy)*bottom_scale, z0) for x,y in pts]
    verts = bot + top
    n = len(pts)
    faces = [tuple(reversed(range(n))), tuple(n+i for i in range(n))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,n+j,n+i))
    me=bpy.data.meshes.new(name+"_mesh")
    me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); coll.objects.link(o)
    me.materials.append(material)
    return o

def gable_roof(name, loc, sx, sy, eave_z, ridge_z, material, coll):
    x,y = loc
    verts=[
        (x-sx/2,y-sy/2,eave_z),(x+sx/2,y-sy/2,eave_z),
        (x+sx/2,y+sy/2,eave_z),(x-sx/2,y+sy/2,eave_z),
        (x-sx/2,y,ridge_z),(x+sx/2,y,ridge_z)
    ]
    faces=[(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)]
    me=bpy.data.meshes.new(name+"_mesh")
    me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); coll.objects.link(o)
    me.materials.append(material)
    return o

def window(name, x, y, z, w=1.15, h=1.45, face="front"):
    if face=="front":
        frame=box(name+"_frame",(x,y,z),(w+0.18,0.12,h+0.18),WOOD,COL_DETAIL,0.03)
        pane=box(name+"_dark",(x,y-0.07,z),(w,0.06,h),DARK,COL_DETAIL,0.02)
        for dx in (-w/4,w/4):
            box(name+"_barV",(x+dx,y-0.11,z),(0.045,0.035,h),IRON,COL_DETAIL)
        box(name+"_barH",(x,y-0.11,z),(w,0.035,0.045),IRON,COL_DETAIL)
    return

# Site base / grassy promontory
cylinder("FAB_GrassyBase",(0,0,-0.55),31.0,1.1,GRASS,COL_SITE,96)
box("FAB_EntrancePath",(0,-27.0,0.04),(4.0,22.0,0.10),PATH,COL_SITE,0.25)

# Fort footprint - decagonal irregular polygon.
fort_pts=[
    (-19,-18),(19,-18),(24,-10),(23,6),(14,15),
    (6,19),(-6,19),(-14,15),(-23,6),(-24,-10)
]
fort = polygon_prism("FAB_MuralhaPrincipal", fort_pts, 0.0, 7.0, STONE, COL_FORT, bottom_scale=1.08)

# White parapet along the top edge.
for i,p1 in enumerate(fort_pts):
    p2=fort_pts[(i+1)%len(fort_pts)]
    ring_segment(f"FAB_Parapeito_{i:02d}",p1,p2,7.55,0.62,1.10,WHITE,COL_FORT)

# Central terrace.
terrace_pts=[(x*0.78,y*0.78) for x,y in fort_pts]
polygon_prism("FAB_Terraco",terrace_pts,7.0,7.18,WHITE,COL_FORT,1.0)

# Main white ranges and roofs.
box("FAB_Edif_Frontal",(0,-10.9,8.85),(31.0,5.6,3.4),WHITE,COL_BUILD,0.08)
gable_roof("FAB_Telhado_Frontal",(0,-10.9),31.7,6.3,10.55,11.65,TILE,COL_BUILD)

box("FAB_Edif_Leste",(13.1,-2.4,8.75),(5.7,11.2,3.2),WHITE,COL_BUILD,0.08)
gable_roof("FAB_Telhado_Leste",(13.1,-2.4),6.3,11.8,10.35,11.45,TILE,COL_BUILD)

box("FAB_Edif_Oeste",(-13.1,-2.4,8.75),(5.7,11.2,3.2),WHITE,COL_BUILD,0.08)
gable_roof("FAB_Telhado_Oeste",(-13.1,-2.4),6.3,11.8,10.35,11.45,TILE,COL_BUILD)

# Front facade windows.
for i,x in enumerate((-12.0,-8.3,-4.6,-0.9,2.8,6.5,10.2)):
    window(f"FAB_Janela_Frontal_{i+1}",x,-13.73,9.0,1.05,1.35)

# Entrance arch cutter: box + cylinder boolean.
box("FAB_EntradaEscura",(0,-18.58,3.05),(2.4,0.16,3.7),DARK,COL_DETAIL,0.12)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.2,depth=0.18,location=(0,-18.60,4.55),rotation=(math.pi/2,0,0))
arch=bpy.context.object; arch.name="FAB_ArcoSuperiorEscuro"; relink(arch,COL_DETAIL); arch.data.materials.append(DARK)

# Stone entrance frame and crest.
box("FAB_Entrada_PilarE",(-1.43,-18.66,3.15),(0.35,0.20,4.1),STONE,COL_DETAIL,0.04)
box("FAB_Entrada_PilarD",(1.43,-18.66,3.15),(0.35,0.20,4.1),STONE,COL_DETAIL,0.04)
box("FAB_Entrada_Lintel",(0,-18.66,5.25),(3.2,0.20,0.42),STONE,COL_DETAIL,0.04)
box("FAB_Brasao_Base",(0,-18.73,6.20),(2.15,0.18,1.15),WHITE,COL_DETAIL,0.08)
cylinder("FAB_Brasao_Medalhao",(0,-18.86,6.20),0.48,0.12,STONE,COL_DETAIL,48).rotation_euler[0]=math.pi/2

# Barred lower embrasures / windows.
for x in (-7.2,7.2):
    box("FAB_AberturaMuralha",(x,-18.66,3.2),(1.25,0.16,1.75),DARK,COL_DETAIL,0.04)
    for bx in (-0.38,-0.13,0.13,0.38):
        box("FAB_Grade",(x+bx,-18.78,3.2),(0.045,0.05,1.55),IRON,COL_DETAIL)

# Front corner sentry turrets.
for x in (-17.1,17.1):
    cylinder("FAB_Guarita_Corpo",(x,-15.7,7.75),0.90,2.8,STONE,COL_DETAIL,48)
    bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=1.05,radius2=0.12,depth=1.0,location=(x,-15.7,9.65))
    cap=bpy.context.object; cap.name="FAB_Guarita_Cupula"; relink(cap,COL_DETAIL); cap.data.materials.append(STONE)
    cylinder("FAB_Guarita_Bola",(x,-15.7,10.25),0.12,0.35,STONE,COL_DETAIL,24)

# Lighthouse tower: 22m from terrace to finial.
tower_base_z=7.25
masonry_h=16.0
base_r=2.75
top_r=2.05
bands=[(0.0,3.2,BLACK),(3.2,5.2,WHITE),(8.4,3.9,BLACK),(12.3,3.7,WHITE)]
for idx,(offset,h,mat) in enumerate(bands):
    r0=base_r+(top_r-base_r)*(offset/masonry_h)
    r1=base_r+(top_r-base_r)*((offset+h)/masonry_h)
    frustum(f"FAB_Torre_Banda_{idx+1}",tower_base_z+offset,h,r0,r1,mat,COL_TOWER)

# Tower plinth.
cylinder("FAB_Torre_Plinto",(0,4.3,tower_base_z+0.20),3.15,0.40,WHITE,COL_TOWER,72)

# Move tower bands to their true plan location (toward sea side).
for obj in list(COL_TOWER.objects):
    obj.location.y += 4.3

# Tower windows, approximate observed placements.
def tower_window(name, z, angle_deg, w=0.65, h=0.85):
    a=math.radians(angle_deg)
    frac=(z-tower_base_z)/masonry_h
    r=base_r+(top_r-base_r)*frac + 0.025
    x=math.cos(a)*r; y=4.3+math.sin(a)*r
    o=box(name,(x,y,z),(w,0.11,h),DARK,COL_DETAIL,0.08)
    o.rotation_euler[2]=a-math.pi/2
    return o
tower_window("FAB_Torre_Janela_1",11.6,-90,0.72,0.90)
tower_window("FAB_Torre_Janela_2",16.6,-90,0.60,0.72)
tower_window("FAB_Torre_Janela_3",21.7,-90,0.55,0.60)

# Gallery and lantern.
gallery_z=tower_base_z+masonry_h
cylinder("FAB_Galeria_Base",(0,4.3,gallery_z+0.18),2.45,0.36,BLACK,COL_TOWER,72)
cylinder("FAB_Galeria_Piso",(0,4.3,gallery_z+0.44),2.70,0.16,IRON,COL_TOWER,72)

# Railing posts and rings.
for i in range(24):
    a=2*math.pi*i/24
    x=math.cos(a)*2.45; y=4.3+math.sin(a)*2.45
    box("FAB_Galeria_Post",(x,y,gallery_z+1.0),(0.055,0.055,1.15),IRON,COL_DETAIL)
bpy.ops.mesh.primitive_torus_add(major_radius=2.45,minor_radius=0.045,major_segments=72,minor_segments=10,location=(0,4.3,gallery_z+0.55))
relink(bpy.context.object,COL_DETAIL); bpy.context.object.data.materials.append(IRON); bpy.context.object.name="FAB_Galeria_RingLow"
bpy.ops.mesh.primitive_torus_add(major_radius=2.45,minor_radius=0.045,major_segments=72,minor_segments=10,location=(0,4.3,gallery_z+1.45))
relink(bpy.context.object,COL_DETAIL); bpy.context.object.data.materials.append(IRON); bpy.context.object.name="FAB_Galeria_RingHigh"

# Lantern cabin.
cylinder("FAB_Lanterna_Base",(0,4.3,gallery_z+1.62),1.88,0.28,BLACK,COL_TOWER,72)
cylinder("FAB_Lanterna_Vidro",(0,4.3,gallery_z+2.95),1.68,2.45,GLASS,COL_TOWER,72)
for i in range(16):
    a=2*math.pi*i/16
    x=math.cos(a)*1.70; y=4.3+math.sin(a)*1.70
    box("FAB_Lanterna_Mullion",(x,y,gallery_z+2.95),(0.055,0.055,2.55),IRON,COL_DETAIL)
cylinder("FAB_Lanterna_Cornija",(0,4.3,gallery_z+4.20),1.88,0.24,BLACK,COL_TOWER,72)

# Black dome and finial.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,location=(0,4.3,gallery_z+4.70))
dome=bpy.context.object; dome.name="FAB_Lanterna_Cupula"; dome.scale=(1.90,1.90,0.78)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
relink(dome,COL_TOWER); dome.data.materials.append(BLACK)
# Hide lower half by intersecting into cornice; visually yields rounded cap.
cylinder("FAB_Lanterna_FinialStem",(0,4.3,gallery_z+5.50),0.10,0.46,BLACK,COL_TOWER,24)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(0,4.3,gallery_z+5.80),scale=(0.18,0.18,0.18))
ball=bpy.context.object; ball.name="FAB_Lanterna_FinialBall"; relink(ball,COL_TOWER); ball.data.materials.append(BLACK)

# Roof lettering seen in aerial views.
bpy.ops.object.text_add(location=(0,-4.8,11.72),rotation=(0,0,0))
txt=bpy.context.object; txt.name="FAB_MARINHA_DO_BRASIL"; txt.data.body="MARINHA DO BRASIL"
txt.data.align_x="CENTER"; txt.data.align_y="CENTER"; txt.data.size=1.05; txt.data.extrude=0.018
txt.rotation_euler=(0,0,0); txt.scale=(1,1,1)
relink(txt,COL_DETAIL); txt.data.materials.append(BLACK)

# Simple presentation.
scene.world.color=(0.035,0.050,0.065)
bpy.ops.object.light_add(type="SUN", location=(12,-18,35))
sun=bpy.context.object; sun.name="FAB_Sun"; sun.data.energy=2.2; sun.rotation_euler=(math.radians(28),0,math.radians(32))
relink(sun,COL_SITE)
bpy.ops.object.light_add(type="AREA", location=(0,-28,24))
area=bpy.context.object; area.name="FAB_Fill"; area.data.energy=1300; area.data.shape="DISK"; area.data.size=16
area.rotation_euler=(math.radians(28),0,0); relink(area,COL_SITE)

scene["ordax_asset"]="Farol da Barra / Forte de Santo Antonio da Barra"
scene["ordax_scale"]="meters"
scene["ordax_lighthouse_height_m"]=22.0
scene["ordax_revision"]="farol-da-barra-v1"
scene["ordax_reference_notes"]="IALA: 22m conical masonry tower, 1839; HPIP: late-17th-century star polygon fort; aerial Wikimedia refs."

bpy.ops.wm.save_as_mainfile(filepath=str(OUT_FILE))
print(json.dumps({"ok":True,"file":str(OUT_FILE),"objects":len(bpy.data.objects),"revision":"farol-da-barra-v1"}))
