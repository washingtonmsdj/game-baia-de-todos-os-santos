"""Amostra read-only da Rua da Misericórdia em qualquer revisão carregada."""
import bpy, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
audit = json.loads((root / "docs/reports/blender/rondesp_network_current.json").read_text(encoding="utf8"))
seg = next(x for x in audit["segments"] if x["edge_id"] == "way-803899198-seg-1")
ground = bpy.context.scene.objects.get("MVP | terreno corrigido | colisão estática")
proxy = bpy.context.scene.objects.get("R30A5 | COLLISION | terrain proxy")

def make_tree(ob):
    if ob is None:
        return None, None
    me = ob.data
    me.calc_loop_triangles()
    verts = [ob.matrix_world @ v.co for v in me.vertices]
    tris = [list(t.vertices) for t in me.loop_triangles]
    pm = [p.material_index for p in me.polygons]
    tm = [pm[t.polygon_index] for t in me.loop_triangles]
    return BVHTree.FromPolygons(verts, tris, all_triangles=True), tm

def cast(ob, tree, mats, q):
    if ob is None or tree is None:
        return None
    hit, normal, idx, _ = tree.ray_cast(Vector((q.x, q.y, q.z + 8.0)), Vector((0,0,-1)), 16.0)
    if hit is None:
        return None
    mi = mats[idx]
    mat = ob.data.materials[mi].name if mi < len(ob.data.materials) and ob.data.materials[mi] else None
    return {"z": round(float(hit.z), 6), "delta": round(float(hit.z-q.z), 6), "normal_z": round(float(normal.z), 6), "material": mat}

gt, gm = make_tree(ground)
pt, pm = make_tree(proxy)
wanted = [0.0, 0.0408163265, 0.1020408163, 0.25, 0.5, 0.75, 1.0]
rows = []
for target in wanted:
    s = min(seg["samples"], key=lambda x: abs(x["fraction"]-target))
    q = Vector(s["point"])
    rows.append({
        "fraction": s["fraction"],
        "reference_z": round(float(q.z), 6),
        "ground": cast(ground, gt, gm, q),
        "proxy": cast(proxy, pt, pm, q),
    })
print("BOAS_MISERICORDIA_SAMPLE="+json.dumps({
    "file": Path(bpy.data.filepath).name,
    "ground_vertices": len(ground.data.vertices) if ground else None,
    "proxy_vertices": len(proxy.data.vertices) if proxy else None,
    "rows": rows,
}, ensure_ascii=False))
