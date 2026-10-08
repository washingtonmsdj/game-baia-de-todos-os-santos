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
from tools.world.market_access import evaluate_access_candidates, evaluate_direct_approach

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

# Diagnóstico de segmento reto somente para a fachada de Cairu; não gera
# waypoints e não liga o controller histórico a uma entrada especulativa.
cfg = json.loads((source_root / "world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json").read_text(encoding="utf-8"))
entry = next((p for p in portals if p["name"] == "ACESSO | fachada Praça Cairu"), None)
if entry is None:
    raise RuntimeError("Falta o portal de Cairu registrado na cena de autoria")
import math
angle = cfg["local_frame"]["angle"]
local = cfg["lower_route"][-1]
origin = cfg["local_frame"]["origin_xy"]
start = Vector((origin[0] + math.cos(angle)*local[0] - math.sin(angle)*local[1],
                origin[1] + math.sin(angle)*local[0] + math.cos(angle)*local[1], 0))
end = Vector((*entry["center_xy"], 0))
vector = end - start
segment_length = vector.length
if segment_length < 1:
    raise RuntimeError("Segmento B82->Mercado inválido")
terrain_start = sample_z(terrain, start.x, start.y)
if terrain_start is None:
    raise RuntimeError("Ponto de saída B82 sem terreno")
terrain_samples = []
for i in range(16):
    t = i / 15
    xy = start + vector * t
    terrain_samples.append({"t": t, "terrain_z": sample_z(terrain, xy.x, xy.y)})

# Filtro espacial barato antes das interseções exatas. Mesmo uma linha visual
# livre não seria teste de cápsula, navmesh ou autenticação da porta real.
visual_hits = []
for obstacle in scene.objects:
    if obstacle.type != "MESH" or not obstacle.visible_get() or obstacle in (terrain, floor):
        continue
    if not any("PRAÇA CAIRU" in col.name.upper()
               or "MERCADO MODELO" in col.name.upper()
               or "GAMEPLAY" in col.name.upper()
               or "COLLISION" in col.name.upper()
               for col in obstacle.users_collection):
        continue
    corners = [obstacle.matrix_world @ Vector(point) for point in obstacle.bound_box]
    lo = [min(point[d] for point in corners) for d in range(3)]
    hi = [max(point[d] for point in corners) for d in range(3)]
    if hi[2] < terrain_start + .30 or lo[2] > terrain_start + 1.4:
        continue
    if (hi[0] < min(start.x, end.x) - 2 or lo[0] > max(start.x, end.x) + 2
            or hi[1] < min(start.y, end.y) - 2 or lo[1] > max(start.y, end.y) + 2):
        continue
    t = max(0., min(1., ((obstacle.matrix_world.translation - start).dot(vector)
                          / (segment_length * segment_length))))
    nearest = start + vector * t
    closest_x = max(lo[0], min(hi[0], nearest.x))
    closest_y = max(lo[1], min(hi[1], nearest.y))
    if math.hypot(closest_x - nearest.x, closest_y - nearest.y) > 2:
        continue
    inverse = obstacle.matrix_world.inverted()
    for above in (.35, .75, 1.3):
        height = terrain_start + above
        ray_start = Vector((start.x, start.y, height))
        ray_end = Vector((end.x, end.y, height))
        local_start = inverse @ ray_start
        local_vector = inverse @ ray_end - local_start
        hit, point, normal, face = obstacle.ray_cast(
            local_start, local_vector.normalized(), distance=local_vector.length)
        if hit:
            world_hit = obstacle.matrix_world @ point
            visual_hits.append({"name": obstacle.name, "distance_m": (world_hit - ray_start).length,
                                "ray_z": height})

nav_object = scene.objects.get("B81 | NAV | Cairu OSM parcial bloqueada")
nav_bounds = None
if nav_object is not None and nav_object.type == "MESH":
    nav_points = [nav_object.matrix_world @ Vector(point) for point in nav_object.bound_box]
    nav_bounds = [[min(point[d] for point in nav_points),
                   max(point[d] for point in nav_points)] for d in (0, 1)]
report["direct_cairu_approach"] = evaluate_direct_approach(
    cfg, entry["center_xy"], terrain_samples, visual_hits, nav_bounds=nav_bounds)

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
