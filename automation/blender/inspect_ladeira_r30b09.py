"""Amostra read-only de terreno e material em torno da Ladeira da Montanha."""
import bpy, json
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
terrain = bpy.data.objects['MVP | terreno corrigido | colisão estática']
rotation = Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z, 4, 'Z')
tree = BVHTree.FromObject(terrain, bpy.context.evaluated_depsgraph_get())
samples = []
for x in range(-70, -5, 5):
    for y in range(-30, 41, 5):
        origin = rotation @ Vector((x, y, 100))
        local_origin = terrain.matrix_world.inverted() @ origin
        direction = (terrain.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized()
        hit, normal, face, distance = tree.ray_cast(local_origin, direction, 150)
        if hit is None:
            continue
        mat = terrain.data.materials[terrain.data.polygons[face].material_index]
        z = (terrain.matrix_world @ hit).z
        samples.append({'x': x, 'y': y, 'z': round(z, 2), 'material': mat.name if mat else ''})
(root / 'artifacts/lacerda/r30b09_ladeira_surface_grid.json').write_text(json.dumps(samples, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({'samples': len(samples)}))
