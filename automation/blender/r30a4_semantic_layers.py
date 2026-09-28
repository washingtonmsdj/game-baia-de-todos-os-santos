from __future__ import annotations

import json
import unicodedata
from collections import Counter
from pathlib import Path

import bpy

REVISION = "R30A.4"
ROOT_NAME = "32 GAMEPLAY | SEMANTIC LAYERS R30A4"
LAYER_NAMES = {
    "terrain": "32.1 GAMEPLAY | TERRAIN",
    "collision": "32.2 GAMEPLAY | COLLISION SOURCE",
    "road": "32.3 GAMEPLAY | ROAD DRIVEABLE",
    "walkable": "32.4 GAMEPLAY | WALKABLE",
    "crossing": "32.5 GAMEPLAY | PEDESTRIAN CROSSINGS",
    "curb": "32.6 GAMEPLAY | CURB BOUNDARIES",
    "water": "32.7 GAMEPLAY | WATER",
    "georef": "32.8 REFERENCE | GEOREF",
    "legacy": "32.9 REFERENCE | LEGACY TERRAIN PROXIES",
}


def norm(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def ensure_collection(name: str, parent: bpy.types.Collection) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    if collection.name not in {child.name for child in parent.children}:
        parent.children.link(collection)
    collection["ordax_revision"] = REVISION
    collection["ordax_semantic_only"] = True
    return collection


def link_once(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    if obj.name not in collection.objects:
        collection.objects.link(obj)


def set_role(obj: bpy.types.Object, role: str, layer: str, note: str = "") -> None:
    obj["ordax_semantic_revision"] = REVISION
    obj["game_role"] = role
    obj["ordax_semantic_layer"] = layer
    if note:
        obj["ordax_semantic_note"] = note


def mesh_totals() -> dict[str, int]:
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.data]
    return {
        "mesh_objects": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "edges": sum(len(obj.data.edges) for obj in meshes),
        "polygons": sum(len(obj.data.polygons) for obj in meshes),
    }


scene = bpy.context.scene
before_objects = len(bpy.data.objects)
before_meshes = len(bpy.data.meshes)
before_geometry = mesh_totals()
selected_before = [obj.name for obj in bpy.context.selected_objects]
active_before = bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None

root = bpy.data.collections.get(ROOT_NAME)
if root is None:
    root = bpy.data.collections.new(ROOT_NAME)
if root.name not in {child.name for child in scene.collection.children}:
    scene.collection.children.link(root)
root["ordax_revision"] = REVISION
root["ordax_semantic_only"] = True
root["ordax_non_destructive"] = True

layers = {key: ensure_collection(name, root) for key, name in LAYER_NAMES.items()}
for collection in layers.values():
    for existing in list(collection.objects):
        collection.objects.unlink(existing)
assigned: dict[str, set[str]] = {key: set() for key in layers}


def assign(obj: bpy.types.Object, key: str, role: str, note: str = "") -> None:
    link_once(obj, layers[key])
    set_role(obj, role, layers[key].name, note)
    assigned[key].add(obj.name)


for obj in bpy.data.objects:
    if obj.type not in {"MESH", "CURVE"}:
        continue
    name = norm(obj.name)
    collections = [norm(col.name) for col in obj.users_collection]
    materials = [norm(slot.material.name) for slot in obj.material_slots if slot.material]
    material_text = " ".join(materials)

    is_composite_terrain = name.startswith("mvp | terreno corrigido | colis")
    if is_composite_terrain:
        assign(obj, "terrain", "gameplay_terrain_composite", "Legacy composite: terrain plus surface roles.")
        assign(obj, "collision", "collision_source", "Collision source; geometry split intentionally deferred.")
        obj["ordax_semantic_status"] = "composite_legacy_not_geometry_split"
        continue

    if "colis" in name or "collision" in name:
        assign(obj, "collision", "collision_source")

    in_19 = any(col.startswith("19 mvp | terreno dem") for col in collections)
    in_21 = any(col.startswith("21 mvp | ruas e calcadas") for col in collections)
    in_24 = any(col.startswith("24 orla |") for col in collections)
    in_25 = any(col.startswith("25 vias |") for col in collections)

    if (in_19 or in_21) and ("pista" in name or "asfalto" in material_text):
        assign(obj, "road", "road_driveable")
    if (in_19 or in_21) and any(term in name for term in ("calcada", "caminho", "escadaria")):
        assign(obj, "walkable", "walkable_surface")
    elif (in_19 or in_21) and "percurso pedonal" in material_text:
        assign(obj, "walkable", "walkable_surface")

    if in_25 and "guia" in name:
        assign(obj, "curb", "curb_boundary")
    elif in_25 and "travessia" in name:
        assign(obj, "crossing", "pedestrian_crossing")

    if in_24 and ("baia" in name or "agua" in material_text or "superficie" in name):
        assign(obj, "water", "water_surface")

    if any(col.startswith("source_georef |") for col in collections):
        assign(obj, "georef", "reference_georef", "Reference-only; not gameplay geometry.")

    if any(col.startswith("03 terreno |") for col in collections) and name.startswith("terreno |"):
        assign(obj, "legacy", "legacy_terrain_proxy", "Hidden historical proxy; not gameplay terrain.")

    if name.startswith("inferior r21 | passeio da entrada") or name.startswith("inferior r21 | rebaixo acessivel"):
        assign(obj, "walkable", "walkable_surface", "Lower Elevador access corridor.")

role_names = {
    "terrain": "GAMEPLAY_TERRAIN",
    "collision": "COLLISION_SOURCE",
    "road": "ROAD_DRIVEABLE",
    "walkable": "WALKABLE_SURFACE",
    "crossing": "PEDESTRIAN_CROSSING",
    "curb": "CURB_BOUNDARY",
    "water": "WATER_SURFACE",
    "georef": "REFERENCE_GEOREF",
    "legacy": "LEGACY_TERRAIN_PROXY",
}

reverse_roles: dict[str, list[str]] = {}
for key, names in assigned.items():
    for obj_name in names:
        reverse_roles.setdefault(obj_name, []).append(role_names[key])

for obj_name, roles in reverse_roles.items():
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        continue
    obj["ordax_semantic_roles"] = json.dumps(sorted(roles))
    if len(roles) > 1:
        obj["game_role"] = "composite:" + "+".join(sorted(roles)).lower()

scene["ordax_semantic_revision"] = REVISION
scene["ordax_semantic_root"] = ROOT_NAME
scene["ordax_semantic_policy"] = "non_destructive_collection_links_and_metadata"

after_geometry = mesh_totals()
report = {
    "schema": "bay-of-all-saints/r30a4-semantic-layers-v1",
    "revision": REVISION,
    "blend_file": bpy.data.filepath,
    "scene": scene.name,
    "before": {
        "objects": before_objects,
        "meshes": before_meshes,
        "geometry": before_geometry,
        "selected": selected_before,
        "active": active_before,
    },
    "after": {
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        "geometry": after_geometry,
        "selected": [obj.name for obj in bpy.context.selected_objects],
        "active": bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
    },
    "geometry_unchanged": before_geometry == after_geometry,
    "object_count_unchanged": before_objects == len(bpy.data.objects),
    "mesh_datablock_count_unchanged": before_meshes == len(bpy.data.meshes),
    "semantic_root": ROOT_NAME,
    "layers": {
        key: {
            "collection": layers[key].name,
            "count": len(names),
            "objects": sorted(names),
        }
        for key, names in assigned.items()
    },
    "multi_role_objects": {
        name: sorted(roles) for name, roles in reverse_roles.items() if len(roles) > 1
    },
}

project_root = Path(bpy.data.filepath).resolve().parent.parent
output = project_root / "docs" / "reports" / "blender" / "r30a4" / "semantic_layers.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"output": str(output), "geometry_unchanged": report["geometry_unchanged"], "layer_counts": {k: v["count"] for k, v in report["layers"].items()}}, ensure_ascii=False))
