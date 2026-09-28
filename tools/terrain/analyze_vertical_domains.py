#!/usr/bin/env python3
"""Diagnostica fit vertical separando terreno terrestre de batimetria.

Este script NÃO altera DEM nem Blender. Ele usa as mesmas amostras do fit vertical,
separa valores DEM abaixo de 0 m (batimetria/abaixo do nível médio do mar) dos
valores não negativos e produz uma grade espacial de resíduos para triagem.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import fit_dem_blender_vertical as vertical  # noqa: E402

SUPPORTED_SAMPLE_SCHEMAS = {"bay-of-all-saints/blender-terrain-samples-v1"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def split_domains(records: list[dict], sea_level_m: float = 0.0) -> tuple[list[dict], list[dict]]:
    below = []
    nonnegative = []
    for row in records:
        if float(row["dem_z_m"]) < sea_level_m:
            below.append(row)
        else:
            nonnegative.append(row)
    return below, nonnegative


def summarize_values(records: list[dict]) -> dict:
    if not records:
        return {"sample_count": 0, "dem_min_m": None, "dem_max_m": None, "dem_median_m": None}
    values = [float(row["dem_z_m"]) for row in records]
    return {
        "sample_count": len(values),
        "dem_min_m": min(values),
        "dem_max_m": max(values),
        "dem_median_m": statistics.median(values),
    }


def fit_records(
    records: list[dict],
    horizontal_scale: float | None,
    min_points: int,
    residual_floor: float,
    mad_multiplier: float,
) -> dict:
    if len(records) < min_points:
        return {
            "quality": "insufficient",
            "reason": f"amostras insuficientes: {len(records)} < {min_points}",
            "summary": {"input": len(records), "kept": 0, "removed": 0},
            "fit": None,
            "kept_records": [],
        }
    fit, kept, removed = vertical.robust_vertical_fit(
        records,
        min_points=min_points,
        residual_floor=residual_floor,
        mad_multiplier=mad_multiplier,
    )
    result_quality = vertical.quality(fit, len(kept), horizontal_scale)
    return {
        "quality": result_quality,
        "reason": None,
        "summary": {"input": len(records), "kept": len(kept), "removed": len(removed)},
        "fit": fit,
        "kept_records": kept,
    }


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def spatial_grid(
    records: list[dict],
    fit: dict,
    grid_size_m: float,
    review_median_abs_residual: float,
    min_cell_samples: int,
) -> tuple[list[dict], list[dict]]:
    if not records or not fit:
        return [], []
    slope = float(fit["scale_z_blender_units_per_dem_meter"])
    intercept = float(fit["z_offset_blender_units"])
    cells: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in records:
        x, y = [float(v) for v in row["epsg3857_xy"]]
        residual = float(row["blender_z"]) - (slope * float(row["dem_z_m"]) + intercept)
        ix = math.floor(x / grid_size_m)
        iy = math.floor(y / grid_size_m)
        cells[(ix, iy)].append({**row, "residual": residual})

    output = []
    review = []
    for (ix, iy), rows in sorted(cells.items()):
        residuals = [float(row["residual"]) for row in rows]
        abs_residuals = [abs(value) for value in residuals]
        dem_values = [float(row["dem_z_m"]) for row in rows]
        blender_values = [float(row["blender_z"]) for row in rows]
        cell = {
            "grid_index": [ix, iy],
            "bounds_epsg3857": {
                "min_x": ix * grid_size_m,
                "min_y": iy * grid_size_m,
                "max_x": (ix + 1) * grid_size_m,
                "max_y": (iy + 1) * grid_size_m,
            },
            "sample_count": len(rows),
            "dem_min_m": min(dem_values),
            "dem_max_m": max(dem_values),
            "dem_median_m": statistics.median(dem_values),
            "blender_z_median": statistics.median(blender_values),
            "residual_median": statistics.median(residuals),
            "residual_median_abs": statistics.median(abs_residuals),
            "residual_p90_abs": percentile(abs_residuals, 0.90),
            "residual_max_abs": max(abs_residuals),
        }
        output.append(cell)
        if len(rows) >= min_cell_samples and cell["residual_median_abs"] >= review_median_abs_residual:
            review.append(cell)

    review.sort(key=lambda item: (-float(item["residual_median_abs"]), -int(item["sample_count"])))
    return output, review


def flatten_samples(samples: dict, robust_xy: dict) -> list[dict]:
    flattened = []
    for obj in samples.get("objects", []):
        for point in obj.get("points_world", []):
            if len(point) < 3:
                continue
            epsg_xy = vertical.inverse_xy((float(point[0]), float(point[1])), robust_xy)
            flattened.append({
                "object_name": obj.get("object_name"),
                "blender_xyz": [float(point[0]), float(point[1]), float(point[2])],
                "epsg3857_xy": [epsg_xy[0], epsg_xy[1]],
                "blender_z": float(point[2]),
            })
    return flattened


def main() -> int:
    parser = argparse.ArgumentParser(description="Separa terra/batimetria e mapeia resíduos do fit vertical DEM ↔ Blender.")
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True, help="georef_fit.json")
    parser.add_argument("--dem", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sea-level-m", type=float, default=0.0)
    parser.add_argument("--grid-size-m", type=float, default=50.0)
    parser.add_argument("--min-points", type=int, default=50)
    parser.add_argument("--residual-floor", type=float, default=0.75)
    parser.add_argument("--mad-multiplier", type=float, default=4.0)
    parser.add_argument("--review-median-abs-residual", type=float, default=5.0)
    parser.add_argument("--min-cell-samples", type=int, default=8)
    args = parser.parse_args()

    if args.grid_size_m <= 0:
        raise SystemExit("--grid-size-m precisa ser > 0")
    if args.min_cell_samples < 1:
        raise SystemExit("--min-cell-samples precisa ser >= 1")

    try:
        import rasterio  # type: ignore
    except ImportError as exc:
        raise SystemExit("analyze_vertical_domains.py requer rasterio.") from exc

    samples = load_json(args.samples)
    fit_report = load_json(args.fit)
    if samples.get("schema") not in SUPPORTED_SAMPLE_SCHEMAS:
        raise SystemExit(f"schema de samples não suportado: {samples.get('schema')}")
    robust_xy = fit_report.get("robust_fit")
    if not robust_xy:
        raise SystemExit("georef_fit.json não contém robust_fit")
    if fit_report.get("quality") not in {"candidate", "strong_candidate"}:
        raise SystemExit("fit XY precisa ser candidate/strong_candidate")

    flattened = flatten_samples(samples, robust_xy)
    with rasterio.open(args.dem) as dataset:
        epsg = dataset.crs.to_epsg() if dataset.crs else None
        if epsg != 3857 and "3857" not in str(dataset.crs or ""):
            raise SystemExit(f"DEM precisa estar em EPSG:3857; encontrado {dataset.crs}")
        values = vertical.sample_dem(dataset, [(r["epsg3857_xy"][0], r["epsg3857_xy"][1]) for r in flattened])

    valid = []
    invalid = 0
    for row, dem_z in zip(flattened, values):
        if dem_z is None:
            invalid += 1
            continue
        valid.append({**row, "dem_z_m": float(dem_z)})

    bathymetry, land = split_domains(valid, args.sea_level_m)
    horizontal_scale = robust_xy.get("scale_blender_units_per_meter")
    horizontal_scale = float(horizontal_scale) if horizontal_scale is not None else None

    all_fit = fit_records(valid, horizontal_scale, args.min_points, args.residual_floor, args.mad_multiplier)
    land_fit = fit_records(land, horizontal_scale, args.min_points, args.residual_floor, args.mad_multiplier)

    cells, review = spatial_grid(
        land_fit.get("kept_records") or [],
        land_fit.get("fit") or {},
        args.grid_size_m,
        args.review_median_abs_residual,
        args.min_cell_samples,
    )

    def public_fit(result: dict) -> dict:
        return {
            "quality": result["quality"],
            "reason": result["reason"],
            "summary": result["summary"],
            "fit": result["fit"],
        }

    payload = {
        "schema": "bay-of-all-saints/dem-vertical-domains-v1",
        "status": "diagnostic_only",
        "inputs": {
            "samples": str(args.samples),
            "georef_fit": str(args.fit),
            "dem": str(args.dem),
        },
        "thresholds": {
            "sea_level_m": args.sea_level_m,
            "grid_size_m": args.grid_size_m,
            "review_median_abs_residual": args.review_median_abs_residual,
            "min_cell_samples": args.min_cell_samples,
        },
        "sample_summary": {
            "input_blender_samples": len(flattened),
            "valid_dem_samples": len(valid),
            "invalid_dem_samples": invalid,
            "below_sea_level": summarize_values(bathymetry),
            "nonnegative_land_candidate": summarize_values(land),
        },
        "fits": {
            "all_valid": public_fit(all_fit),
            "nonnegative_land_candidate": public_fit(land_fit),
        },
        "land_spatial_grid": {
            "cells": cells,
            "review_cells": review,
            "review_cell_count": len(review),
        },
        "notes": [
            "DEM < sea_level_m é separado do fit terrestre; os dados não são apagados nem reclassificados como nodata.",
            "Mapzen/Tilezen usa ETOPO1 para batimetria oceânica; valores negativos na Baía podem ser válidos.",
            "DEM >= sea_level_m é apenas domínio candidato de terra para QA vertical, não máscara cartográfica definitiva.",
            "A grade de resíduos serve para localizar discrepâncias; nenhum valor é aplicado automaticamente à cena.",
            "Qualquer correção deve ser regional e rastreável depois de revisar as células com maiores resíduos.",
        ],
    }
    write_json(args.output, payload)
    print(json.dumps({
        "valid_dem_samples": len(valid),
        "below_sea_level_samples": len(bathymetry),
        "land_candidate_samples": len(land),
        "all_quality": all_fit["quality"],
        "land_quality": land_fit["quality"],
        "review_cells": len(review),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
