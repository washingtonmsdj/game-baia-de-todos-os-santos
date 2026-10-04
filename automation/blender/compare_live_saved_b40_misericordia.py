"""Compara terreno B40 vivo com uma cópia byte-a-byte do B40 salvo, sem salvar a sessão."""
import bpy, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2]
assert Path(bpy.data.filepath).name=="salvador_lacerda_r30b40_fluxos_e_colisao.blend"
audit=json.loads((root/"docs/reports/blender/rondesp_network_current.json").read_text(encoding="utf8"))
seg=next(x for x in audit["segments"] if x["edge_id"]=="way-803899198-seg-1")
samples=[min(seg["samples"],key=lambda x:abs(x["fraction"]-f)) for f in (.0408163265,.1020408163,.25,.5,.75)]
name="MVP | terreno corrigido | colisão estática"

def info(ob):
    me=ob.data;me.calc_loop_triangles()
    verts=[ob.matrix_world@v.co for v in me.vertices]
    tris=[list(t.vertices) for t in me.loop_triangles]
    pm=[p.material_index for p in me.polygons];tm=[pm[t.polygon_index] for t in me.loop_triangles]
    tree=BVHTree.FromPolygons(verts,tris,all_triangles=True);rows=[]
    for s in samples:
        q=Vector(s["point"]);p,n,i,_=tree.ray_cast(Vector((q.x,q.y,q.z+8)),Vector((0,0,-1)),16)
        if p is None:rows.append({"fraction":s["fraction"],"hit":None});continue
        mi=tm[i];mat=me.materials[mi].name if mi<len(me.materials) and me.materials[mi] else None
        rows.append({"fraction":s["fraction"],"reference_z":float(q.z),"z":float(p.z),"material":mat,"normal_z":float(n.z)})
    return {"name":ob.name,"parent":ob.parent.name if ob.parent else None,
      "matrix_world":[list(r) for r in ob.matrix_world],"matrix_basis":[list(r) for r in ob.matrix_basis],
      "vertices":len(me.vertices),"faces":len(me.polygons),"rows":rows}

live=bpy.context.scene.objects[name]
before_o=set(bpy.data.objects);before_m=set(bpy.data.meshes);before_mat=set(bpy.data.materials)
copy=root/"artifacts/blender-sessions/b40_saved_probe_copy.blend"
with bpy.data.libraries.load(str(copy),link=False) as (src,dst):
    dst.objects=[name]
saved=dst.objects[0]
report={"live_dirty":bpy.data.is_dirty,"live":info(live),"saved_copy":info(saved),"geometry_changed":False,"saved_session":False}
for ob in list(set(bpy.data.objects)-before_o):bpy.data.objects.remove(ob,do_unlink=True)
for me in list(set(bpy.data.meshes)-before_m):
    if me.users==0:bpy.data.meshes.remove(me)
for mat in list(set(bpy.data.materials)-before_mat):
    if mat.users==0:bpy.data.materials.remove(mat)
out=root/"artifacts/roads/rondesp/b40_live_saved_misericordia.json"
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(report,ensure_ascii=False))
