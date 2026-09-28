#!/usr/bin/env python3
"""Cruza vias estruturais OSM com um DEM para detectar anomalias de perfil.

É uma ferramenta de QA: flags de inclinação/salto nunca corrigem terreno ou via automaticamente.
Requer rasterio em runtime para leitura/amostragem do GeoTIFF.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

DEFAULT_LAYERS = {"roads", "pedestrian"}
SUPPORTED_STRUCTURE_SCHEMAS = {
    "bay-of-all-saints/osm-structure-v1",
    "bay-of-all-saints/osm-structure-v2",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def densify(points: list[list[float]], spacing_m: float, max_samples: int = 5000) -> list[tuple[float, float]]:
    if len(points) < 2:
        return []
    result: list[tuple[float, float]] = [(float(points[0][0]), float(points[0][1]))]
    for raw_a, raw_b in zip(points, points[1:]):
        a = (float(raw_a[0]), float(raw_a[1]))
        b = (float(raw_b[0]), float(raw_b[1]))
        seg = distance(a, b)
        if seg <= 1e-9:
            continue
        steps = max(1, int(math.ceil(seg / spacing_m)))
        for index in range(1, steps + 1):
            t = index / steps
            result.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            if len(result) >= max_samples:
                return result
    return result


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    fraction = pos - lo
    return ordered[lo] * (1.0 - fraction) + ordered[hi] * fraction


def analyze_profile(
    points: list[tuple[float, float]],
    elevations: list[float | None],
    grade_review: float,
    jump_review_m: float,
) -> dict:
    if len(points) != len(elevations):
        raise ValueError("points/elevations precisam ter o mesmo tamanho")

    valid_z = [float(z) for z in elevations if z is not None and math.isfinite(float(z))]
    grades: list[float] = []
    jumps: list[float] = []
    flagged_segments = []

    for index in range(len(points) - 1):
        za, zb = elevations[index], elevations[index + 1]
        if za is None or zb is None:
            continue
        za, zb = float(za), float(zb)
        if not (math.isfinite(za) and math.isfinite(zb)):
            continue
        horizontal = distance(points[index], points[index + 1])
        if horizontal <= 1e-9:
            continue
        dz = zb - za
        grade = abs(dz) / horizontal
        jump = abs(dz)
        grades.append(grade)
        jumps.append(jump)
        reasons = []
        if grade > grade_review:
            reasons.append("grade_review")
        if jump > jump_review_m:
            reasons.append("jump_review")
        if reasons:
            flagged_segments.append({
                "segment_index": index,
                "from_xy": [points[index][0], points[index][1]],
                "to_xy": [points[index + 1][0], points[index + 1][1]],
                "from_z": za,
                "to_z": zb,
                "horizontal_m_projected": horizontal,
                "delta_z_m": dz,
                "abs_grade": grade,
                "reasons": reasons,
            })

    nodata_count = len(elevations) - len(valid_z)
    flags = []
    if nodata_count:
        flags.append("nodata")
    if any("grade_review" in segment["reasons"] for segment in flagged_segments):
        flags.append("grade_review")
    if any("jump_review" in segment["reasons"] for segment in flagged_segments):
        flags.append("jump_review")

    return {
        "sample_count": len(points),
        "valid_sample_count": len(valid_z),
        "nodata_sample_count": nodata_count,
        "z_min_m": min(valid_z) if valid_z else None,
        "z_max_m": max(valid_z) if valid_z else None,
        "z_range_m": (max(valid_z) - min(valid_z)) if valid_z else None,
        "max_abs_grade": max(grades) if grades else None,
        "p95_abs_grade": percentile(grades, 0.95),
        "max_abs_jump_m": max(jumps) if jumps else None,
        "flags": flags,
        "flagged_segments": flagged_segments,
    }


def sample_elevations(dataset, points: list[tuple[float, float]]) -> list[float | None]:
    values = []
    for sample in dataset.sample(points, indexes=1, masked=True):
        value = sample[0]
        if getattr(value, "mask", False):
            values.append(None)
        else:
            numeric = float(value)
            nodata = dataset.nodata
            if nodata is not None and math.isclose(numeric, float(nodata), rel_tol=0.0, abs_tol=1e-8):
                values.append(None)
            elif not math.isfinite(numeric):
                values.append(None)
            else:
                values.append(numeric)
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita saltos/inclinações do DEM ao longo de vias OSM.")
    parser.add_argument("--dem", type=Path, required=True)
    parser.add_argument("--structure", type=Path, required=True, help="osm_structure.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--spacing-m", type=float, default=5.0)
    parser.add_argument("--grade-review", type=float, default=0.35, help="grade absoluta para revisão (0.35 = 35%%)")
    parser.add_argument("--jump-review-m", type=float, default=4.0)
    parser.add_argument("--include-steps", action="store_true")
    parser.add_argument("--max-samples-per-feature", type=int, default=5000)
    args = parser.parse_args()

    if args.spacing_m <= 0:
        raise SystemExit("--spacing-m deve ser > 0")
    if args.grade_review <= 0 or args.jump_review_m <= 0:
        raise SystemExit("thresholds de revisão devem ser > 0")

    try:
        import rasterio  # type: ignore
    except ImportError as exc:
        raise SystemExit("audit_road_profiles.py requer `rasterio` para amostrar o DEM.") from exc

    structure = load_json(args.structure)
    if structure.get("schema") not in SUPPORTED_STRUCTURE_SCHEMAS:
        raise SystemExit("--structure possui schema estrutural não suportado")

    layers = set(DEFAULT_LAYERS)
    if args.include_steps:
        layers.add("steps")

    results = []
    total_samples = 0
    with rasterio.open(args.dem) as dataset:
        epsg = dataset.crs.to_epsg() if dataset.crs else None
        crs_text = str(dataset.crs) if dataset.crs else None
        if epsg != 3857 and "3857" not in (crs_text or ""):
            raise SystemExit(f"DEM precisa estar em EPSG:3857 para cruzar osm_structure diretamente; encontrado: {crs_text}")

        for feature in structure.get("features", []):
            if feature.get("layer") not in layers:
                continue
            coords = feature.get("epsg3857") or []
            points = densify(coords, args.spacing_m, args.max_samples_per_feature)
            if len(points) < 2:
                continue
            elevations = sample_elevations(dataset, points)
            analysis = analyze_profile(points, elevations, args.grade_review, args.jump_review_m)
            total_samples += analysis["sample_count"]
            tags = feature.get("tags") or {}
            results.append({
                "osm_type": feature.get("osm_type"),
                "osm_id": feature.get("osm_id"),
                "layer": feature.get("layer"),
                "name": tags.get("name"),
                "highway": tags.get("highway"),
                "analysis": analysis,
            })

        dem_meta = {
            "path": str(args.dem.resolve()),
            "crs": crs_text,
            "width": dataset.width,
            "height": dataset.height,
            "nodata": dataset.nodata,
            "bounds": [dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top],
            "pixel_size": [abs(dataset.transform.a), abs(dataset.transform.e)],
        }

    flagged = [item for item in results if item["analysis"]["flags"]]
    flagged.sort(key=lambda item: (
        -(item["analysis"]["max_abs_grade"] or 0.0),
        -(item["analysis"]["max_abs_jump_m"] or 0.0),
    ))
    payload = {
        "schema": "bay-of-all-saints/dem-road-profile-audit-v1",
        "dem": dem_meta,
        "structure_source": str(args.structure.resolve()),
        "thresholds": {
            "spacing_m_projected": args.spacing_m,
            "grade_review": args.grade_review,
            "jump_review_m": args.jump_review_m,
            "layers": sorted(layers),
        },
        "summary": {
            "features_analyzed": len(results),
            "features_flagged_for_review": len(flagged),
            "total_samples": total_samples,
            "nodata_features": sum(1 for item in results if "nodata" in item["analysis"]["flags"]),
        },
        "features": results,
        "review_queue": [
            {
                "osm_id": item["osm_id"],
                "layer": item["layer"],
                "name": item["name"],
                "highway": item["highway"],
                "flags": item["analysis"]["flags"],
                "max_abs_grade": item["analysis"]["max_abs_grade"],
                "max_abs_jump_m": item["analysis"]["max_abs_jump_m"],
                "nodata_sample_count": item["analysis"]["nodata_sample_count"],
                "flagged_segments": item["analysis"]["flagged_segments"],
            }
            for item in flagged
        ],
        "notes": [
            "Thresholds são heurísticas de QA configuráveis, não limites legais/engenharia nem prova de erro.",
            "Trechos íngremes podem ser reais em Salvador; cada flag precisa de revisão espacial.",
            "O relatório nunca move vias nem altera o DEM.",
            "Distâncias horizontais são em EPSG:3857 projetado e servem para detecção relativa de anomalias.",
        ],
    }
    write_json(args.output, payload)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
