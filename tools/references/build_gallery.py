#!/usr/bin/env python3
"""Gera uma galeria HTML local do acervo de referências do Bay of All Saints.

Não copia mídias e não altera manifests. O HTML aponta para os arquivos do acervo local.
"""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
from urllib.parse import quote

USABLE_USAGE = {"PRODUCAO_APROVADA", "REFERENCIA_INTERNA"}
ACTIVE_CANDIDATE_STATUS = {"candidate", "accepted"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def h(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def file_uri_relative(file_path: Path, output_dir: Path) -> str:
    relative = os.path.relpath(file_path, output_dir).replace(os.sep, "/")
    return "/".join(quote(part) for part in relative.split("/"))


def media_coverage(item: dict):
    yield item.get("location_id"), item.get("view"), True
    for coverage in item.get("coverage", []):
        yield coverage.get("location_id"), coverage.get("view"), False


def candidate_coverage(item: dict):
    yield item.get("location_id"), item.get("suggested_view"), True
    for coverage in item.get("coverage", []):
        yield coverage.get("location_id"), coverage.get("view"), False


def render_media_card(item: dict, local_view: str, primary: bool, media_root: Path, output_dir: Path) -> str:
    storage = item.get("storage") or {}
    logical = storage.get("logical_path") or ""
    file_path = media_root / logical
    exists = file_path.is_file()
    src = file_uri_relative(file_path, output_dir) if exists else ""
    provenance = item.get("provenance") or {}
    source_url = provenance.get("source_url")
    image = f'<img src="{h(src)}" loading="lazy" alt="{h(item.get("media_id"))}">' if exists else '<div class="missing-file">arquivo local ausente</div>'
    source = f'<a href="{h(source_url)}" target="_blank" rel="noreferrer">fonte</a>' if source_url else "sem URL de fonte"
    secondary = "principal" if primary else "cobertura adicional"
    return f"""
      <article class="card media-card">
        {image}
        <div class="card-body">
          <div class="chips"><span>{h(local_view)}</span><span>{h(item.get('usage_class'))}</span><span>{secondary}</span></div>
          <strong>{h(item.get('media_id'))}</strong>
          <small>{h(logical)}</small>
          <small>SHA-256: {h(storage.get('sha256') or 'não registrado')}</small>
          <small>Licença: {h(provenance.get('license') or 'não informada')} · {h(provenance.get('license_status'))}</small>
          <small>{source}</small>
        </div>
      </article>
    """


def render_candidate_card(item: dict, local_view: str, primary: bool) -> str:
    secondary = "principal" if primary else "cobertura adicional"
    notes = " ".join(item.get("notes", []))
    return f"""
      <article class="card candidate-card">
        <div class="candidate-preview">candidato</div>
        <div class="card-body">
          <div class="chips"><span>{h(local_view)}</span><span>{secondary}</span></div>
          <strong>{h(item.get('file_title'))}</strong>
          <small>ID: {h(item.get('candidate_id'))}</small>
          <small>Licença esperada: {h(item.get('expected_license') or 'verificar via API')}</small>
          <small>{h(notes)}</small>
          <a href="{h(item.get('page_url'))}" target="_blank" rel="noreferrer">abrir no Wikimedia Commons</a>
        </div>
      </article>
    """


def build_gallery(repo_root: Path, area: str, media_root: Path, output: Path, include_candidates: bool = True) -> dict:
    repo_root = repo_root.resolve()
    media_root = media_root.resolve()
    output = output.resolve()
    area_dir = repo_root / "world" / "areas" / area
    area_data = load_json(area_dir / "area.json")
    locations = load_json(area_dir / "locations.json").get("locations", [])
    media = load_json(area_dir / "media-manifest.json").get("media", [])
    candidates_path = area_dir / "reference-candidates.json"
    candidates = load_json(candidates_path).get("candidates", []) if include_candidates and candidates_path.is_file() else []

    media_by_location: dict[str, list[tuple[dict, str, bool]]] = {}
    for item in media:
        for location_id, view, primary in media_coverage(item):
            if location_id and view:
                media_by_location.setdefault(location_id, []).append((item, view, primary))

    candidates_by_location: dict[str, list[tuple[dict, str, bool]]] = {}
    for item in candidates:
        if item.get("status") not in ACTIVE_CANDIDATE_STATUS:
            continue
        for location_id, view, primary in candidate_coverage(item):
            if location_id and view:
                candidates_by_location.setdefault(location_id, []).append((item, view, primary))

    sections = []
    summary = []
    for loc in sorted(locations, key=lambda item: (-item.get("priority", 0), item.get("name", ""))):
        lid = loc["location_id"]
        local_media = media_by_location.get(lid, [])
        available_views = {
            view for item, view, _ in local_media
            if item.get("usage_class") in USABLE_USAGE and (item.get("provenance") or {}).get("license_status") in {"verified", "pending"}
        }
        required_views = set(loc.get("required_views", []))
        missing_views = sorted(required_views - available_views)
        local_candidates = sorted(candidates_by_location.get(lid, []), key=lambda x: (x[1], x[0].get("candidate_id", "")))
        media_cards = "".join(render_media_card(item, view, primary, media_root, output.parent) for item, view, primary in local_media)
        candidate_cards = "".join(render_candidate_card(item, view, primary) for item, view, primary in local_candidates)
        sections.append(f"""
        <section id="{h(lid)}" class="location-section">
          <header>
            <div><span class="priority">P{h(loc.get('priority'))}</span><h2>{h(loc.get('name'))}</h2></div>
            <p><code>{h(lid)}</code> · classe {h(loc.get('fidelity_class'))} · modelo {h(loc.get('model_status'))} · referência {h(loc.get('reference_status'))}</p>
          </header>
          <div class="status-row"><strong>Vistas obrigatórias:</strong> {h(', '.join(sorted(required_views)) or '-')}</div>
          <div class="status-row {'alert' if missing_views else 'ok'}"><strong>Faltando:</strong> {h(', '.join(missing_views) or 'nenhuma')}</div>
          <h3>Mídias importadas</h3>
          <div class="grid">{media_cards or '<p class="empty">Nenhuma mídia importada para este local.</p>'}</div>
          <h3>Candidatos auditáveis</h3>
          <div class="grid">{candidate_cards or '<p class="empty">Nenhum candidato catalogado.</p>'}</div>
        </section>
        """)
        summary.append({"location_id": lid, "media": len(local_media), "candidates": len(local_candidates), "missing_views": missing_views})

    title = f"Bay of All Saints · referências · {area}"
    html_doc = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)}</title>
<style>
:root{{--bg:#0b1018;--panel:#121a27;--line:#28364a;--text:#e5edf7;--muted:#9aa9bd;--soft:#192536;--ok:#8fd3a6;--warn:#f0bd75}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}}
a{{color:#b9d8ff}} .page{{max-width:1500px;margin:auto;padding:28px}} .hero{{margin-bottom:30px}} .hero h1{{font-size:32px;margin:0 0 8px}} .hero p{{color:var(--muted);max-width:900px}}
nav{{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}} nav a{{background:var(--soft);border:1px solid var(--line);padding:7px 10px;border-radius:8px;text-decoration:none}}
.location-section{{border-top:1px solid var(--line);padding:28px 0}} .location-section header>div{{display:flex;align-items:center;gap:12px}} h2{{margin:0;font-size:25px}} h3{{margin:20px 0 10px;font-size:16px}} code{{color:#cfe0f6}}
.priority,.chips span{{display:inline-block;background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:3px 8px;font-size:12px}} .status-row{{color:var(--muted);margin:5px 0}} .status-row.alert{{color:var(--warn)}} .status-row.ok{{color:var(--ok)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}} .card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;min-height:170px}} .card img{{width:100%;height:210px;object-fit:cover;background:#05080d}} .card-body{{display:flex;flex-direction:column;gap:6px;padding:12px}} .card small{{color:var(--muted);overflow-wrap:anywhere}} .chips{{display:flex;gap:5px;flex-wrap:wrap}} .missing-file,.candidate-preview{{height:160px;display:grid;place-items:center;background:#0d1520;color:var(--muted)}} .candidate-preview{{font-size:22px;letter-spacing:.08em;text-transform:uppercase}} .empty{{color:var(--muted)}}
</style></head><body><main class="page">
<section class="hero"><h1>{h(title)}</h1><p>Galeria local gerada a partir dos manifests versionados. Os arquivos binários permanecem fora do Git. Candidatos não são tratados como mídia importada até passarem pela ingestão, licença e hash.</p><p>Área: <strong>{h(area_data.get('name') or area)}</strong></p></section>
<nav>{''.join(f'<a href="#{h(loc["location_id"])}">{h(loc["name"])}</a>' for loc in locations)}</nav>
{''.join(sections)}
</main></body></html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_doc, encoding="utf-8")
    return {"output": str(output), "area_id": area, "locations": summary}


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera galeria HTML local das referências de uma área.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--area", required=True)
    parser.add_argument("--media-root", type=Path, default=Path("world-reference"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-candidates", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    media_root = args.media_root if args.media_root.is_absolute() else repo_root / args.media_root
    output = args.output or (repo_root / "artifacts" / "reference-gallery" / args.area / "index.html")
    if not output.is_absolute():
        output = repo_root / output
    result = build_gallery(repo_root, args.area, media_root, output, not args.no_candidates)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
