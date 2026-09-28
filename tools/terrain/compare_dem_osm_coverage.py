#!/usr/bin/env python3
"""Compara cobertura espacial do DEM com a janela estrutural relevante.

Por padrão mantém compatibilidade e usa os bounds completos de ``osm_structure.json``.
Quando ``--capture-bounds-source`` é informado, usa os bounds WGS84 da captura
(Aleph manifest/source_summary/area.json) como alvo canônico. Isso evita que ways
OSM completos que atravessam o recorte inflem artificialmente o bbox usado pelo QA.

Não modifica DEM, OSM ou Blender.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

EARTH_RADIUS = 6378137.0
MAX_LAT = 85.0511287798066

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


def mercator(lat: float, lon: float) -> tuple[float, float]:
    lat = max(-MAX_LAT, min(MAX_LAT, float(lat)))
    x = EARTH_RADIUS * math.radians(float(lon))
    y = EARTH_RADIUS * math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0))
    return x, y


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


def extract_wgs84_bounds(payload: dict) -> dict:
    """Aceita manifest Aleph, source_summary ou area.json."""
    candidate = None
    source_kind = None

    if isinstance(payload.get("bounds"), list) and len(payload["bounds"]) == 4:
        candidate = payload["bounds"]
        source_kind = "aleph_manifest"
    elif isinstance((payload.get("geografia") or {}).get("bounds"), list):
        values = (payload.get("geografia") or {}).get("bounds")
        if len(values) == 4:
            candidate = values
            source_kind = "aleph_source_summary"
    elif isinstance(payload.get("bounds_wgs84"), dict):
        b = payload["bounds_wgs84"]
        if all(b.get(key) is not None for key in ("south", "west", "north", "east")):
            candidate = [b["south"], b["west"], b["north"], b["east"]]
            source_kind = "area_registry"

    if candidate is None:
        raise ValueError("fonte de bounds não contém bounds WGS84 reconhecidos")

    south, west, north, east = (float(value) for value in candidate)
    if not (-90 <= south < north <= 90 and -180 <= west < east <= 180):
        raise ValueError("bounds WGS84 inválidos; esperado [south, west, north, east]")
    return {
        "source_kind": source_kind,
        "wgs84": {"south": south, "west": west, "north": north, "east": east},
    }


def project_wgs84_bounds(bounds: dict) -> dict:
    min_x, min_y = mercator(bounds["south"], bounds["west"])
    max_x, max_y = mercator(bounds["north"], bounds["east"])
    return {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}


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


def classify(dem: dict, target: dict, min_margin: float) -> tuple[str, list[str]]:
    notes: list[str] = []
    m = margins(dem, target)
    contained = all(value >= 0 for value in m.values())
    if not contained:
        notes.append("Parte da janela-alvo está fora dos bounds do DEM.")
        return "insufficient", notes
    if all(value >= min_margin for value in m.values()):
        notes.append("A janela-alvo está integralmente coberta pelo DEM com margem mínima em todas as bordas.")
        return "covered_with_margin", notes
    notes.append("A janela-alvo está dentro do DEM, mas próxima de pelo menos uma borda do raster.")
    return "covered_edge_sensitive", notes


def compare(
    dem_audit: dict,
    structure: dict,
    min_margin: float,
    target_bounds_epsg3857: dict | None = None,
    target_metadata: dict | None = None,
) -> dict:
    dem_schema = dem_audit.get("schema")
    structure_schema = structure.get("schema")
    if dem_schema not in SUPPORTED_DEM_SCHEMAS:
        raise ValueError(f"schema DEM não suportado: {dem_schema}")
    if structure_schema not in SUPPORTED_STRUCTURE_SCHEMAS:
        raise ValueError(f"schema OSM não suportado: {structure_schema}")

    dem = normalize_dem_bounds(dem_audit)
    full_osm = normalize_osm_bounds(structure)
    target = target_bounds_epsg3857 or full_osm
    target_kind = "capture_bounds" if target_bounds_epsg3857 is not None else "full_osm_bounds"

    overlap = intersection(dem, target)
    dem_area = area(dem)
    target_area = area(target)
    overlap_area = area(overlap) if overlap else 0.0
    coverage_ratio = overlap_area / target_area if target_area > 0 else 0.0
    status, notes = classify(dem, target, min_margin)

    pixel = (dem_audit.get("metadata") or {}).get("pixel_size") or {}
    max_pixel = max(float(pixel.get("x") or 0), float(pixel.get("y") or 0))
    edge_margin_pixels = None
    m = margins(dem, target)
    if max_pixel > 0:
        edge_margin_pixels = {key.replace("_m_projected", "_pixels_approx"): value / max_pixel for key, value in m.items()}

    warnings = []
    if coverage_ratio < 1.0 - 1e-9:
        warnings.append(f"Cobertura da janela-alvo pelo DEM é {coverage_ratio:.6f}, inferior a 100%.")
    if any(value < 0 for value in m.values()):
        warnings.append("Há pelo menos uma borda da janela-alvo fora do DEM; não extrapolar altitude automaticamente.")
    if status == "covered_edge_sensitive":
        warnings.append("O recorte está perto da borda de tile/raster; revisar artefatos antes de confiar em perfis próximos às extremidades.")
    if target_kind == "capture_bounds" and area(full_osm) > target_area * 4.0:
        warnings.append(
            "O bbox das geometrias OSM completas é muito maior que a janela da captura; isso é esperado quando ways completos atravessam o recorte e não deve invalidar o DEM por si só."
        )

    payload = {
        "schema": "bay-of-all-saints/dem-osm-coverage-v2",
        "status": status,
        "thresholds": {"minimum_margin_m_projected": min_margin},
        "target": {
            "kind": target_kind,
            "metadata": target_metadata or {},
            "bounds_epsg3857": target,
        },
        "dem_bounds_epsg3857": dem,
        "full_osm_bounds_epsg3857": full_osm,
        # Alias mantido para consumidores antigos. Quando target=capture_bounds, este campo
        # continua representando o bbox OSM completo e não a janela usada no gate.
        "osm_bounds_epsg3857": full_osm,
        "intersection_epsg3857": overlap,
        "margins": m,
        "margins_in_pixels_approx": edge_margin_pixels,
        "areas_projected": {
            "dem_m2": dem_area,
            "target_bbox_m2": target_area,
            "intersection_m2": overlap_area,
            "target_bbox_coverage_ratio": coverage_ratio,
            "full_osm_bbox_m2": area(full_osm),
            # Alias histórico: representa cobertura do alvo usado no gate nesta v2.
            "osm_bbox_coverage_ratio": coverage_ratio,
        },
        "pixel_size": pixel,
        "warnings": warnings,
        "notes": notes + [
            "O gate usa a janela-alvo declarada; quando há bounds de captura, ways OSM completos fora do recorte não inflam artificialmente a decisão.",
            "O bbox OSM completo permanece registrado para auditoria e topologia.",
            "A comparação usa EPSG:3857; ela detecta cobertura/recorte, não qualidade vertical do DEM.",
            "Margem negativa indica falta de cobertura, não autorização para extrapolar ou esticar o raster.",
            "Margem em pixels é aproximada e usa o maior pixel size reportado no audit do DEM.",
        ],
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara cobertura do DEM com OSM completo ou bounds reais da captura.")
    parser.add_argument("--dem-audit", type=Path, required=True)
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--capture-bounds-source", type=Path, help="manifest.json/source_summary.json/area.json com bounds WGS84")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-margin-m", type=float, default=20.0)
    args = parser.parse_args()
    if args.minimum_margin_m < 0:
        raise SystemExit("--minimum-margin-m não pode ser negativo")

    target_bounds = None
    target_metadata = None
    if args.capture_bounds_source:
        source = args.capture_bounds_source.resolve()
        if not source.is_file():
            raise SystemExit(f"fonte de bounds não encontrada: {source}")
        parsed = extract_wgs84_bounds(load_json(source))
        target_bounds = project_wgs84_bounds(parsed["wgs84"])
        target_metadata = {
            "source_path": str(source),
            "source_kind": parsed["source_kind"],
            "bounds_wgs84": parsed["wgs84"],
        }

    payload = compare(
        load_json(args.dem_audit),
        load_json(args.structure),
        args.minimum_margin_m,
        target_bounds_epsg3857=target_bounds,
        target_metadata=target_metadata,
    )
    write_json(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "target_kind": payload["target"]["kind"],
        "coverage_ratio": payload["areas_projected"]["target_bbox_coverage_ratio"],
        "margins": payload["margins"],
        "warnings": payload["warnings"],
    }, ensure_ascii=False, indent=2))
    return 2 if payload["status"] == "insufficient" else 0


if __name__ == "__main__":
    raise SystemExit(main())
