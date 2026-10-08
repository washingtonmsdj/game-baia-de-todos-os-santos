"""Sondagem de duas malhas no mesmo XY, somente leitura no Blender visível.

Sem interseção real com piso e terreno não existe delta de superfície válido.
"""
import bpy
import hashlib
import json
import os
import sys
from pathlib import Path
from mathutils import Matrix, Vector

root = next(p for p in Path(bpy.data.filepath).parents
            if (p / "world/areas/mvp-centro-lacerda/blender-revisions.json").exists())
sys.path.insert(0, str(root))
from tools.terrain.surface_registration import evaluate_samples

catalog = json.loads((root / "world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf-8"))
authoring = catalog["authoring_source"]
source = (root / authoring["file"]).resolve()
if Path(bpy.data.filepath).resolve() != source:
    raise RuntimeError("A cena aberta não é a fonte explícita do catálogo")
if bpy.data.is_dirty:
    raise RuntimeError("A cena tem alterações não salvas; não declarar resultados reproduzíveis")
with source.open("rb") as stream:
    sha = hashlib.file_digest(stream, "sha256").hexdigest()
if sha != authoring["sha256"]:
    raise RuntimeError("O SHA-256 da fonte Blender difere do ponteiro de autoria")

scene = bpy.data.scenes.get("SALVADOR | ESBOCO OFICIAL")
if scene is None:
    raise RuntimeError("Cena estrutural histórica ausente")
terrain = scene.objects.get("MVP | terreno corrigido | colisão estática")
floor = scene.objects.get("INFERIOR | piso do saguão")
if terrain is None or floor is None or terrain.type != "MESH" or floor.type != "MESH":
    raise RuntimeError("Objetos explícitos da interface estrutural ausentes")

evidence_path = root / "docs/reports/blender/lacerda-lower-structure-b93/application.json"
frame_path = root / "docs/reports/blender/lacerda-corridor/scene_b78.json"
evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
frame = Matrix(json.loads(frame_path.read_text(encoding="utf-8"))["measurement_frame"])
floor_reference_z = max((floor.matrix_world @ Vector(corner)).z for corner in floor.bound_box)


def sample_surface(object_, x, y):
    inverse = object_.matrix_world.inverted()
    origin = inverse @ Vector((x, y, 200))
    direction = (inverse.to_3x3() @ Vector((0, 0, -1))).normalized()
    hit, location, normal, index = object_.ray_cast(origin, direction, distance=500)
    return ((object_.matrix_world @ location).z if hit else None,
            index if hit else None)


samples = []
for sample in evidence["terrain_samples_before"]:
    if sample.get("control_group") != "lower_floor":
        continue
    xy = sample["local_xy"]
    point = frame @ Vector((xy[0], xy[1], 0))
    floor_z, floor_polygon = sample_surface(floor, point.x, point.y)
    terrain_z, terrain_polygon = sample_surface(terrain, point.x, point.y)
    samples.append({
        "world_xy": [point.x, point.y],
        "floor_world_z": floor_z,
        "terrain_world_z": terrain_z,
        "terrain_world_z_baseline": sample.get("terrain_world_z"),
        "floor_polygon": floor_polygon,
        "terrain_polygon": terrain_polygon,
        "control_group": sample["control_group"],
    })

result = evaluate_samples(samples, floor_reference_z)
result.update({
    "source_file": authoring["file"],
    "source_sha256": sha,
    "scene": scene.name,
    "pid": os.getpid(),
    "reference": evidence_path.relative_to(root).as_posix(),
    "frame_source": frame_path.relative_to(root).as_posix(),
    "terrain_object": terrain.name,
    "floor_object": floor.name,
    "source_dirty": bpy.data.is_dirty,
    "method": "B93 XY transformed by B78 frame; independent downward rays on floor and terrain meshes at identical XY",
    "absolute_placement_approved": False,
    "market_connector_approved": False,
})
print(json.dumps(result, ensure_ascii=False))
