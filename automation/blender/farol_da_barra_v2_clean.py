import bpy, math, json
from pathlib import Path
from mathutils import Vector

scene=bpy.context.scene
COL_BUILD=bpy.data.collections.get("02_EDIFICIOS")
COL_DETAIL=bpy.data.collections.get("04_DETALHES")
COL_FORT=bpy.data.collections.get("01_FORTE")
COL_SITE=bpy.data.collections.get("05_TERRENO")

WHITE=bpy.data.materials.get("FAB_CalBranca")
TILE=bpy.data.materials.get("FAB_TelhaCeramica")
STONE=bpy.data.materials.get("FAB_Pedra")
WOOD=bpy.data.materials.get("FAB_MadeiraEscura")
IRON=bpy.data.materials.get("FAB_Ferro")
DARK=bpy.data.materials.get("FAB_AberturaEscura")
BLACK=bpy.data.materials.get("FAB_Preto")

GREEN=bpy.data.materials.get("FAB_CaixilhariaVerde") or bpy.data.materials.new("FAB_CaixilhariaVerde")
GREEN.use_nodes=True
pg=GREEN.node_tree.nodes.get("Principled BSDF")
pg.inputs["Base Color"].default_value=(0.035,0.075,0.055,1)
pg.inputs["Roughness"].default_value=0.68

SANDSTONE=bpy.data.materials.get("FAB_Arenito") or bpy.data.materials.new("FAB_Arenito")
SANDSTONE.use_nodes=True
ps=SANDSTONE.node_tree.nodes.get("Principled BSDF")
ps.inputs["Base Color"].default_value=(0.43,0.34,0.23,1)
ps.inputs["Roughness"].default_value=0.80

BLUE=bpy.data.materials.get("FAB_BrasaoAzul") or bpy.data.materials.new("FAB_BrasaoAzul")
BLUE.diffuse_color=(0.025,0.16,0.30,1)
GOLD=bpy.data.materials.get("FAB_BrasaoDourado") or bpy.data.materials.new("FAB_BrasaoDourado")
GOLD.diffuse_color=(0.70,0.45,0.08,1)

def relink(obj,coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj

def box(name,loc,dims,mat,coll,bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    relink(o,coll)
    if mat:o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new("Bevel","BEVEL"); b.width=bevel; b.segments=3; b.limit_method="ANGLE"
    return o

def hip_roof(name,cx,cy,sx,sy,eave,ridge,mat):
    end=1.8
    verts=[
        (cx-sx/2,cy-sy/2,eave),(cx+sx/2,cy-sy/2,eave),
        (cx+sx/2,cy+sy/2,eave),(cx-sx/2,cy+sy/2,eave),
        (cx-sx/2+end,cy,ridge),(cx+sx/2-end,cy,ridge)
    ]
    faces=[(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)]
    me=bpy.data.meshes.new(name+"_mesh"); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); COL_BUILD.objects.link(o); me.materials.append(mat)
    return o

def facade_window(name,x,y,z,w=1.05,h=1.35):
    frame=box(name+"_Frame",(x,y,z),(w+0.22,0.16,h+0.22),SANDSTONE,COL_DETAIL,0.035)
    opening=box(name+"_Opening",(x,y-0.10,z),(w,0.07,h),DARK,COL_DETAIL,0.02)
    for dx in (-w*0.26,w*0.26):
        box(name+"_V",(x+dx,y-0.16,z),(0.045,0.04,h*0.92),GREEN,COL_DETAIL)
    box(name+"_H",(x,y-0.16,z),(w*0.92,0.04,0.045),GREEN,COL_DETAIL)

# Reposition front range close to the landward stone facade.
front=bpy.data.objects.get("FAB_Edif_Frontal")
if front:
    front.location.y=-14.15
    front.dimensions.y=3.8
    bpy.context.view_layer.objects.active=front
old_roof=bpy.data.objects.get("FAB_Telhado_Frontal")
if old_roof:
    old_roof.hide_viewport=True; old_roof.hide_render=True
hip_roof("FAB_Telhado_Frontal_V2",0,-14.15,31.6,4.6,10.52,11.45,TILE)

# Move side ranges forward; they form the characteristic U around the courtyard.
for side in ("Leste","Oeste"):
    o=bpy.data.objects.get("FAB_Edif_"+side)
    if o: o.location.y=-5.2
    r=bpy.data.objects.get("FAB_Telhado_"+side)
    if r: r.hide_viewport=True; r.hide_render=True
x=13.1
hip_roof("FAB_Telhado_Leste_V2", x,-5.2,6.3,11.5,10.35,11.30,TILE)
hip_roof("FAB_Telhado_Oeste_V2",-x,-5.2,6.3,11.5,10.35,11.30,TILE)

# Hide first-pass upper facade windows and recreate closer to the wall.
for o in bpy.data.objects:
    if o.name.startswith("FAB_Janela_Frontal_"):
        o.hide_viewport=True; o.hide_render=True
for i,xw in enumerate((-12.0,-8.2,-4.4,-0.6,3.2,7.0,10.8)):
    facade_window(f"FAB_V2_Janela_{i+1}",xw,-16.08,8.95)

# Front white strip from first parapet is hidden behind the proper facade.
p=bpy.data.objects.get("FAB_Parapeito_00")
if p:
    p.hide_viewport=True; p.hide_render=True

# More substantial sandstone entrance frame and coat of arms.
for n in ("FAB_Entrada_PilarE","FAB_Entrada_PilarD","FAB_Entrada_Lintel","FAB_Brasao_Base","FAB_Brasao_Medalhao"):
    o=bpy.data.objects.get(n)
    if o: o.hide_viewport=True; o.hide_render=True

box("FAB_V2_Portada_E",(-1.55,-18.72,3.15),(0.48,0.28,4.25),SANDSTONE,COL_DETAIL,0.05)
box("FAB_V2_Portada_D",(1.55,-18.72,3.15),(0.48,0.28,4.25),SANDSTONE,COL_DETAIL,0.05)
box("FAB_V2_Portada_Lintel",(0,-18.72,5.28),(3.55,0.28,0.48),SANDSTONE,COL_DETAIL,0.05)
box("FAB_V2_Brasao_Base",(0,-18.78,6.25),(2.30,0.22,1.28),SANDSTONE,COL_DETAIL,0.07)

# Simplified heraldic shield relief.
box("FAB_V2_Escudo_Azul",(0,-18.92,6.25),(0.78,0.08,0.78),BLUE,COL_DETAIL,0.09)
box("FAB_V2_Escudo_CruzV",(0,-18.98,6.25),(0.10,0.04,0.65),GOLD,COL_DETAIL,0.02)
box("FAB_V2_Escudo_CruzH",(0,-18.98,6.25),(0.55,0.04,0.10),GOLD,COL_DETAIL,0.02)

# Entry door timber behind the dark opening.
box("FAB_V2_Porta",(0,-18.63,3.25),(2.05,0.10,3.15),WOOD,COL_DETAIL,0.05)

# Add narrow facade cornice above stone wall.
box("FAB_V2_Cornija_Frontal",(0,-17.55,7.20),(35.6,0.48,0.38),WHITE,COL_DETAIL,0.08)

# Side building windows.
for side,xw,face_y in (("E",13.1,-5.2),("W",-13.1,-5.2)):
    for j,yw in enumerate((-8.2,-5.4,-2.6)):
        # outward-facing decorative window panels on the side wings
        xface=xw + (2.93 if xw>0 else -2.93)
        box(f"FAB_V2_Side_{side}_{j}_Frame",(xface,yw,8.90),(0.15,1.28,1.55),SANDSTONE,COL_DETAIL,0.04)
        box(f"FAB_V2_Side_{side}_{j}_Dark",(xface+(0.09 if xw>0 else -0.09),yw,8.90),(0.06,1.04,1.30),DARK,COL_DETAIL,0.02)

# Improve tower band transitions with masonry moldings.
for z in (10.45,15.65,19.55,23.25):
    bpy.ops.mesh.primitive_torus_add(major_radius=2.25-(z-10.45)*0.018,minor_radius=0.065,
        major_segments=72,minor_segments=12,location=(0,4.3,z))
    t=bpy.context.object; t.name="FAB_V2_Torre_Moldura"; relink(t,COL_DETAIL); t.data.materials.append(WHITE if z in (15.65,23.25) else BLACK)

# Add white surrounds to tower windows.
for name in ("FAB_Torre_Janela_1","FAB_Torre_Janela_2","FAB_Torre_Janela_3"):
    o=bpy.data.objects.get(name)
    if not o: continue
    mat=WHITE if o.location.z>19.0 or o.location.z<15.0 else BLACK
    frame=box(name+"_Surround",o.location,(o.dimensions.x+0.18,0.08,o.dimensions.z+0.18),mat,COL_DETAIL,0.04)
    frame.rotation_euler=o.rotation_euler.copy()
    o.location += Vector((0,-0.03,0))

# Add lamp/lens core.
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=(0,4.3,26.25),scale=(0.48,0.48,0.38))
lamp=bpy.context.object; lamp.name="FAB_V2_Lente_Fresnel"; relink(lamp,COL_DETAIL)
LENS=bpy.data.materials.get("FAB_Lente") or bpy.data.materials.new("FAB_Lente"); LENS.use_nodes=True
pl=LENS.node_tree.nodes.get("Principled BSDF"); pl.inputs["Base Color"].default_value=(0.75,0.88,0.90,1); pl.inputs["Metallic"].default_value=0.25; pl.inputs["Roughness"].default_value=0.08
lamp.data.materials.append(LENS)

# A simple dry-moat/rock border around the fort instead of a perfect circular lawn edge.
ROCK=bpy.data.materials.get("FAB_Rocha") or bpy.data.materials.new("FAB_Rocha"); ROCK.use_nodes=True
pr=ROCK.node_tree.nodes.get("Principled BSDF"); pr.inputs["Base Color"].default_value=(0.15,0.13,0.11,1); pr.inputs["Roughness"].default_value=0.92
for i in range(42):
    a=2*math.pi*i/42
    r=27.0+1.6*math.sin(i*2.7)
    x,y=math.cos(a)*r,math.sin(a)*r
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1.5+0.55*math.sin(i),location=(x,y,-0.2))
    ro=bpy.context.object; ro.name="FAB_V2_Rocha"; ro.scale=(1.8,1.2,0.75); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    relink(ro,COL_SITE); ro.data.materials.append(ROCK)

scene["ordax_revision"]="farol-da-barra-v2-refine"
scene["ordax_reference_plan"]="irregular decagon; historical Caldas plan and current aerial imagery"
out=Path(bpy.path.abspath("//"))/"farol_da_barra_v2_refine.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print(json.dumps({"ok":True,"file":str(out),"revision":"farol-da-barra-v2"}))