#!/usr/bin/env python3
"""Registra uma mídia local no manifesto sem copiar binários para o Git."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path


VIEWS = {
    "front", "rear", "left", "right", "oblique_left", "oblique_right", "roof", "access",
    "street_context", "waterfront_context", "detail", "panorama", "map"
}
SOURCE_TYPES = {"own_photo", "licensed_photo", "public_archive", "government", "osm", "aleph_reference", "other"}
USAGE_CLASSES = {"PRODUCAO_APROVADA", "REFERENCIA_INTERNA", "TEMPORARIA", "PROIBIDO_PRODUCAO"}
LICENSE_STATUS = {"verified", "pending", "restricted", "unknown"}
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Registra uma imagem de referência no catálogo do projeto.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--area", required=True)
    parser.add_argument("--location", required=True)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--media-root", type=Path, required=True, help="raiz local do acervo; não é gravada no Git")
    parser.add_argument("--view", required=True, choices=sorted(VIEWS))
    parser.add_argument("--source-type", required=True, choices=sorted(SOURCE_TYPES))
    parser.add_argument("--usage-class", required=True, choices=sorted(USAGE_CLASSES))
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--license-status", required=True, choices=sorted(LICENSE_STATUS))
    parser.add_argument("--license")
    parser.add_argument("--source-url")
    parser.add_argument("--capture-date", help="AAAA-MM-DD")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--heading", type=float)
    parser.add_argument("--notes", action="append", default=[])
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    area_dir = repo_root / "world" / "areas" / args.area
    locations_path = area_dir / "locations.json"
    manifest_path = area_dir / "media-manifest.json"

    media_file = args.file.expanduser().resolve()
    media_root = args.media_root.expanduser().resolve()
    if not media_file.is_file():
        raise SystemExit(f"Arquivo não encontrado: {media_file}")
    if media_file.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise SystemExit(f"Extensão não suportada: {media_file.suffix}")
    try:
        logical_path = media_file.relative_to(media_root).as_posix()
    except ValueError as exc:
        raise SystemExit("--file precisa estar dentro de --media-root") from exc

    locations = load_json(locations_path)
    valid_locations = {item["location_id"] for item in locations.get("locations", [])}
    if args.location not in valid_locations:
        raise SystemExit(f"location_id inexistente em {locations_path}: {args.location}")

    if args.capture_date:
        try:
            date.fromisoformat(args.capture_date)
        except ValueError as exc:
            raise SystemExit("--capture-date deve usar AAAA-MM-DD") from exc
    if (args.lat is None) != (args.lon is None):
        raise SystemExit("--lat e --lon devem ser informados juntos")
    if args.lat is not None and not -90 <= args.lat <= 90:
        raise SystemExit("--lat fora do intervalo válido")
    if args.lon is not None and not -180 <= args.lon <= 180:
        raise SystemExit("--lon fora do intervalo válido")
    if args.heading is not None and not 0 <= args.heading < 360:
        raise SystemExit("--heading deve estar em [0, 360)")
    if args.usage_class == "PRODUCAO_APROVADA" and args.license_status != "verified":
        raise SystemExit("PRODUCAO_APROVADA exige --license-status verified")

    digest = sha256_file(media_file)
    manifest = load_json(manifest_path)
    existing = manifest.get("media", [])
    duplicate = next((item for item in existing if (item.get("storage") or {}).get("sha256") == digest), None)
    if duplicate:
        raise SystemExit(f"Arquivo já registrado como {duplicate.get('media_id')}")

    media_id = f"{args.location}-{args.view}-{digest[:12]}"
    item = {
        "media_id": media_id,
        "location_id": args.location,
        "source_type": args.source_type,
        "usage_class": args.usage_class,
        "view": args.view,
        "capture": None,
        "storage": {"logical_path": logical_path, "sha256": digest},
        "provenance": {
            "source_name": args.source_name,
            "license_status": args.license_status,
            "license": args.license,
            "source_url": args.source_url,
            "notes": ""
        },
        "notes": args.notes
    }
    if args.capture_date or args.lat is not None or args.heading is not None:
        item["capture"] = {
            "date": args.capture_date,
            "lat": args.lat,
            "lon": args.lon,
            "heading_deg": args.heading,
            "notes": ""
        }

    existing.append(item)
    existing.sort(key=lambda value: (value.get("location_id", ""), value.get("view", ""), value.get("media_id", "")))
    manifest["media"] = existing
    write_json(manifest_path, manifest)

    print(json.dumps({"registered": media_id, "logical_path": logical_path, "sha256": digest}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
