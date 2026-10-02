"""Inspeção read-only dos volumes do Elevador Lacerda na janela visível."""
import bpy, json
from pathlib import Path
from mathutils import Matrix, Vector

root = Path(__file__).resolve().parents[2]
rot = Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z, 4, 'Z').inverted()
terms = ('PASSARELA', 'GALERIA', 'TORRE', 'CASCA', 'SUPERIOR', 'LAC R30B07', 'LAC R30B03', 'FACHADA INFERIOR')
items = []
for ob in bpy.data.objects:
    if ob.type != 'MESH' or not any(t in ob.name.upper() for t in terms):
        continue
    points = [rot @ ob.matrix_world @ Vector(corner) for corner in ob.bound_box]
    bounds = [[round(min(v[i] for v in points), 3), round(max(v[i] for v in points), 3)] for i in range(3)]
    items.append({'name': ob.name, 'bounds_local': bounds, 'hidden': ob.hide_get() or ob.hide_render})
dest = root / 'artifacts/lacerda/r30b08_inspection.json'
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf8')
from mathutils.bvhtree import BVHTree
terrain = bpy.data.objects['MVP | terreno corrigido | colisão estática']
deps = bpy.context.evaluated_depsgraph_get()
tree = BVHTree.FromObject(terrain, deps)
samples = []
for x in (-25, -20, -16, -14, -12, -10, -8, -5):
    for y in (-2, 1, 4, 7, 10):
        world_origin = Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z, 4, 'Z') @ Vector((x, y, 100))
        local_origin = terrain.matrix_world.inverted() @ world_origin
        local_dir = (terrain.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized()
        hit, normal, face, distance = tree.ray_cast(local_origin, local_dir, 150)
        if hit is not None:
            world_hit = terrain.matrix_world @ hit
            mat = terrain.data.materials[terrain.data.polygons[face].material_index]
            samples.append({'x': x, 'y': y, 'z': round(world_hit.z, 3), 'material': mat.name if mat else None})
(root / 'artifacts/lacerda/r30b08_ground_samples.json').write_text(json.dumps(samples, indent=2), encoding='utf8')
print(json.dumps({'objects': len(items), 'path': str(dest)}, ensure_ascii=False))
