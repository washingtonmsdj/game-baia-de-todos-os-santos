#!/usr/bin/env python3
"""Estima a relação vertical DEM(m) -> Blender Z a partir da mesh de terreno.

Requer:
- terrain_samples.json exportado pelo Blender;
- georef_fit.json para inverter XY Blender -> EPSG:3857;
- terrain.tif/DEM em EPSG:3857.

Somente auditoria: não altera DEM nem Blender.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inverse_xy(blender_xy: tuple[float, float], fit: dict) -> tuple[float, float]:
    scale = float(fit["scale_blender_units_per_meter"])
    if scale <= 0:
        raise ValueError("scale_blender_units_per_meter precisa ser > 0")
    theta = math.radians(float(fit["rotation_epsg3857_to_blender_deg"]))
    tx, ty = [float(value) for value in fit["translation_blender"]]
    bx = float(blender_xy[0]) - tx
    by = float(blender_xy[1]) - ty
    c, s = math.cos(theta), math.sin(theta)
    # p = R^-1 * ((b - t) / scale)
    px = (c * bx + s * by) / scale
    py = (-s * bx + c * by) / scale
    return px, py


def fit_line(pairs: list[tuple[float, float]]) -> dict:
    if len(pairs) < 2:
        raise ValueError("são necessários pelo menos 2 pares DEM/Blender")
    xs = [float(pair[0]) for pair in pairs]
    ys = [float(pair[1]) for pair in pairs]
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    den = sum((x - mean_x) ** 2 for x in xs)
    if den <= 1e-12:
        raise ValueError("elevações DEM sem variação suficiente para estimar escala vertical")
    slope = sum((x - mean_x) * (y - mean_y) for x, y in pairs) / den
    intercept = mean_y - slope * mean_x
    residuals = [y - (slope * x + intercept) for x, y in pairs]
    rms = math.sqrt(statistics.fmean(value * value for value in residuals))
    return {
        "scale_z_blender_units_per_dem_meter": slope,
        "dem_meters_per_blender_z_unit": (1.0 / slope) if abs(slope) > 1e-12 else None,
        "z_offset_blender_units": intercept,
        "rms_residual_blender_units": rms,
        "median_abs_residual_blender_units": statistics.median(abs(value) for value in residuals),
        "max_abs_residual_blender_units": max(abs(value) for value in residuals),
        "residuals": residuals,
    }


def robust_vertical_fit(
    records: list[dict],
    min_points: int = 30,
    residual_floor: float = 0.75,
    mad_multiplier: float = 4.0,
    max_iterations: int = 8,
) -> tuple[dict, list[dict], list[dict]]:
    if len(records) < max(2, min_points):
        raise ValueError(f"amostras insuficientes: {len(records)} < {min_points}")
    current = list(records)
    removed: list[dict] = []

    for _ in range(max_iterations):
        fit = fit_line([(row["dem_z_m"], row["blender_z"]) for row in current])
        residuals = fit["residuals"]
        abs_residuals = [abs(value) for value in residuals]
        median_abs = statistics.median(abs_residuals)
        deviations = [abs(value - median_abs) for value in abs_residuals]
        mad = statistics.median(deviations) if deviations else 0.0
        robust_sigma = 1.4826 * mad
        cutoff = max(residual_floor, mad_multiplier * robust_sigma)
        outlier_indices = [index for index, value in enumerate(abs_residuals) if value > cutoff]
        if not outlier_indices:
            fit.pop("residuals", None)
            fit["robust_cutoff_blender_units"] = cutoff
            fit["robust_mad_blender_units"] = mad
            return fit, current, removed

        keep_count = len(current) - len(outlier_indices)
        if keep_count < min_points:
            ranked = sorted(range(len(current)), key=lambda index: abs_residuals[index])
            keep_indices = set(ranked[:min_points])
            outlier_indices = [index for index in range(len(current)) if index not in keep_indices]

        outlier_set = set(outlier_indices)
        next_rows = []
        for index, row in enumerate(current):
            enriched = dict(row)
            enriched["residual_blender_units"] = residuals[index]
            if index in outlier_set:
                removed.append(enriched)
            else:
                next_rows.append(row)
        if len(next_rows) == len(current):
            break
        current = next_rows
        if len(current) < min_points:
            break

    fit = fit_line([(row["dem_z_m"], row["blender_z"]) for row in current])
    fit.pop("residuals", None)
    fit["robust_cutoff_blender_units"] = residual_floor
    fit["robust_mad_blender_units"] = None
    return fit, current, removed


def quality(fit: dict, kept_count: int, horizontal_scale: float | None) -> str:
    slope = fit["scale_z_blender_units_per_dem_meter"]
    rms = fit["rms_residual_blender_units"]
    if slope <= 0:
        return "insufficient"
    scale_ratio = slope / horizontal_scale if horizontal_scale and horizontal_scale > 0 else None
    if kept_count >= 200 and rms <= 0.75 and (scale_ratio is None or 0.75 <= scale_ratio <= 1.25):
        return "strong_candidate"
    if kept_count >= 50 and rms <= 2.0 and (scale_ratio is None or 0.5 <= scale_ratio <= 1.5):
        return "candidate"
    return "insufficient"


def sample_dem(dataset, xy: list[tuple[float, float]]) -> list[float | None]:
    output = []
    for sample in dataset.sample(xy, indexes=1, masked=True):
        value = sample[0]
        if getattr(value, "mask", False):
            output.append(None)
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            output.append(None)
            continue
        if dataset.nodata is not None and math.isclose(numeric, float(dataset.nodata), rel_tol=0.0, abs_tol=1e-8):
            output.append(None)
            continue
        output.append(numeric)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Estima escala/offset vertical entre DEM e Blender Z.")
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True, help="georef_fit.json")
    parser.add_argument("--dem", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-points", type=int, default=50)
    parser.add_argument("--residual-floor", type=float, default=0.75)
    parser.add_argument("--mad-multiplier", type=float, default=4.0)
    parser.add_argument("--top-outliers", type=int, default=200)
    args = parser.parse_args()

    try:
        import rasterio  # type: ignore
    except ImportError as exc:
        raise SystemExit("fit_dem_blender_vertical.py requer `rasterio` para amostrar o DEM.") from exc

    samples = load_json(args.samples)
    fit_report = load_json(args.fit)
    if samples.get("schema") != "bay-of-all-saints/blender-terrain-samples-v1":
        raise SystemExit("arquivo --samples inválido")
    robust_xy = fit_report.get("robust_fit")
    if not robust_xy:
        raise SystemExit("georef_fit.json não contém robust_fit")
    if fit_report.get("quality") not in {"candidate", "strong_candidate"}:
        raise SystemExit("fit XY precisa ser candidate/strong_candidate antes do fit vertical")

    flattened = []
    for obj in samples.get("objects", []):
        for point in obj.get("points_world", []):
            if len(point) < 3:
                continue
            epsg_xy = inverse_xy((float(point[0]), float(point[1])), robust_xy)
            flattened.append({
                "object_name": obj.get("object_name"),
                "blender_xyz": [float(point[0]), float(point[1]), float(point[2])],
                "epsg3857_xy": [epsg_xy[0], epsg_xy[1]],
                "blender_z": float(point[2]),
            })
    if len(flattened) < args.min_points:
        raise SystemExit(f"amostras de terreno insuficientes antes do DEM: {len(flattened)}")

    with rasterio.open(args.dem) as dataset:
        epsg = dataset.crs.to_epsg() if dataset.crs else None
        crs_text = str(dataset.crs) if dataset.crs else None
        if epsg != 3857 and "3857" not in (crs_text or ""):
            raise SystemExit(f"DEM precisa estar em EPSG:3857; encontrado: {crs_text}")
        dem_values = sample_dem(dataset, [(row["epsg3857_xy"][0], row["epsg3857_xy"][1]) for row in flattened])

    records = []
    nodata_count = 0
    for row, dem_z in zip(flattened, dem_values):
        if dem_z is None:
            nodata_count += 1
            continue
        records.append({**row, "dem_z_m": float(dem_z)})

    if len(records) < args.min_points:
        raise SystemExit(f"amostras DEM válidas insuficientes: {len(records)} < {args.min_points}")

    robust, kept, removed = robust_vertical_fit(
        records,
        min_points=args.min_points,
        residual_floor=args.residual_floor,
        mad_multiplier=args.mad_multiplier,
    )
    horizontal_scale = robust_xy.get("scale_blender_units_per_meter")
    horizontal_scale = float(horizontal_scale) if horizontal_scale is not None else None
    scale_ratio = (
        robust["scale_z_blender_units_per_dem_meter"] / horizontal_scale
        if horizontal_scale and horizontal_scale > 0 else None
    )
    result_quality = quality(robust, len(kept), horizontal_scale)

    object_residuals: dict[str, list[float]] = defaultdict(list)
    slope = robust["scale_z_blender_units_per_dem_meter"]
    intercept = robust["z_offset_blender_units"]
    kept_enriched = []
    for row in kept:
        residual = row["blender_z"] - (slope * row["dem_z_m"] + intercept)
        object_residuals[row["object_name"] or "<unknown>"].append(residual)
        kept_enriched.append({**row, "residual_blender_units": residual})

    per_object = []
    for name, values in object_residuals.items():
        per_object.append({
            "object_name": name,
            "sample_count": len(values),
            "median_residual_blender_units": statistics.median(values),
            "median_abs_residual_blender_units": statistics.median(abs(value) for value in values),
            "max_abs_residual_blender_units": max(abs(value) for value in values),
        })
    per_object.sort(key=lambda item: -item["max_abs_residual_blender_units"])

    all_outliers = removed + sorted(
        kept_enriched,
        key=lambda row: -abs(row["residual_blender_units"]),
    )[: max(0, args.top_outliers)]
    all_outliers.sort(key=lambda row: -abs(row.get("residual_blender_units", 0.0)))

    payload = {
        "schema": "bay-of-all-saints/dem-blender-vertical-fit-v1",
        "status": "candidate_only",
        "quality": result_quality,
        "inputs": {
            "samples": str(args.samples.resolve()),
            "georef_fit": str(args.fit.resolve()),
            "dem": str(args.dem.resolve()),
        },
        "horizontal_fit_quality": fit_report.get("quality"),
        "horizontal_scale_blender_units_per_meter": horizontal_scale,
        "vertical_fit": robust,
        "scale_ratio_vertical_to_horizontal": scale_ratio,
        "summary": {
            "input_blender_samples": len(flattened),
            "valid_dem_samples": len(records),
            "nodata_or_invalid_samples": nodata_count,
            "kept_samples": len(kept),
            "removed_outliers": len(removed),
            "objects_with_samples": len(object_residuals),
        },
        "per_object_residuals": per_object,
        "largest_residual_samples": all_outliers[: args.top_outliers],
        "notes": [
            "Resultado é candidato e nunca altera DEM ou Blender.",
            "Escala vertical próxima à escala horizontal sugere unidades uniformes, mas não prova precisão topográfica.",
            "Outliers podem representar correções locais legítimas, artefatos do DEM ou objetos classificados indevidamente como terreno.",
            "Revisar objetos/resíduos espacialmente antes de qualquer correção de Z.",
        ],
    }
    write_json(args.output, payload)
    print(json.dumps({"quality": result_quality, **payload["summary"], **robust, "scale_ratio_vertical_to_horizontal": scale_ratio}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
