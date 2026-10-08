"""Auditoria read-only das fontes oficiais de autoria e produção.

Nunca escolhe revisão pelo nome, data de modificação ou janela do Blender.
NUNCA altera .blend, manifesta aprovação de gameplay ou modifica contratos.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

AREA = "world/areas/mvp-centro-lacerda"
HASH_RE = re.compile(r"^[a-f0-9]{64}$")
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"


def safe_path(root, value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Caminho de fonte inválido")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise ValueError(f"Caminho de fonte inseguro: {value}")
    candidate = (root / value).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ValueError("Fonte aponta para fora do repositório")
    return candidate


def file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tracked_paths(root):
    proc = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                          capture_output=True, check=True)
    return set(v.decode("utf-8") for v in proc.stdout.split(b"\0") if v)


def file_record(root, entry, tracked, *, digest=True):
    record = {"file": entry.get("file"), "revision": entry.get("revision"),
              "issues": [], "warnings": []}
    try:
        path = safe_path(root, entry.get("file"))
    except ValueError as exc:
        record["issues"].append(str(exc))
        return record
    relative = path.relative_to(root.resolve()).as_posix()
    if not path.is_file():
        record["issues"].append("arquivo_ausente")
        return record
    record["bytes"] = path.stat().st_size
    if relative not in tracked:
        record["warnings"].append("nao_versionado_git")
    expected = entry.get("sha256")
    if not isinstance(expected, str) or not HASH_RE.fullmatch(expected):
        record["issues"].append("sha256_nao_declarado")
    with path.open("rb") as stream:
        if stream.read(len(LFS_HEADER)) == LFS_HEADER:
            record["issues"].append("somente_ponteiro_lfs")
            return record
    if digest and isinstance(expected, str) and HASH_RE.fullmatch(expected):
        record["sha256_verified"] = file_digest(path) == expected
        if not record["sha256_verified"]:
            record["issues"].append("sha256_divergente")
    return record


def audit(root, *, require_tracked=False):
    root = Path(root).resolve()
    sources = json.loads((root / AREA / "blender-revisions.json").read_text(encoding="utf-8"))
    contract = json.loads((root / AREA / "production.json").read_text(encoding="utf-8"))
    if sources.get("production_source_reference") != "production.json#/world_source":
        raise ValueError("Catálogo desconectado do SSOT de produção")
    if sources.get("selection_policy") != "explicit_pointer_never_filename_mtime_or_open_window":
        raise ValueError("A escolha de revisão não é explícita")
    tracked = tracked_paths(root)
    authoring = sources["authoring_source"]
    production = contract["world_source"]
    result = {"schema": "boas/authoring-audit-v1", "area_id": contract["area_id"],
              "production_revision": production["revision"],
              "authoring_revision": authoring["revision"],
              "production_ready": bool(authoring.get("production_ready", False)),
              "records": {}}
    for kind, entry in (("authoring", authoring), ("production", production)):
        record = file_record(root, entry, tracked)
        if kind == "authoring":
            for field in ("parent_file", "evidence"):
                value = entry.get(field)
                try:
                    item = safe_path(root, value)
                    if not item.is_file():
                        record["issues"].append(field + "_ausente")
                    elif item.relative_to(root).as_posix() not in tracked:
                        record["warnings"].append(field + "_nao_versionado_git")
                except ValueError:
                    record["issues"].append(field + "_invalido")
        result["records"][kind] = record
    result["issues"] = [f"{kind}:{issue}" for kind, obj in result["records"].items()
                        for issue in obj["issues"]]
    result["warnings"] = [f"{kind}:{warning}" for kind, obj in result["records"].items()
                          for warning in obj["warnings"]]
    if authoring.get("file") == production.get("file") and not authoring.get("production_ready"):
        result["issues"].append("fonte_nao_aprovada_e_igual_a_producao")
    if require_tracked and result["warnings"]:
        result["issues"].append("fontes_ou_evidencias_fora_do_git")
    result["passed"] = not result["issues"]
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    cli.add_argument("--require-tracked", action="store_true",
                     help="Falha se fontes, parent ou evidência ainda não estiverem no Git")
    args = cli.parse_args()
    result = audit(args.root, require_tracked=args.require_tracked)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()
