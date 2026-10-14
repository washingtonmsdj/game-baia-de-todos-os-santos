"""Recupera páginas públicas descobertas; não envia requerimentos ou autentica."""
import concurrent.futures
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/research/lacerda-b80-installation-xy"
RAW = ROOT / "world-reference/mvp-centro-lacerda/research-20261006-semob"
URLS = {
    "semob": "https://mobilidade.salvador.ba.gov.br/",
    "transparencia": "https://transparencia.salvador.ba.gov.br/",
    "sefaz-semob": "https://www2.sefaz.salvador.ba.gov.br/servico/semob",
    "sefaz-licitacoes": "https://www2.sefaz.salvador.ba.gov.br/transparencia/licitacoes",
    "transparencia-antigo": "https://antigotransparencia.salvador.ba.gov.br/",
    "dom": "https://dom.salvador.ba.gov.br/",
}


def fetch(item):
    name, url = item
    record = {"locator_id": name, "requested_url": url, "process_target": "151228/2023", "contract_target": "SEMOB 008/2023", "release_status": "DEV_REFERENCE_ONLY", "retrieved_at": datetime.now(timezone.utc).isoformat(), "technical_installation_document": False}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "BayOfAllSaints-DocumentResearch/1.0"})
        try:
            response = urllib.request.urlopen(request, timeout=16)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            content = response.read(5_000_001)
            record.update({"status_code": response.code, "final_url": response.url, "content_type": response.headers.get("Content-Type"), "bytes": len(content)})
        if len(content) > 5_000_000:
            record["error"] = "Página excede limite de aquisição"
            return record
        path = RAW / (name + ".html")
        path.write_bytes(content)
        record.update({"raw_file": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(content).hexdigest(), "links": list(dict.fromkeys(re.findall(r'(?:href|src)=[\"\']([^\"\']+)', content.decode('utf-8', errors='replace'), re.I)))[:180]})
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        record["error"] = str(exc)
    return record


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    phase = "annex" if "--annex" in sys.argv else ("search" if "--search" in sys.argv else ("navigation" if "--navigation" in sys.argv else "entry"))
    urls = URLS if phase == "entry" else {
        "semob-licitacao": "https://mobilidade.salvador.ba.gov.br/licitacao",
        "semob-transparencia": "https://mobilidade.salvador.ba.gov.br/transparencia",
        "transparencia-env": "https://transparencia.salvador.ba.gov.br/env.js",
        "transparencia-app": "https://transparencia.salvador.ba.gov.br/static/js/main.bfb54192.chunk.js",
        "transparencia-antigo-contratos": "https://antigotransparencia.salvador.ba.gov.br/Modulos/LicitacaoContratos.aspx",
    }
    if phase == "search":
        urls = {
            "semob-search-process": "https://mobilidade.salvador.ba.gov.br/wp-json/wp/v2/search?search=151228&per_page=100",
            "semob-search-otis": "https://mobilidade.salvador.ba.gov.br/wp-json/wp/v2/search?search=Otis&per_page=100",
            "semob-search-inexigibilidade": "https://mobilidade.salvador.ba.gov.br/wp-json/wp/v2/search?search=inexigibilidade&per_page=100",
            "semob-search-lacerda": "https://mobilidade.salvador.ba.gov.br/wp-json/wp/v2/search?search=Lacerda&per_page=100",
            "compras-busca": "http://compras.salvador.ba.gov.br/novo/index.php?secao=licitacao_busca",
        }
    if phase == "annex":
        urls = {
            "semob-aquisicoes": "https://mobilidade.salvador.ba.gov.br/aquisicoes/",
            "semob-aquisicoes-api": "https://mobilidade.salvador.ba.gov.br/wp-json/wp/v2/posts/1169",
            "semob-search-contract": "https://mobilidade.salvador.ba.gov.br/wp-json/wp/v2/search?search=008%2F2023&per_page=100",
        }
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(fetch, urls.items()))
    report = {"schema": "boas/public-document-locators-v1", "records": records, "outbound_requests_sent": False, "note": "GETs públicos apenas. HTML, erros HTTP e landing pages não são dados dimensionais de instalação. Endereço DOM sondado como candidato, não previamente validado."}
    name = {"entry": "semob_locators.json", "navigation": "semob_navigation.json", "search": "semob_search.json", "annex": "semob_annex_locators.json"}[phase]
    (OUT / name).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{k: v for k, v in r.items() if k != "links"} for r in records], ensure_ascii=False))


if __name__ == "__main__":
    main()
