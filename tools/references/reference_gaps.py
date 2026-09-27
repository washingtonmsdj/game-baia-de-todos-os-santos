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


def media_pairs(item: dict):
    yield item.get("location_id"), item.get("view")
    for coverage in item.get("coverage", []):
        yield coverage.get("location_id"), coverage.get("view")


def candidate_pairs(item: dict):
    yield item.get("location_id"), item.get("suggested_view")
    for coverage in item.get("coverage", []):
        yield coverage.get("location_id"), coverage.get("view")


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

    views_by_location: dict[str, set[str]] = {}
    for item in media:
        if item.get("usage_class") not in USABLE_USAGE:
            continue
        for location_id, view in media_pairs(item):
            if location_id and view:
                views_by_location.setdefault(location_id, set()).add(view)

    candidate_suggestions_by_location: dict[str, list[dict]] = {}
    for item in candidates:
        if item.get("status") not in ACTIVE_CANDIDATE_STATUS:
            continue
        for location_id, view in candidate_pairs(item):
            if not location_id or not view:
                continue
            candidate_suggestions_by_location.setdefault(location_id, []).append({
                "candidate_id": item.get("candidate_id"),
                "view": view,
                "file_title": item.get("file_title"),
                "page_url": item.get("page_url"),
                "expected_license": item.get("expected_license")
            })

    report = []
    for loc in sorted(locations, key=lambda item: (-item.get("priority", 0), item.get("name", ""))):
        location_id = loc["location_id"]
        available_views = sorted(views_by_location.get(location_id, set()))
        required_views = loc.get("required_views", [])
        missing_views = sorted(set(required_views) - set(available_views))

        suggestions = [
            candidate for candidate in candidate_suggestions_by_location.get(location_id, [])
            if candidate["view"] in missing_views
        ]
        unique = {}
        for candidate in suggestions:
            unique[(candidate["candidate_id"], candidate["view"])] = candidate
        suggestions = sorted(unique.values(), key=lambda item: (item.get("view") or "", item.get("candidate_id") or ""))

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
