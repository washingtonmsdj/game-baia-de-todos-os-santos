#!/usr/bin/env python3
"""Compara cobertura espacial do DEM auditado com a estrutura OSM extraída.

Entrada:
- dem_audit.json (v1 ou v2)
- osm_structure.json (v1 ou v2)

Saída:
- dem_osm_coverage.json com margens, interseção e classificação de cobertura.

Não modifica o DEM, OSM ou Blender.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SUPPORTED_DEM_SCHEMAS = {
    "bay-of-all-saints/dem-audit-v1",
    "bay-of-all-saints/dem-audit-v2",
}
SUPPORTED_STRUCTURE_SCHEMAS = {
    "bay-of-all-saints/osm-structure-v1",
    "bay-of-all-saints/osm-structure-v2",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_dem_bounds(audit: dict) -> dict:
    meta = audit.get("metadata") or {}
    bounds = meta.get("bounds") or {}
    required = ("left", "bottom", "right", "top")
    if any(bounds.get(key) is None for key in required):
        raise ValueError("dem_audit não contém bounds completos")
    return {
        "min_x": float(bounds["left"]),
        "min_y": float(bounds["bottom"]),
        "max_x": float(bounds["right"]),
        "max_y": float(bounds["top"]),
    }


def normalize_osm_bounds(structure: dict) -> dict:
    bounds = structure.get("bounds_epsg3857") or {}
    required = ("min_x", "min_y", "max_x", "max_y")
    if any(bounds.get(key) is None for key in required):
        raise ValueError("osm_structure não contém bounds_epsg3857 completos")
    return {key: float(bounds[key]) for key in required}


def area(bounds: dict) -> float:
    return max(0.0, bounds["max_x"] - bounds["min_x"]) * max(0.0, bounds["max_y"] - bounds["min_y"])


def intersection(a: dict, b: dict) -> dict | None:
    result = {
        "min_x": max(a["min_x"], b["min_x"]),
        "min_y": max(a["min_y"], b["min_y"]),
        "max_x": min(a["max_x"], b["max_x"]),
        "max_y": min(a["max_y"], b["max_y"]),
    }
    if result["min_x"] >= result["max_x"] or result["min_y"] >= result["max_y"]:
        return None
    return result


def margins(container: dict, target: dict) -> dict:
    return {
        "west_m_projected": target["min_x"] - container["min_x"],
        "south_m_projected": target["min_y"] - container["min_y"],
        "east_m_projected": container["max_x"] - target["max_x"],
        "north_m_projected": container["max_y"] - target["max_y"],
    }


def classify(dem: dict, osm: dict, min_margin: float) -> tuple[str, list[str]]:
    notes: list[str] = []
    m = margins(dem, osm)
    contained = all(value >= 0 for value in m.values())
    if not contained:
        notes.append("Parte da estrutura OSM está fora dos bounds do DEM.")
        return "insufficient", notes
    if all(value >= min_margin for value in m.values()):
        notes.append("A estrutura OSM está integralmente coberta pelo DEM com margem mínima em todas as bordas.")
        return "covered_with_margin", notes
    notes.append("A estrutura OSM está dentro do DEM, mas próxima de pelo menos uma borda do raster.")
    return "covered_edge_sensitive", notes


def compare(dem_audit: dict, structure: dict, min_margin: float) -> dict:
    dem_schema = dem_audit.get("schema")
    structure_schema = structure.get("schema")
    if dem_schema not in SUPPORTED_DEM_SCHEMAS:
        raise ValueError(f"schema DEM não suportado: {dem_schema}")
    if structure_schema not in SUPPORTED_STRUCTURE_SCHEMAS:
        raise ValueError(f"schema OSM não suportado: {structure_schema}")

    dem = normalize_dem_bounds(dem_audit)
    osm = normalize_osm_bounds(structure)
    overlap = intersection(dem, osm)
    dem_area = area(dem)
    osm_area = area(osm)
    overlap_area = area(overlap) if overlap else 0.0
    coverage_ratio = overlap_area / osm_area if osm_area > 0 else 0.0
    status, notes = classify(dem, osm, min_margin)

    pixel = (dem_audit.get("metadata") or {}).get("pixel_size") or {}
    max_pixel = max(float(pixel.get("x") or 0), float(pixel.get("y") or 0))
    edge_margin_pixels = None
    m = margins(dem, osm)
    if max_pixel > 0:
        edge_margin_pixels = {key.replace("_m_projected", "_pixels_approx"): value / max_pixel for key, value in m.items()}

    warnings = []
    if coverage_ratio < 1.0 - 1e-9:
        warnings.append(f"Cobertura OSM pelo DEM é {coverage_ratio:.6f}, inferior a 100%.")
    if any(value < 0 for value in m.values()):
        warnings.append("Há pelo menos uma borda OSM fora do DEM; não extrapolar altitude automaticamente.")
    if status == "covered_edge_sensitive":
        warnings.append("O recorte está perto da borda de tile/raster; revisar artefatos antes de confiar em perfis próximos às extremidades.")

    return {
        "schema": "bay-of-all-saints/dem-osm-coverage-v1",
        "status": status,
        "thresholds": {"minimum_margin_m_projected": min_margin},
        "dem_bounds_epsg3857": dem,
        "osm_bounds_epsg3857": osm,
        "intersection_epsg3857": overlap,
        "margins": m,
        "margins_in_pixels_approx": edge_margin_pixels,
        "areas_projected": {
            "dem_m2": dem_area,
            "osm_bbox_m2": osm_area,
            "intersection_m2": overlap_area,
            "osm_bbox_coverage_ratio": coverage_ratio,
        },
        "pixel_size": pixel,
        "warnings": warnings,
        "notes": notes + [
            "A comparação usa bounds em EPSG:3857; ela detecta cobertura/recorte, não qualidade vertical do DEM.",
            "Margem negativa indica falta de cobertura, não autorização para extrapolar ou esticar o raster.",
            "Margem em pixels é aproximada e usa o maior pixel size reportado no audit do DEM.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara bounds/cobertura de dem_audit.json e osm_structure.json.")
    parser.add_argument("--dem-audit", type=Path, required=True)
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-margin-m", type=float, default=20.0)
    args = parser.parse_args()
    if args.minimum_margin_m < 0:
        raise SystemExit("--minimum-margin-m não pode ser negativo")
    payload = compare(load_json(args.dem_audit), load_json(args.structure), args.minimum_margin_m)
    write_json(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "coverage_ratio": payload["areas_projected"]["osm_bbox_coverage_ratio"],
        "margins": payload["margins"],
        "warnings": payload["warnings"],
    }, ensure_ascii=False, indent=2))
    return 2 if payload["status"] == "insufficient" else 0


if __name__ == "__main__":
    raise SystemExit(main())
