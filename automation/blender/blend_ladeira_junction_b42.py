"""B42: preserva a pista compartilhada da Ladeira da Misericórdia na junção e mistura suavemente para o perfil corrigido."""
import bpy,json,hashlib,runpy,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]; scene=bpy.context.scene
registry_path=root/"world/areas/mvp-centro-lacerda/blender-revisions.json"
reg=json.loads(registry_path.read_text(encoding="utf8")); src=reg["validation_source"]
assert src["revision"]=="R30B.42"
assert Path(bpy.data.filepath).resolve()==(root/src["file"]).resolve()
report_path=root/"docs/reports/blender/misericordia_surface_r30b42.json"
report=json.loads(report_path.read_text(encoding="utf8"))
contract=json.loads((root/"world/areas/mvp-centro-lacerda/production.json").read_text(encoding="utf8"))
api=runpy.run_path(str(root/"automation/blender/component_fingerprint.py")); wm=api["world_matrix"]; signature=api["signature"]

ground=scene.objects[contract["export"]["road_object"]]
proxy=scene.objects[contract["export"]["terrain_proxy"]]
miser=scene.objects["R30A7 | ROAD | 803899198"]
ladeira=scene.objects["R30A7 | ROAD | 103595139"]
protected={o.name:signature(o) for o in scene.objects if o.type in {"MESH","CURVE","FONT"} and o not in {ground,proxy,miser}}

# Carrega somente a malha B41 como baseline; usa o transform do ground atual, pois objeto de library não linkado não resolve matrix_world.
before_o=set(bpy.data.objects); before_m=set(bpy.data.meshes); before_mat=set(bpy.data.materials)
with bpy.data.libraries.load(str(root/"blender/salvador_lacerda_r30b41_perfil_misericordia.blend"),link=False) as (available,requested):
    requested.objects=[ground.name]
old=requested.objects[0]
assert old and old.type=="MESH"
assert len(old.data.vertices)==len(ground.data.vertices)
M=wm(ground); Minv=M.inverted()

lpts=[wm(ladeira)@Vector(p.co[:3]) for sp in ladeira.data.splines for p in sp.points]
def dist_to_ladeira(p2):
    best=1e30
    for a,b in zip(lpts,lpts[1:]):
        d=(b-a).to_2d(); L2=d.length_squared
        if L2<1e-12: continue
        t=max(0.0,min(1.0,(p2-a.to_2d()).dot(d)/L2))
        q=a.to_2d()+d*t
        best=min(best,(p2-q).length)
    return best

def smoothstep(x):
    x=max(0.0,min(1.0,x))
    return x*x*(3.0-2.0*x)

core=1.9; outer=2.5
restored=blended=0; max_restore=0.0; max_xy_error=0.0
for i,(cur,base) in enumerate(zip(ground.data.vertices,old.data.vertices)):
    w=M@cur.co; bw=M@base.co
    original_xy=(w.x,w.y)
    dz=w.z-bw.z
    if abs(dz)<1e-5: continue
    d=dist_to_ladeira(w.to_2d())
    if d<=core:
        max_restore=max(max_restore,abs(dz)); w.z=bw.z; restored+=1
    elif d<outer:
        t=smoothstep((d-core)/(outer-core))
        target=bw.z*(1.0-t)+w.z*t
        max_restore=max(max_restore,abs(w.z-target)); w.z=target; blended+=1
    else:
        continue
    cur.co=Minv@w
    chk=M@cur.co
    max_xy_error=max(max_xy_error,math.hypot(chk.x-original_xy[0],chk.y-original_xy[1]))
ground.data.update()
assert restored==68 and blended==28,(restored,blended)
assert max_xy_error<1e-6

# Limpa baseline importado antes de construir BVH.
for ob in list(set(bpy.data.objects)-before_o):
    if ob!=ground and ob!=proxy and ob!=miser and ob!=ladeira:
        bpy.data.objects.remove(ob,do_unlink=True)
for me in list(set(bpy.data.meshes)-before_m):
    if me.users==0:bpy.data.meshes.remove(me)
for mat in list(set(bpy.data.materials)-before_mat):
    if mat.users==0:bpy.data.materials.remove(mat)

# BVH do pavimento já corrigido.
ground.data.calc_loop_triangles(); gtris=list(ground.data.loop_triangles)
gtree=BVHTree.FromPolygons([M@v.co for v in ground.data.vertices],[list(t.vertices) for t in gtris],all_triangles=True)
road_slots={i for i,m in enumerate(ground.data.materials) if m and m.name in contract["export"]["road_materials"]}
def ground_hit(x,y,z):
    p,n,idx,_=gtree.ray_cast(Vector((x,y,z+4.0)),Vector((0,0,-1)),8.0)
    if p is None or n.z<=.70 or gtris[idx].material_index not in road_slots:return None
    return p

# Re-drape somente o helper da Misericórdia, preservando XY e clearance documentado.
b41=json.loads((root/"docs/reports/blender/misericordia_profile_r30b41.json").read_text(encoding="utf8"))
clear=float(b41["clearance_m"])
flat=[p for sp in miser.data.splines for p in sp.points]
miser_inv=wm(miser).inverted(); helper_changed=0; helper_xy_error=0.0
for p in flat:
    w=wm(miser)@Vector(p.co[:3]); xy=(w.x,w.y)
    h=ground_hit(w.x,w.y,w.z)
    if h is None: continue
    nz=h.z+clear
    if abs(nz-w.z)>1e-6:
        w.z=nz; q=miser_inv@w; p.co=(*q,1.0); helper_changed+=1
        chk=wm(miser)@Vector(p.co[:3]); helper_xy_error=max(helper_xy_error,math.hypot(chk.x-xy[0],chk.y-xy[1]))
assert helper_xy_error<1e-5
miser["boas_junction_preservation"]="B42 Ladeira core 1.9m, smooth blend to 2.5m; XY unchanged"

# Reprojeta em Z o proxy apenas no corredor da junção; não muda topologia.
pinv=wm(proxy).inverted(); proxy_changed=0; max_proxy_move=0.0
for v in proxy.data.vertices:
    w=wm(proxy)@v.co
    d=dist_to_ladeira(w.to_2d())
    if d>outer+.25: continue
    # Limita à vizinhança da junção com Misericórdia para não tocar toda a Ladeira.
    node=Vector((98.71444229967892,44.6737222073134))
    if (w.to_2d()-node).length>8.0: continue
    h=ground_hit(w.x,w.y,w.z)
    if h is None: continue
    move=abs(h.z-w.z)
    if move<1e-5: continue
    w.z=h.z; v.co=pinv@w; proxy_changed+=1; max_proxy_move=max(max_proxy_move,move)
proxy.data.update()

# Sanidade topológica: não criar degenerações.
proxy.data.calc_loop_triangles()
xyz=np.array([list(v.co) for v in proxy.data.vertices],dtype=np.float64)
tri=np.array([list(t.vertices) for t in proxy.data.loop_triangles],dtype=np.int32)
areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
assert np.isfinite(xyz).all() and int(np.sum(areas<1e-10))==0

# Proteção global fora dos três componentes autorizados.
changed_protected=[n for n,sig in protected.items() if n not in scene.objects or signature(scene.objects[n])!=sig]
assert not changed_protected,changed_protected

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
evidence={
    "method":"restore B41 Z inside authored Ladeira junction core and smoothstep blend to B42 outside; XY/materials/topology preserved",
    "core_m":core,"outer_m":outer,"restored_ground_vertices":restored,"blended_ground_vertices":blended,
    "maximum_ground_restore_m":max_restore,"maximum_ground_xy_error_m":max_xy_error,
    "helper_points_redraped":helper_changed,"maximum_helper_xy_error_m":helper_xy_error,
    "proxy_vertices_reprojected":proxy_changed,"maximum_proxy_move_m":max_proxy_move,
    "degenerate_triangles_lt_1e10":int(np.sum(areas<1e-10)),
    "protected_changes":changed_protected
}
report["source_after"]["sha256"]=sha
report["junction_blend"]=evidence
report["pending"]=["Reabrir e repetir auditoria integral de 743 segmentos","Crossfall/envelope/física continuam gates separados","Largura real não verificada"]
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
reg=json.loads(registry_path.read_text(encoding="utf8")); assert reg["authoring_source"]["revision"]=="R30B.41"
reg["validation_source"]["sha256"]=sha
for row in reg["revisions"]:
    if row.get("revision")=="R30B.42":row["sha256"]=sha
registry_path.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"sha256":sha,**evidence},ensure_ascii=False))
