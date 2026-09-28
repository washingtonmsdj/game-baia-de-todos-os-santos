from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import bpy

SCHEMA = "bay-of-all-saints/r30a3-semantic-audit-v1"
REFERENCE_PREFIX = "SOURCE_GEOREF |"


def folded(*values):
    return " ".join(str(v) for v in values if v is not None).casefold()


def classify(obj):
    collections = [c.name for c in obj.users_collection]
    materials = [slot.material.name for slot in obj.material_slots if slot.material]
    props = {str(k): obj.get(k) for k in obj.keys()}
    text = folded(obj.name, *collections, *materials, *props.keys(), *props.values())
    labels = []
    if any(c.startswith(REFERENCE_PREFIX) for c in collections) or obj.get("boas_reference_only"):
        labels.append("REFERENCE")
    if "game_role" in props and "terrain" in folded(props.get("game_role")):
        labels.append("GAMEPLAY_TERRAIN")
    if "colis" in text or "collision" in text:
        labels.append("COLLISION")
    if any(t in text for t in ("asfalto", "road", "rua ", "vias |")):
        labels.append("ROAD_DRIVEABLE_CANDIDATE")
    if any(t in text for t in ("calÃ§ada", "calcada", "passeio", "pedonal", "travessia")):
        labels.append("SIDEWALK_WALKABLE_CANDIDATE")
    if any(t in text for t in ("elevador lacerda", "mercado modelo", "palacio rio branco", "hero")):
        labels.append("HERO_CANDIDATE")
    if any(t in text for t in ("baÃ­a", "baia", "water", "mar |")):
        labels.append("WATER_CANDIDATE")
    return labels or ["UNCLASSIFIED"]


def object_row(obj):
    mesh = None
    if obj.type == "MESH" and obj.data:
        mesh = {
            "vertices": len(obj.data.vertices),
            "edges": len(obj.data.edges),
            "polygons": len(obj.data.polygons),
        }
    return {
        "name": obj.name,
        "type": obj.type,
        "visible": bool(obj.visible_get()),
        "collections": [c.name for c in obj.users_collection],
        "materials": [slot.material.name for slot in obj.material_slots if slot.material],
        "labels": classify(obj),
        "mesh": mesh,
        "ordax": {str(k): obj.get(k) for k in obj.keys() if str(k).startswith("ordax_") or str(k) in {"game_role", "source", "accuracy", "surface_method"}},
    }


def main():
    rows = [object_row(obj) for obj in bpy.data.objects]
    counts = Counter(label for row in rows for label in row["labels"])
    by_collection = defaultdict(Counter)
    for row in rows:
        for collection in row["collections"]:
            for label in row["labels"]:
                by_collection[collection][label] += 1

    focus = [row for row in rows if any(label != "UNCLASSIFIED" for label in row["labels"])]
    repo_root = Path(bpy.data.filepath).resolve().parent.parent
    output = repo_root / "docs" / "reports" / "blender" / "r30a3" / "semantic_scene_audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": SCHEMA,
        "blend_file": str(Path(bpy.data.filepath).resolve()),
        "scene": bpy.context.scene.name,
        "is_dirty_before": bool(bpy.data.is_dirty),
        "summary": {
            "objects": len(rows),
            "meshes": sum(1 for row in rows if row["type"] == "MESH"),
            "classified_focus_objects": len(focus),
            "label_counts": dict(sorted(counts.items())),
        },
        "collection_label_counts": {k: dict(sorted(v.items())) for k, v in sorted(by_collection.items()) if any(x != "UNCLASSIFIED" for x in v)},
        "objects": sorted(focus, key=lambda row: row["name"].casefold()),
    }
    payload["notes"] = [
        "Auditoria somente leitura; nenhuma geometria, coleÃ§Ã£o ou propriedade Ã© alterada.",
        "Labels *_CANDIDATE sÃ£o triagem e nÃ£o autorizaÃ§Ã£o para gameplay/export.",
        "REFERENCE e GAMEPLAY_TERRAIN/COLLISION devem permanecer responsabilidades distintas.",
    ]
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), **payload["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()

