#!/usr/bin/env python3
"""Compara objetos Blender com OSM ID contra a referência estrutural transformada.

Entrada:
- structural_scene_audit.json (v2)
- structural_reference.json

Saída: offsets/escala de bounds para triagem. Não move nenhum objeto.
Além do agregado histórico por OSM ID, calcula candidatos por objeto para impedir
que um binding semântico errado contamine silenciosamente toda a entidade.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


SUPPORTED_REFERENCE_SCHEMAS = {
    "bay-of-all-saints/blender-structure-reference-v1",
    "bay-of-all-saints/blender-structure-reference-v2",
}

REFERENCE_LAYER_EXPECTED_SCENE_CATEGORIES = {
    "buildings": {"buildings"},
    "roads": {"roads"},
    "pedestrian": {"sidewalks", "roads"},
    "steps": {"steps"},
    "retaining_walls": {"retaining"},
    "earthworks": {"terrain", "retaining"},
    "cliffs": {"terrain", "retaining"},
    "waterfront": {"waterfront"},
    "coastline": {"waterfront", "water"},
    "water": {"water"},
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bounds_from_xy(points: list[list[float]]) -> dict | None:
    if not points:
        return None
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    return {
        "min": [min(xs), min(ys)],
        "max": [max(xs), max(ys)],
        "center": [(min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0],
        "size": [max(xs) - min(xs), max(ys) - min(ys)],
    }


def bounds2d_from_scene(bounds: dict | None) -> dict | None:
    if not bounds:
        return None
    minimum = bounds.get("min") or []
    maximum = bounds.get("max") or []
    if len(minimum) < 2 or len(maximum) < 2:
        return None
    return {
        "min": [float(minimum[0]), float(minimum[1])],
        "max": [float(maximum[0]), float(maximum[1])],
        "center": [(float(minimum[0]) + float(maximum[0])) / 2.0, (float(minimum[1]) + float(maximum[1])) / 2.0],
        "size": [float(maximum[0]) - float(minimum[0]), float(maximum[1]) - float(minimum[1])],
    }


def union_bounds(bounds_list: list[dict]) -> dict | None:
    if not bounds_list:
        return None
    minimum = [min(item["min"][axis] for item in bounds_list) for axis in (0, 1)]
    maximum = [max(item["max"][axis] for item in bounds_list) for axis in (0, 1)]
    return {
        "min": minimum,
        "max": maximum,
        "center": [(minimum[0] + maximum[0]) / 2.0, (minimum[1] + maximum[1]) / 2.0],
        "size": [maximum[0] - minimum[0], maximum[1] - minimum[1]],
    }


def distance(a: list[float], b: list[float]) -> float:
    return math.hypot(float(b[0]) - float(a[0]), float(b[1]) - float(a[1]))


def relative_size_delta(scene_size: list[float], reference_size: list[float]) -> list[float | None]:
    result = []
    for actual, expected in zip(scene_size, reference_size):
        if abs(expected) <= 1e-9:
            result.append(None)
        else:
            result.append((actual - expected) / expected)
    return result


def aggregate_scene_by_osm(scene: dict) -> dict[int, dict]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for obj in scene.get("objects", []):
        if not obj.get("osm_ids"):
            continue
        for osm_id in obj["osm_ids"]:
            grouped[int(osm_id)].append(obj)

    result = {}
    for osm_id, objects in grouped.items():
        bounds = [bounds2d_from_scene(obj.get("bounds")) for obj in objects]
        bounds = [item for item in bounds if item]
        result[osm_id] = {
            "objects": objects,
            "bounds": union_bounds(bounds),
            "categories": sorted({category for obj in objects for category in obj.get("categories", [])}),
        }
    return result


def aggregate_reference_by_osm(reference: dict) -> dict[int, dict]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for feature in reference.get("features", []):
        grouped[int(feature["osm_id"])].append(feature)
    result = {}
    for osm_id, features in grouped.items():
        bounds = [bounds_from_xy(feature.get("blender_xy") or []) for feature in features]
        bounds = [item for item in bounds if item]
        result[osm_id] = {
            "features": features,
            "bounds": union_bounds(bounds),
            "layers": sorted({feature.get("layer") for feature in features if feature.get("layer")}),
        }
    return result


def compare(scene_group: dict, ref_group: dict, meters_per_unit: float | None, offset_review_m: float, size_review_ratio: float) -> dict | None:
    scene_bounds = scene_group.get("bounds")
    ref_bounds = ref_group.get("bounds")
    if not scene_bounds or not ref_bounds:
        return None

    offset_units = distance(scene_bounds["center"], ref_bounds["center"])
    offset_m = offset_units * meters_per_unit if meters_per_unit is not None else None
    size_delta = relative_size_delta(scene_bounds["size"], ref_bounds["size"])
    max_size_ratio = max((abs(value) for value in size_delta if value is not None), default=None)

    flags = []
    if offset_m is not None and offset_m > offset_review_m:
        flags.append("center_offset_review")
    elif offset_m is None and offset_units > offset_review_m:
        flags.append("center_offset_units_review")
    if max_size_ratio is not None and max_size_ratio > size_review_ratio:
        flags.append("bounds_size_review")

    return {
        "scene_center_xy": scene_bounds["center"],
        "reference_center_xy": ref_bounds["center"],
        "center_offset_blender_units": offset_units,
        "center_offset_m": offset_m,
        "scene_bounds_xy": scene_bounds,
        "reference_bounds_xy": ref_bounds,
        "bounds_relative_size_delta": size_delta,
        "max_abs_bounds_size_delta_ratio": max_size_ratio,
        "flags": flags,
    }


def expected_categories(reference_layers: list[str]) -> set[str]:
    expected: set[str] = set()
    for layer in reference_layers:
        expected.update(REFERENCE_LAYER_EXPECTED_SCENE_CATEGORIES.get(layer, set()))
    return expected


def compare_individual_objects(scene_group: dict, ref_group: dict, meters_per_unit: float | None, offset_review_m: float, size_review_ratio: float) -> list[dict]:
    expected = expected_categories(ref_group.get("layers") or [])
    rows = []
    for obj in scene_group.get("objects", []):
        bounds = bounds2d_from_scene(obj.get("bounds"))
        if not bounds:
            continue
        result = compare({"bounds": bounds}, ref_group, meters_per_unit, offset_review_m, size_review_ratio)
        if result is None:
            continue
        categories = set(obj.get("categories") or [])
        semantic_match = bool(expected & categories) if expected else None
        rows.append({
            "object_name": obj.get("name"),
            "scene_categories": sorted(categories),
            "expected_scene_categories": sorted(expected),
            "semantic_match": semantic_match,
            **result,
        })

    def score(item):
        semantic_penalty = 0 if item.get("semantic_match") is True else (1 if item.get("semantic_match") is None else 2)
        offset = item.get("center_offset_m")
        if offset is None:
            offset = item.get("center_offset_blender_units") or 0.0
        size = item.get("max_abs_bounds_size_delta_ratio")
        return (semantic_penalty, float(offset), float(size or 0.0), item.get("object_name") or "")

    rows.sort(key=score)
    return rows


def binding_conflict(aggregate_result: dict, object_candidates: list[dict], offset_review_m: float) -> tuple[bool, list[str]]:
    reasons = []
    if len(object_candidates) <= 1:
        return False, reasons

    semantic_values = [item.get("semantic_match") for item in object_candidates]
    if True in semantic_values and False in semantic_values:
        reasons.append("mesmo OSM ID aparece em objetos semanticamente compatíveis e incompatíveis com a camada de referência")

    best = object_candidates[0]
    aggregate_offset = aggregate_result.get("center_offset_m")
    best_offset = best.get("center_offset_m")
    if aggregate_offset is not None and best_offset is not None and aggregate_offset > offset_review_m and best_offset <= offset_review_m:
        reasons.append("agregado falha no offset enquanto um objeto candidato isolado fica dentro do limite")

    offsets = [item.get("center_offset_m") for item in object_candidates if item.get("center_offset_m") is not None]
    if len(offsets) >= 2 and max(offsets) - min(offsets) > max(10.0, offset_review_m * 3.0):
        reasons.append("objetos com o mesmo OSM ID têm offsets individuais fortemente divergentes")

    return bool(reasons), reasons


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara OSM IDs presentes na cena Blender com a referência estrutural.")
    parser.add_argument("--scene-audit", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offset-review-m", type=float, default=3.0)
    parser.add_argument("--size-review-ratio", type=float, default=0.25)
    args = parser.parse_args()

    scene = load_json(args.scene_audit)
    reference = load_json(args.reference)
    if scene.get("schema") != "bay-of-all-saints/blender-structural-scene-audit-v2":
        raise SystemExit("scene audit precisa ser v2; execute novamente audit_structural_scene.py")
    if reference.get("schema") not in SUPPORTED_REFERENCE_SCHEMAS:
        raise SystemExit("schema de structural reference não suportado")

    meters_per_unit = (reference.get("fit_summary") or {}).get("meters_per_blender_unit")
    if meters_per_unit is not None:
        meters_per_unit = float(meters_per_unit)
        if meters_per_unit <= 0:
            raise SystemExit("meters_per_blender_unit inválido")

    scene_by_id = aggregate_scene_by_osm(scene)
    ref_by_id = aggregate_reference_by_osm(reference)
    shared = sorted(set(scene_by_id) & set(ref_by_id))
    comparisons = []
    skipped = []
    for osm_id in shared:
        scene_group = scene_by_id[osm_id]
        ref_group = ref_by_id[osm_id]
        row = compare(scene_group, ref_group, meters_per_unit, args.offset_review_m, args.size_review_ratio)
        if row is None:
            skipped.append(osm_id)
            continue

        object_candidates = compare_individual_objects(
            scene_group,
            ref_group,
            meters_per_unit,
            args.offset_review_m,
            args.size_review_ratio,
        )
        conflict, conflict_reasons = binding_conflict(row, object_candidates, args.offset_review_m)
        flags = list(row["flags"])
        if conflict:
            flags.append("binding_conflict_review")

        best = object_candidates[0] if object_candidates else None
        comparisons.append({
            "osm_id": osm_id,
            "scene_objects": [obj.get("name") for obj in scene_group["objects"]],
            "scene_categories": scene_group["categories"],
            "reference_layers": ref_group["layers"],
            "expected_scene_categories": sorted(expected_categories(ref_group["layers"])),
            "best_object_candidate": best,
            "object_candidates": object_candidates,
            "binding_conflict_reasons": conflict_reasons,
            **{**row, "flags": flags},
        })

    review_queue = [item for item in comparisons if item["flags"]]
    review_queue.sort(key=lambda item: (
        "binding_conflict_review" not in item["flags"],
        -(item["center_offset_m"] if item["center_offset_m"] is not None else item["center_offset_blender_units"]),
        -(item["max_abs_bounds_size_delta_ratio"] or 0.0),
    ))
    offsets_m = [item["center_offset_m"] for item in comparisons if item["center_offset_m"] is not None]
    best_offsets_m = [
        item["best_object_candidate"]["center_offset_m"]
        for item in comparisons
        if item.get("best_object_candidate") and item["best_object_candidate"].get("center_offset_m") is not None
    ]
    binding_conflicts = [item for item in comparisons if "binding_conflict_review" in item["flags"]]

    payload = {
        "schema": "bay-of-all-saints/scene-reference-alignment-v2",
        "inputs": {"scene_audit": str(args.scene_audit), "reference": str(args.reference)},
        "thresholds": {"offset_review_m": args.offset_review_m, "size_review_ratio": args.size_review_ratio},
        "fit_summary": reference.get("fit_summary", {}),
        "summary": {
            "scene_osm_ids": len(scene_by_id),
            "reference_osm_ids": len(ref_by_id),
            "shared_osm_ids": len(shared),
            "compared_osm_ids": len(comparisons),
            "skipped_without_bounds": len(skipped),
            "review_items": len(review_queue),
            "binding_conflict_items": len(binding_conflicts),
            "median_center_offset_m": statistics.median(offsets_m) if offsets_m else None,
            "max_center_offset_m": max(offsets_m) if offsets_m else None,
            "median_best_object_center_offset_m": statistics.median(best_offsets_m) if best_offsets_m else None,
            "max_best_object_center_offset_m": max(best_offsets_m) if best_offsets_m else None,
        },
        "comparisons": comparisons,
        "review_queue": review_queue,
        "binding_conflicts": binding_conflicts,
        "unmatched": {
            "scene_only_osm_ids": sorted(set(scene_by_id) - set(ref_by_id)),
            "reference_only_count": len(set(ref_by_id) - set(scene_by_id)),
            "skipped_shared_osm_ids": skipped,
        },
        "notes": [
            "Comparação agregada histórica é preservada para detectar bindings que contaminam bounds.",
            "best_object_candidate é triagem: prioriza compatibilidade semântica e menor offset, mas não autoriza mover/excluir objetos automaticamente.",
            "binding_conflict_review sinaliza OSM ID atribuído a objetos incompatíveis ou espacialmente divergentes.",
            "Bounds podem variar por extrusão, rotação e organização do asset; bounds_size_review é triagem, não prova de erro.",
            "Nenhum objeto é movido, desvinculado ou alterado automaticamente.",
        ],
    }
    write_json(args.output, payload)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
