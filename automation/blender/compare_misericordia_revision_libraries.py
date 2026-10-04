"""Compara, sem abrir outra janela, a superfície da Misericórdia entre revisões salvas."""
import bpy, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
current = Path(bpy.data.filepath).resolve()
assert current.name == "salvador_lacerda_r30b40_fluxos_e_colisao.blend"
audit = json.loads((root/"docs/reports/blender/rondesp_network_current.json").read_text(encoding="utf8"))
seg = next(x for x in audit["segments"] if x["edge_id"]=="way-803899198-seg-1")
targets = [0.0408163265,0.1020408163,0.25,0.5,0.75]
samples = [min(seg["samples"], key=lambda x:abs(x["fraction"]-f)) for f in targets]
files = [
 "salvador_lacerda_r30b30_conexao_real_recorte.blend",
 "salvador_lacerda_r30b34_palacio_galerias.blend",
 "salvador_lacerda_r30b38_binding_conceicao.blend",
 "salvador_lacerda_r30b39_rondesp_percursos.blend",
]
names = ["MVP | terreno corrigido | colisão estática","R30A5 | COLLISION | terrain proxy"]

def bvh(ob):
    me=ob.data; me.calc_loop_triangles()
    verts=[ob.matrix_world@v.co for v in me.vertices]
    tris=[list(t.vertices) for t in me.loop_triangles]
    return BVHTree.FromPolygons(verts,tris,all_triangles=True)

def cast(tree,q):
    p,n,i,d=tree.ray_cast(Vector((q.x,q.y,q.z+8)),Vector((0,0,-1)),16)
    return None if p is None else round(float(p.z),6)

results=[]
for fn in files:
    before_o=set(bpy.data.objects); before_m=set(bpy.data.meshes); before_mat=set(bpy.data.materials)
    path=root/"blender"/fn
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):
        dst.objects=[n for n in names if n in src.objects]
    loaded={ob.name.split(".")[0]:ob for ob in dst.objects if ob is not None}
    row={"file":fn,"objects":[ob.name for ob in dst.objects if ob]}
    for desired in names:
        ob=next((o for o in dst.objects if o and (o.name==desired or o.name.startswith(desired+"."))),None)
        if ob is None:
            row[desired]=None; continue
        tree=bvh(ob)
        row[desired]=[{"fraction":s["fraction"],"z":cast(tree,Vector(s["point"]))} for s in samples]
    results.append(row)
    for ob in list(set(bpy.data.objects)-before_o):
        bpy.data.objects.remove(ob,do_unlink=True)
    for me in list(set(bpy.data.meshes)-before_m):
        if me.users==0:bpy.data.meshes.remove(me)
    for mat in list(set(bpy.data.materials)-before_mat):
        if mat.users==0:bpy.data.materials.remove(mat)

# Current B40 is already loaded; no appended data needed.
row={"file":current.name}
for desired in names:
    ob=bpy.context.scene.objects.get(desired)
    tree=bvh(ob) if ob else None
    row[desired]=None if tree is None else [{"fraction":s["fraction"],"z":cast(tree,Vector(s["point"]))} for s in samples]
results.append(row)
out=root/"artifacts/roads/rondesp/misericordia_revision_compare.json"
out.write_text(json.dumps({"geometry_changed":False,"saved":False,"results":results},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(results,ensure_ascii=False))
