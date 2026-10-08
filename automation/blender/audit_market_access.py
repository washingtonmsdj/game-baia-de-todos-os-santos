"""Audita aberturas candidatas do Mercado Modelo na janela Blender existente.

Não move objetos, não aprova binding nem conecta navegação ao Mercado.
"""
import bpy
import hashlib
import json
import os
import sys
from pathlib import Path
from mathutils import Vector

source_root = next(p for p in Path(bpy.data.filepath).parents
                   if (p / "world/areas/mvp-centro-lacerda/blender-revisions.json").exists())
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.world.market_access import evaluate_access_candidates

revisions = json.loads((source_root / "world/areas/mvp-centro-lacerda/blender-revisions.json").read_text(encoding="utf-8"))
source = (source_root / revisions["authoring_source"]["file"]).resolve()
if Path(bpy.data.filepath).resolve() != source or bpy.data.is_dirty:
    raise RuntimeError("Fonte de autoria divergente ou alterações não salvas")
with source.open("rb") as file:
    sha = hashlib.file_digest(file, "sha256").hexdigest()
if sha != revisions["authoring_source"]["sha256"]:
    raise RuntimeError("Fonte Blender com hash diferente do SSOT")

locations = json.loads((source_root / "world/areas/mvp-centro-lacerda/locations.json").read_text(encoding="utf-8"))
scene = bpy.data.scenes.get("SALVADOR | ESBOCO OFICIAL")
if scene is None:
    raise RuntimeError("Cena autoral não encontrada")
terrain = scene.objects.get("MVP | terreno corrigido | colisão estática")
floor = scene.objects.get("TÉRREO | laje")
if not all(o and o.type == "MESH" for o in (terrain, floor)):
    raise RuntimeError("Piso ou terreno explícito do Mercado não encontrado")


def sample_z(obj, x, y):
    inverse = obj.matrix_world.inverted()
    start = inverse @ Vector((x, y, 150))
    down = (inverse.to_3x3() @ Vector((0, 0, -1))).normalized()
    hit, point, normal, polygon = obj.ray_cast(start, down, distance=350)
    return (obj.matrix_world @ point).z if hit else None


portals = []
for obj in scene.objects:
    if not (obj.name.startswith("ACESSO | fachada ")
            and obj.name.endswith(" | ombreira E")):
        continue
    if not any("MERCADO MODELO" in c.name.upper() and "LEGACY" not in c.name.upper()
               for c in obj.users_collection):
        continue
    prefix = obj.name.removesuffix(" | ombreira E")
    other = scene.objects.get(prefix + " | ombreira D")
    lintel = scene.objects.get(prefix + " | verga")
    if not other or not lintel or any(o.type != "MESH" for o in (obj, other, lintel)):
        raise RuntimeError("Abertura com ombreira/verga incompleta: " + prefix)

    midpoint = (obj.matrix_world.translation + other.matrix_world.translation) / 2
    tangent = (other.matrix_world.translation - obj.matrix_world.translation).normalized()
    normal = Vector((-tangent.y, tangent.x, 0))
    projected_e = [((obj.matrix_world @ Vector(v)) - midpoint).dot(tangent)
                   for v in obj.bound_box]
    projected_d = [((other.matrix_world @ Vector(v)) - midpoint).dot(tangent)
                   for v in other.bound_box]
    gap = min(projected_d) - max(projected_e)
    low = max(min((o.matrix_world @ Vector(c)).z for c in o.bound_box)
              for o in (obj, other))
    high = min((lintel.matrix_world @ Vector(c)).z for c in lintel.bound_box)
    samples = []
    for offset in (-3, -1, 0, 1, 3):
        xy = midpoint + normal * offset
        samples.append({
            "offset_m": offset,
            "terrain_z": sample_z(terrain, xy.x, xy.y),
            "floor_z": sample_z(floor, xy.x, xy.y),
        })
    portals.append({
        "name": prefix,
        "visible": all(o.visible_get() for o in (obj, other, lintel)),
        "center_xy": [midpoint.x, midpoint.y],
        "clear_gap_m": gap,
        "headroom_m": high - low,
        "reference_status": obj.get("status_fidelidade", ""),
        "samples": samples,
    })

report = evaluate_access_candidates(locations, "mercado-modelo", portals)
report.update({
    "source_file": revisions["authoring_source"]["file"],
    "source_sha256": sha,
    "pid": os.getpid(),
    "scene": scene.name,
    "dirty": bpy.data.is_dirty,
    "terrain_object": terrain.name,
    "floor_object": floor.name,
    "measurement": "Ombreiras/vergas visíveis e raios piso/terreno, sem teste de colisão e navegação",
    "route_certified": False,
    "objects_modified": 0,
})
print(json.dumps(report, ensure_ascii=False))
