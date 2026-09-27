#!/usr/bin/env python3
"""Audita um DEM/GeoTIFF e exporta metadados estruturais/proveniência.

Tenta rasterio primeiro; se indisponível, usa `gdalinfo -json`. Não modifica o raster.
Com `--statistics`, calcula/solicita estatísticas verticais sem reamostrar o DEM.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_crs(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def rasterio_statistics(dataset) -> dict | None:
    if dataset.count < 1:
        return None
    valid_count = 0
    total = 0.0
    total_sq = 0.0
    minimum = None
    maximum = None
    for _, window in dataset.block_windows(1):
        values = dataset.read(1, window=window, masked=True).compressed()
        if values.size == 0:
            continue
        block_min = float(values.min())
        block_max = float(values.max())
        minimum = block_min if minimum is None else min(minimum, block_min)
        maximum = block_max if maximum is None else max(maximum, block_max)
        valid_count += int(values.size)
        total += float(values.sum(dtype="float64"))
        total_sq += float((values.astype("float64") ** 2).sum())
    if valid_count == 0:
        return {"valid_pixel_count": 0, "minimum_m": None, "maximum_m": None, "mean_m": None, "stddev_m": None}
    mean = total / valid_count
    variance = max(0.0, total_sq / valid_count - mean * mean)
    return {
        "valid_pixel_count": valid_count,
        "minimum_m": minimum,
        "maximum_m": maximum,
        "mean_m": mean,
        "stddev_m": math.sqrt(variance),
    }


def from_rasterio(path: Path, statistics: bool = False) -> dict | None:
    try:
        import rasterio  # type: ignore
    except ImportError:
        return None
    with rasterio.open(path) as dataset:
        bounds = dataset.bounds
        transform = dataset.transform
        result = {
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
            "vertical_statistics": rasterio_statistics(dataset) if statistics else None,
        }
        return result


def gdal_band_statistics(band: dict) -> dict | None:
    metadata = band.get("metadata") or {}
    flat = {}
    for value in metadata.values():
        if isinstance(value, dict):
            flat.update(value)
    def number(key):
        try:
            return float(flat[key]) if key in flat else None
        except (TypeError, ValueError):
            return None
    minimum = number("STATISTICS_MINIMUM")
    maximum = number("STATISTICS_MAXIMUM")
    mean = number("STATISTICS_MEAN")
    stddev = number("STATISTICS_STDDEV")
    if all(value is None for value in (minimum, maximum, mean, stddev)):
        return None
    return {"valid_pixel_count": None, "minimum_m": minimum, "maximum_m": maximum, "mean_m": mean, "stddev_m": stddev}


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
        "vertical_statistics": gdal_band_statistics(bands[0]) if bands else None,
    }


def from_gdal(path: Path, statistics: bool = False) -> dict | None:
    executable = shutil.which("gdalinfo")
    if not executable:
        return None
    command = [executable, "-json"]
    if statistics:
        command.append("-stats")
    command.append(str(path))
    proc = subprocess.run(command, check=True, capture_output=True, text=True)
    return parse_gdalinfo_json(json.loads(proc.stdout))


def projected_extent(meta: dict) -> dict | None:
    bounds = meta.get("bounds") or {}
    try:
        width = float(bounds["right"]) - float(bounds["left"])
        height = float(bounds["top"]) - float(bounds["bottom"])
    except (KeyError, TypeError, ValueError):
        return None
    if width < 0 or height < 0:
        return None
    return {"width_m_projected": width, "height_m_projected": height, "area_m2_projected": width * height}


def audit(path: Path, statistics: bool = False) -> dict:
    meta = from_rasterio(path, statistics=statistics) or from_gdal(path, statistics=statistics)
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
    stats = meta.get("vertical_statistics")
    if statistics and stats is None:
        warnings.append("Estatísticas verticais foram solicitadas, mas o backend não as retornou.")
    if stats and stats.get("minimum_m") is not None and stats.get("maximum_m") is not None:
        if stats["minimum_m"] < -500 or stats["maximum_m"] > 1000:
            warnings.append("Faixa de elevação incomum para o recorte; revisar nodata, unidade ou artefatos do DEM.")

    return {
        "schema": "bay-of-all-saints/dem-audit-v2",
        "source": {
            "path": str(path.resolve()),
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "metadata": meta,
        "projected_extent": projected_extent(meta),
        "statistics_requested": statistics,
        "warnings": warnings,
        "notes": [
            "Nenhuma elevação foi corrigida, suavizada ou reamostrada.",
            "EPSG:3857 mede o raster em coordenadas projetadas; métricas horizontais servem para QA estrutural e não substituem levantamento local.",
            "O terrain.tif histórico do Aleph é composto a partir dos Mapzen/Tilezen Terrain Tiles no bucket público elevation-tiles-prod.",
            "A origem/licença dos dados de elevação subjacentes deve permanecer registrada separadamente da licença do software Aleph.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita CRS, bounds, resolução, hash e opcionalmente estatísticas de um terrain.tif/DEM.")
    parser.add_argument("--dem", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--statistics", action="store_true", help="calcular/solicitar min, max, média e desvio sem reamostrar")
    args = parser.parse_args()
    if not args.dem.is_file():
        raise SystemExit(f"DEM não encontrado: {args.dem}")
    payload = audit(args.dem, statistics=args.statistics)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source": payload["source"],
        "metadata": payload["metadata"],
        "projected_extent": payload["projected_extent"],
    }, ensure_ascii=False, indent=2))
    for warning in payload["warnings"]:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
