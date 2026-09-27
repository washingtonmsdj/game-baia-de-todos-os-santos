#!/usr/bin/env python3
"""Gera relatório objetivo das referências que ainda faltam por local."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


USABLE_USAGE = {"PRODUCAO_APROVADA", "REFERENCIA_INTERNA"}
ACTIVE_CANDIDATE_STATUS = {"candidate", "accepted"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Mostra lacunas de referência visual por local.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--area", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    area_dir = args.repo_root.resolve() / "world" / "areas" / args.area
    locations = load(area_dir / "locations.json").get("locations", [])
    media = load(area_dir / "media-manifest.json").get("media", [])
    candidates_path = area_dir / "reference-candidates.json"
    candidates = load(candidates_path).get("candidates", []) if candidates_path.is_file() else []

    media_by_location: dict[str, list[dict]] = {}
    for item in media:
        if item.get("usage_class") in USABLE_USAGE:
            media_by_location.setdefault(item.get("location_id", ""), []).append(item)

    candidates_by_location: dict[str, list[dict]] = {}
    for item in candidates:
        if item.get("status") in ACTIVE_CANDIDATE_STATUS:
            candidates_by_location.setdefault(item.get("location_id", ""), []).append(item)

    report = []
    for loc in sorted(locations, key=lambda item: (-item.get("priority", 0), item.get("name", ""))):
        location_id = loc["location_id"]
        items = media_by_location.get(location_id, [])
        available_views = sorted({item.get("view") for item in items if item.get("view")})
        required_views = loc.get("required_views", [])
        missing_views = sorted(set(required_views) - set(available_views))

        suggestions = []
        for candidate in candidates_by_location.get(location_id, []):
            view = candidate.get("suggested_view")
            if view in missing_views:
                suggestions.append({
                    "candidate_id": candidate.get("candidate_id"),
                    "view": view,
                    "file_title": candidate.get("file_title"),
                    "page_url": candidate.get("page_url"),
                    "expected_license": candidate.get("expected_license")
                })
        suggestions.sort(key=lambda item: (item.get("view") or "", item.get("candidate_id") or ""))

        report.append({
            "location_id": location_id,
            "name": loc["name"],
            "priority": loc["priority"],
            "fidelity_class": loc["fidelity_class"],
            "model_status": loc["model_status"],
            "reference_status": loc["reference_status"],
            "available_views": available_views,
            "missing_views": missing_views,
            "candidate_suggestions": suggestions,
            "ready_for_visual_review": not missing_views and loc["reference_status"] in {"sufficient", "verified"}
        })

    if args.as_json:
        print(json.dumps({"area_id": args.area, "locations": report}, ensure_ascii=False, indent=2))
    else:
        for item in report:
            marker = "OK" if item["ready_for_visual_review"] else "PENDENTE"
            print(f"[{marker}] P{item['priority']} {item['name']} ({item['location_id']})")
            print(f"  modelo: {item['model_status']} | referência: {item['reference_status']} | classe: {item['fidelity_class']}")
            print(f"  vistas disponíveis: {', '.join(item['available_views']) or '-'}")
            print(f"  vistas faltantes: {', '.join(item['missing_views']) or '-'}")
            if item["candidate_suggestions"]:
                print("  candidatos disponíveis:")
                for candidate in item["candidate_suggestions"]:
                    print(f"    - {candidate['view']}: {candidate['candidate_id']} — {candidate['file_title']}")
            elif item["missing_views"]:
                print("  candidatos disponíveis: nenhum catalogado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
