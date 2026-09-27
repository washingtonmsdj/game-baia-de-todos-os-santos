#!/usr/bin/env python3
"""Audita um DEM/GeoTIFF e exporta metadados estruturais.

Tenta rasterio primeiro; se indisponível, usa `gdalinfo -json`. Não modifica o raster.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def normalize_crs(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def from_rasterio(path: Path) -> dict | None:
    try:
        import rasterio  # type: ignore
    except ImportError:
        return None
    with rasterio.open(path) as dataset:
        bounds = dataset.bounds
        transform = dataset.transform
        return {
            "backend": "rasterio",
            "driver": dataset.driver,
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "dtype": list(dataset.dtypes),
            "crs": normalize_crs(dataset.crs),
            "nodata": list(dataset.nodatavals),
            "bounds": {"left": bounds.left, "bottom": bounds.bottom, "right": bounds.right, "top": bounds.top},
            "pixel_size": {"x": abs(transform.a), "y": abs(transform.e)},
            "transform": [transform.a, transform.b, transform.c, transform.d, transform.e, transform.f],
        }


def parse_gdalinfo_json(data: dict) -> dict:
    size = data.get("size") or [None, None]
    geo = data.get("geoTransform") or [None] * 6
    corners = data.get("cornerCoordinates") or {}
    lower_left = corners.get("lowerLeft") or [None, None]
    upper_right = corners.get("upperRight") or [None, None]
    bands = data.get("bands") or []
    coord = data.get("coordinateSystem") or {}
    wkt = coord.get("wkt")
    return {
        "backend": "gdalinfo",
        "driver": ((data.get("driverShortName") or data.get("driverLongName"))),
        "width": size[0],
        "height": size[1],
        "band_count": len(bands),
        "dtype": [band.get("type") for band in bands],
        "crs": normalize_crs(wkt),
        "nodata": [band.get("noDataValue") for band in bands],
        "bounds": {
            "left": lower_left[0],
            "bottom": lower_left[1],
            "right": upper_right[0],
            "top": upper_right[1],
        },
        "pixel_size": {
            "x": abs(geo[1]) if len(geo) >= 6 and geo[1] is not None else None,
            "y": abs(geo[5]) if len(geo) >= 6 and geo[5] is not None else None,
        },
        "transform": geo[:6],
    }


def from_gdal(path: Path) -> dict | None:
    executable = shutil.which("gdalinfo")
    if not executable:
        return None
    proc = subprocess.run([executable, "-json", str(path)], check=True, capture_output=True, text=True)
    return parse_gdalinfo_json(json.loads(proc.stdout))


def audit(path: Path) -> dict:
    meta = from_rasterio(path) or from_gdal(path)
    if meta is None:
        raise SystemExit(
            "Não foi possível auditar o DEM: instale `rasterio` ou disponibilize `gdalinfo` no PATH. "
            "O script não tenta interpretar TIFF geoespacial parcialmente."
        )
    warnings = []
    crs = (meta.get("crs") or "").upper()
    if "3857" not in crs and "WEB MERCATOR" not in crs and "PSEUDO-MERCATOR" not in crs:
        warnings.append("CRS não identificado como EPSG:3857/Web Mercator; conferir contra o manifest Aleph.")
    if not meta.get("width") or not meta.get("height"):
        warnings.append("Dimensões do raster não foram obtidas.")
    pixel = meta.get("pixel_size") or {}
    if pixel.get("x") is None or pixel.get("y") is None:
        warnings.append("Resolução/pixel size não foi obtida.")
    return {
        "schema": "bay-of-all-saints/dem-audit-v1",
        "source": str(path.resolve()),
        "metadata": meta,
        "warnings": warnings,
        "notes": [
            "Auditoria de metadados somente; nenhuma elevação foi corrigida ou reamostrada.",
            "A origem/licença efetiva do DEM deve continuar registrada separadamente da licença do software Aleph.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita CRS, bounds e resolução de um terrain.tif/DEM.")
    parser.add_argument("--dem", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.dem.is_file():
        raise SystemExit(f"DEM não encontrado: {args.dem}")
    payload = audit(args.dem)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["metadata"], ensure_ascii=False, indent=2))
    for warning in payload["warnings"]:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
