#!/usr/bin/env python3
"""Baixa e registra referências do Wikimedia Commons com proveniência verificável.

O binário fica fora do Git; o manifesto versionado recebe hash, licença e metadados.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen


API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "BayOfAllSaintsReferencePipeline/1.0 (GitHub: washingtonmsdj/game-baia-de-todos-os-santos)"
FREE_LICENSE_MARKERS = (
    "CC BY ",
    "CC BY-SA ",
    "CC0",
    "PUBLIC DOMAIN",
    "PUBLIC DOMAIN MARK",
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return " ".join(text.split())


def metadata_value(ext: dict, key: str) -> str:
    value = ext.get(key)
    if isinstance(value, dict):
        return clean_html(str(value.get("value") or ""))
    return ""


def normalize_title(value: str) -> str:
    value = value.strip()
    if value.startswith("http://") or value.startswith("https://"):
        path = unquote(urlparse(value).path)
        marker = "/wiki/"
        if marker not in path:
            raise SystemExit("URL do Commons precisa apontar para uma página File:")
        value = path.split(marker, 1)[1].replace("_", " ")
    if not value.lower().startswith("file:"):
        value = "File:" + value
    return value


def commons_query(title: str) -> dict:
    query = (
        f"{API}?action=query&format=json&formatversion=2&prop=imageinfo"
        f"&iiprop=url%7Csize%7Cmime%7Cextmetadata&titles={quote(title, safe='')}"
    )
    request = Request(query, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    pages = payload.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        raise SystemExit(f"Arquivo não encontrado no Wikimedia Commons: {title}")
    info = (pages[0].get("imageinfo") or [None])[0]
    if not info:
        raise SystemExit(f"Página encontrada sem imageinfo: {title}")
    return {"page": pages[0], "imageinfo": info}


def is_auto_approved_license(name: str) -> bool:
    upper = name.upper()
    if " NC" in upper or "-NC" in upper or " ND" in upper or "-ND" in upper:
        return False
    return any(marker in upper for marker in FREE_LICENSE_MARKERS)


def infer_capture_date(ext: dict) -> str | None:
    for key in ("DateTimeOriginal", "DateTime", "DateTimeDigitized"):
        value = metadata_value(ext, key)
        match = re.search(r"(\d{4})[-:](\d{2})[-:](\d{2})", value)
        if match:
            return "-".join(match.groups())
    return None


def float_metadata(ext: dict, key: str) -> float | None:
    raw = metadata_value(ext, key)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def safe_stem(title: str) -> str:
    value = title.split(":", 1)[-1]
    value = re.sub(r"\.[A-Za-z0-9]{2,5}$", "", value)
    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:100] or "commons-reference"


def extension_from_url(url: str, mime: str) -> str:
    suffix = Path(unquote(urlparse(url).path)).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/tiff": ".tif",
    }.get(mime, ".bin")


def download(url: str, target: Path, max_bytes: int) -> None:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response, target.open("wb") as output:
        length = response.headers.get("Content-Length")
        if length and int(length) > max_bytes:
            raise SystemExit(f"Arquivo excede limite configurado: {int(length):,} bytes")
        copied = 0
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            copied += len(block)
            if copied > max_bytes:
                raise SystemExit(f"Arquivo excede limite configurado: > {max_bytes:,} bytes")
            output.write(block)


def candidate_from_file(repo_root: Path, area: str, candidate_id: str) -> dict:
    path = repo_root / "world" / "areas" / area / "reference-candidates.json"
    data = load_json(path)
    if data.get("area_id") != area:
        raise SystemExit(f"area_id inconsistente em {path}")
    found = next((item for item in data.get("candidates", []) if item.get("candidate_id") == candidate_id), None)
    if not found:
        raise SystemExit(f"candidate_id inexistente: {candidate_id}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa referência do Wikimedia Commons para o acervo local.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--area", required=True)
    parser.add_argument("--candidate-id")
    parser.add_argument("--location")
    parser.add_argument("--title", help="File:... ou URL da página no Commons")
    parser.add_argument("--view")
    parser.add_argument("--media-root", type=Path, default=Path("world-reference"))
    parser.add_argument("--usage-class", default="REFERENCIA_INTERNA", choices=["PRODUCAO_APROVADA", "REFERENCIA_INTERNA", "TEMPORARIA"])
    parser.add_argument("--max-mb", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    media_root = args.media_root.expanduser()
    if not media_root.is_absolute():
        media_root = (repo_root / media_root).resolve()

    if args.candidate_id:
        candidate = candidate_from_file(repo_root, args.area, args.candidate_id)
        location = args.location or candidate["location_id"]
        title = normalize_title(args.title or candidate["file_title"])
        view = args.view or candidate["suggested_view"]
    else:
        if not (args.location and args.title and args.view):
            parser.error("sem --candidate-id, informe --location, --title e --view")
        location = args.location
        title = normalize_title(args.title)
        view = args.view

    result = commons_query(title)
    info = result["imageinfo"]
    ext = info.get("extmetadata") or {}
    original_url = info.get("url")
    description_url = info.get("descriptionurl") or f"https://commons.wikimedia.org/wiki/{quote(title.replace(' ', '_'))}"
    if not original_url:
        raise SystemExit("Wikimedia Commons não retornou URL do arquivo original")

    license_name = metadata_value(ext, "LicenseShortName") or metadata_value(ext, "UsageTerms")
    artist = metadata_value(ext, "Artist") or "autor não informado"
    credit = metadata_value(ext, "Credit")
    description = metadata_value(ext, "ImageDescription")
    license_url = metadata_value(ext, "LicenseUrl")
    capture_date = infer_capture_date(ext)
    lat = float_metadata(ext, "GPSLatitude")
    lon = float_metadata(ext, "GPSLongitude")

    license_verified = bool(license_name and is_auto_approved_license(license_name))
    if args.usage_class == "PRODUCAO_APROVADA" and not license_verified:
        raise SystemExit(
            f"Licença não está na allowlist automática para PRODUCAO_APROVADA: {license_name or 'ausente'}"
        )

    summary = {
        "title": title,
        "location_id": location,
        "view": view,
        "original_url": original_url,
        "description_url": description_url,
        "mime": info.get("mime"),
        "width": info.get("width"),
        "height": info.get("height"),
        "size": info.get("size"),
        "license": license_name or None,
        "license_url": license_url or None,
        "license_auto_verified": license_verified,
        "artist": artist,
        "credit": credit or None,
        "capture_date": capture_date,
        "lat": lat,
        "lon": lon,
        "description": description or None,
    }
    if args.dry_run:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    extension = extension_from_url(original_url, info.get("mime") or "")
    if extension == ".bin":
        raise SystemExit(f"Tipo de imagem não suportado: {info.get('mime')}")

    destination_dir = media_root / args.area / location
    destination_dir.mkdir(parents=True, exist_ok=True)
    final_path = destination_dir / f"{safe_stem(title)}{extension}"
    if final_path.exists():
        raise SystemExit(f"Destino já existe; não sobrescrevendo: {final_path}")

    with tempfile.TemporaryDirectory(prefix="boas-commons-") as temporary:
        downloaded = Path(temporary) / ("download" + extension)
        download(original_url, downloaded, max(1, args.max_mb) * 1024 * 1024)
        shutil.move(str(downloaded), final_path)

    command = [
        sys.executable,
        str(Path(__file__).with_name("register_media.py")),
        "--repo-root", str(repo_root),
        "--area", args.area,
        "--location", location,
        "--file", str(final_path),
        "--media-root", str(media_root),
        "--view", view,
        "--source-type", "licensed_photo",
        "--usage-class", args.usage_class,
        "--source-name", f"Wikimedia Commons — {artist}",
        "--license-status", "verified" if license_verified else "pending",
        "--source-url", description_url,
        "--notes", f"Commons title: {title}",
        "--notes", f"Original URL: {original_url}",
    ]
    if license_name:
        command += ["--license", license_name]
    if capture_date:
        command += ["--capture-date", capture_date]
    if lat is not None and lon is not None:
        command += ["--lat", str(lat), "--lon", str(lon)]
    if credit:
        command += ["--notes", f"Credit: {credit}"]
    if license_url:
        command += ["--notes", f"License URL: {license_url}"]
    command += ["--notes", f"Commons dimensions: {info.get('width')}x{info.get('height')}; mime={info.get('mime')}"]

    try:
        completed = subprocess.run(command, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        final_path.unlink(missing_ok=True)
        message = (exc.stderr or exc.stdout or str(exc)).strip()
        raise SystemExit(f"Falha ao registrar; download removido: {message}") from exc

    print(completed.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
