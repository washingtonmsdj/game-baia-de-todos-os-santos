#!/usr/bin/env python3
"""Inspeciona uma captura Aleph e gera um resumo de proveniência.

Uso:
    python tools/aleph/inspect_capture.py /caminho/para/aleph-RUN
    python tools/aleph/inspect_capture.py /caminho/para/aleph-RUN --output docs/reports/aleph/centro/source_summary.json

O script não modifica a captura e não copia arquivos pesados.
Usa apenas a biblioteca padrão do Python.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

EXPECTED_FORMAT = "aleph-python"
KNOWN_FORMAT_VERSION = 3
EARTH_RADIUS_M = 6_371_008.8

POLICIES = {
    "osm": {
        "classe_uso": "PRODUCAO_COM_ATRIBUICAO",
        "licenca": "ODbL (OpenStreetMap); confirmar requisitos do uso concreto",
        "observacao": "Adequado para vias, footprints, POIs e proxies; manter atribuição e proveniência.",
    },
    "terrain": {
        "classe_uso": "PENDENTE_VERIFICACAO",
        "licenca": "Origem/licença do dataset de elevação deve ser confirmada por captura",
        "observacao": "Usar como referência/MVP até a fonte efetiva do DEM ser registrada e aprovada.",
    },
    "satellite": {
        "classe_uso": "PROIBIDO_PRODUCAO",
        "licenca": "Conteúdo externo; a implementação Aleph analisada usa tiles do Google",
        "observacao": "Não incorporar como textura nem usar como fonte derivativa automática de produção.",
    },
    "streetview": {
        "classe_uso": "PROIBIDO_PRODUCAO",
        "licenca": "Conteúdo externo; a implementação Aleph analisada usa Google Street View",
        "observacao": "Não incorporar ao jogo/assets nem usar como fonte derivativa automática de produção.",
    },
}

EXPECTED_FILES = {
    "osm": ["map.osm", "terrain.tif"],
    "satellite": ["satellite.tif", "satellite.png"],
    "streetview": ["streetview/photos.geojson"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(min(1.0, h)))


def validate_bounds(value) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError("manifest.bounds deve conter [south, west, north, east].")
    try:
        south, west, north, east = map(float, value)
    except (TypeError, ValueError) as exc:
        raise ValueError("manifest.bounds contém valores inválidos.") from exc
    if not (-90 <= south <= north <= 90 and -180 <= west <= east <= 180):
        raise ValueError("manifest.bounds está fora dos limites WGS84 esperados.")
    return south, west, north, east


def source_hosts(stage: dict) -> dict[str, int]:
    hosts = Counter()
    results = stage.get("results", [])
    if not isinstance(results, list):
        return {}
    for item in results:
        if not isinstance(item, dict):
            continue
        for key in ("source_url", "streetview_url"):
            value = item.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                host = urlparse(value).netloc.lower()
                if host:
                    hosts[host] += 1
    return dict(sorted(hosts.items()))


def file_status(folder: Path, modes: set[str]) -> dict[str, dict]:
    status = {}
    for mode in sorted(modes):
        for relative in EXPECTED_FILES.get(mode, []):
            path = folder / relative
            status[relative] = {
                "presente": path.is_file(),
                "bytes": path.stat().st_size if path.is_file() else None,
            }
    return status


def inspect(folder: Path) -> dict:
    folder = folder.expanduser().resolve()
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest.json não encontrado em: {folder}")

    raw = manifest_path.read_bytes()
    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("manifest.json não contém JSON válido.") from exc
    if not isinstance(manifest, dict):
        raise ValueError("manifest.json deve conter um objeto JSON na raiz.")

    warnings: list[str] = []
    format_name = manifest.get("format")
    version = manifest.get("version")
    if format_name != EXPECTED_FORMAT:
        warnings.append(f"Formato inesperado: {format_name!r}; esperado {EXPECTED_FORMAT!r}.")
    if version != KNOWN_FORMAT_VERSION:
        warnings.append(
            f"Versão de manifesto {version!r} diferente da versão Aleph conhecida ({KNOWN_FORMAT_VERSION}); "
            "revisar compatibilidade antes de automatizar importação."
        )

    bounds = validate_bounds(manifest.get("bounds"))
    south, west, north, east = bounds
    center_lat = (south + north) / 2
    width_m = haversine((center_lat, west), (center_lat, east))
    height_m = haversine((south, west), (north, west))

    stages = manifest.get("stages", [])
    if not isinstance(stages, list):
        raise ValueError("manifest.stages deve ser uma lista.")

    stage_summaries = []
    modes: set[str] = set()
    combined_hosts = Counter()
    for stage in stages:
        if not isinstance(stage, dict):
            warnings.append("Estágio não reconhecido ignorado por não ser objeto JSON.")
            continue
        mode = str(stage.get("mode", "desconhecido"))
        modes.add(mode)
        results = stage.get("results", [])
        count = len(results) if isinstance(results, list) else None
        hosts = source_hosts(stage)
        combined_hosts.update(hosts)
        policy_key = "terrain" if mode == "osm" else mode
        stage_summaries.append(
            {
                "modo": mode,
                "resultados_registrados": count,
                "grid": stage.get("grid"),
                "hosts_origem_observados": hosts,
                "politica": POLICIES.get(policy_key, {
                    "classe_uso": "PENDENTE_VERIFICACAO",
                    "licenca": "Não registrada",
                    "observacao": "Fonte desconhecida; revisar manualmente.",
                }),
            }
        )

    # O estágio OSM do Aleph também contém terrain.tif; registre as duas políticas explicitamente.
    policies = []
    if "osm" in modes:
        policies.append({"fonte": "osm", **POLICIES["osm"]})
        policies.append({"fonte": "terrain", **POLICIES["terrain"]})
    for mode in ("satellite", "streetview"):
        if mode in modes:
            policies.append({"fonte": mode, **POLICIES[mode]})

    options = manifest.get("options") if isinstance(manifest.get("options"), dict) else {}

    return {
        "schema": "bay-of-all-saints/aleph-source-summary-v1",
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "capture_folder": str(folder),
        "manifest": {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "format": format_name,
            "version": version,
            "state": manifest.get("state"),
            "started_at": manifest.get("started_at"),
            "finished_at": manifest.get("finished_at"),
            "exports_saved": manifest.get("exports_saved"),
        },
        "geografia": {
            "crs_bounds": "WGS84 / latitude-longitude",
            "bounds": [south, west, north, east],
            "centro": [center_lat, (west + east) / 2],
            "largura_aproximada_m": round(width_m, 2),
            "altura_aproximada_m": round(height_m, 2),
            "terrain_crs_esperado_pelo_aleph": "EPSG:3857",
        },
        "opcoes": options,
        "estagios": stage_summaries,
        "hosts_origem_observados": dict(sorted(combined_hosts.items())),
        "arquivos_esperados": file_status(folder, modes),
        "politicas_de_uso": policies,
        "warnings": warnings,
        "recomendacoes": [
            "Preservar o manifest.json original junto à captura.",
            "Registrar o commit do Aleph usado para criar a captura.",
            "Manter OSM/proxies separados de hero assets no Blender.",
            "Não promover terreno a asset final até confirmar origem/licença do dataset de elevação.",
            "Não importar imagens Google Satellite/Street View como assets de produção.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspeciona uma captura Aleph sem modificar seus arquivos.")
    parser.add_argument("capture_folder", type=Path, help="Pasta que contém manifest.json")
    parser.add_argument("--output", type=Path, help="Arquivo JSON de saída. Se omitido, imprime no stdout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        summary = inspect(args.capture_folder)
    except (OSError, ValueError) as exc:
        print(f"[aleph-inspect] erro: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(f"[aleph-inspect] resumo salvo em: {output}")
    else:
        print(payload, end="")

    if summary["warnings"]:
        print(f"[aleph-inspect] concluído com {len(summary['warnings'])} aviso(s).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
