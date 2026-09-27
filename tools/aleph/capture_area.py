#!/usr/bin/env python3
"""Executa uma captura Aleph limitada a OSM + terreno e registra proveniência.

Exemplo:
    python tools/aleph/capture_area.py \
      --area-id centro-historico \
      --bbox SOUTH WEST NORTH EAST

Por segurança, este wrapper NÃO oferece opções para Satellite ou Street View.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from inspect_capture import inspect

PINNED_ALEPH_COMMIT = "d24c61507481a91a0dd6afac4f97626a4e5ea780"
AREA_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def area_id(value: str) -> str:
    if not AREA_ID_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "area-id deve usar somente minúsculas, números e hífens, por exemplo: centro-historico"
        )
    return value


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Captura OSM + terreno via Aleph e gera relatório de proveniência."
    )
    parser.add_argument("--area-id", required=True, type=area_id)
    parser.add_argument(
        "--bbox",
        required=True,
        nargs=4,
        type=float,
        metavar=("SOUTH", "WEST", "NORTH", "EAST"),
    )
    parser.add_argument("--terrain-zoom", type=int, default=14, choices=range(1, 15))
    parser.add_argument("--captures-root", type=Path, default=Path("world-source"))
    parser.add_argument("--reports-root", type=Path, default=Path("docs/reports/aleph"))
    parser.add_argument("--aleph-bin", default="alephgeo")
    parser.add_argument("--aleph-commit", default=PINNED_ALEPH_COMMIT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def validate_bbox(values: list[float]) -> None:
    south, west, north, east = values
    if not (-90 <= south < north <= 90):
        raise ValueError("bbox inválido: SOUTH deve ser menor que NORTH e ambos devem estar em -90..90")
    if not (-180 <= west < east <= 180):
        raise ValueError("bbox inválido: WEST deve ser menor que EAST e ambos devem estar em -180..180")


def build_command(args: argparse.Namespace, capture_parent: Path) -> list[str]:
    return [
        args.aleph_bin,
        "capture",
        "create",
        "--bbox",
        *(format(v, ".10g") for v in args.bbox),
        "--sources",
        "osm",
        "--terrain-zoom",
        str(args.terrain_zoom),
        "-o",
        str(capture_parent),
        "--yes",
        "--json",
    ]


def run_capture(command: list[str]) -> dict:
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=None,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "alephgeo não foi encontrado. Instale o Aleph pinado ou informe --aleph-bin."
        ) from exc

    if completed.returncode != 0:
        raise RuntimeError(f"Aleph terminou com código {completed.returncode}.")

    stdout = completed.stdout.strip()
    if not stdout:
        raise RuntimeError("Aleph não retornou o JSON esperado no stdout.")
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Saída --json do Aleph não pôde ser interpretada.") from exc
    if not isinstance(result, dict) or not result.get("folder"):
        raise RuntimeError("Resultado do Aleph não contém a pasta da captura.")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        validate_bbox(args.bbox)
    except ValueError as exc:
        print(f"[capture-area] erro: {exc}", file=sys.stderr)
        return 2

    capture_parent = args.captures_root.expanduser().resolve() / args.area_id
    report_dir = args.reports_root.expanduser().resolve() / args.area_id
    command = build_command(args, capture_parent)

    if args.dry_run:
        print(json.dumps({
            "area_id": args.area_id,
            "aleph_commit": args.aleph_commit,
            "command": command,
            "report": str(report_dir / "source_summary.json"),
        }, ensure_ascii=False, indent=2))
        return 0

    capture_parent.mkdir(parents=True, exist_ok=True)
    try:
        result = run_capture(command)
        folder = Path(result["folder"]).expanduser().resolve()
        summary = inspect(folder)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"[capture-area] erro: {exc}", file=sys.stderr)
        return 2

    summary["area_id"] = args.area_id
    summary["aleph"] = {
        "repository": "Belluxx/Aleph",
        "expected_commit": args.aleph_commit,
        "captured_via_wrapper_at": datetime.now(timezone.utc).isoformat(),
        "command_sources": ["osm"],
        "terrain_zoom": args.terrain_zoom,
    }
    summary["capture_result"] = result

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "source_summary.json"
    report_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "area_id": args.area_id,
        "capture_folder": str(folder),
        "report": str(report_path),
        "status": result.get("status"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
