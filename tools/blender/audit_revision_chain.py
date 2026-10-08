"""Auditoria read-only da cadeia autoral Blender, sem escolher arquivos por nome/data.

A trilha é obtida exclusivamente do ponteiro authoring_source e de parent_file.
Cenas antigas, alternativas ou rejeitadas não são promovidas nem apagadas.
"""
import argparse
import json
import re
from pathlib import Path

from tools.blender.audit_authoring_inventory import (
    AREA, LFS_HEADER, file_digest, safe_path, tracked_paths,
)

_SHA = re.compile(r"^[a-f0-9]{64}$")


def audit_chain(root, *, verify_sha=False, require_tracked=False):
    root = Path(root).resolve()
    catalog = json.loads((root / AREA / "blender-revisions.json").read_text(encoding="utf-8"))
    production = json.loads((root / AREA / "production.json").read_text(encoding="utf-8"))
    if catalog.get("production_source_reference") != "production.json#/world_source":
        raise ValueError("Autoridade de produção divergente")
    if catalog.get("selection_policy") != "explicit_pointer_never_filename_mtime_or_open_window":
        raise ValueError("Seleção da fonte autoral não explícita")

    entries = catalog.get("revisions")
    if not isinstance(entries, list):
        raise ValueError("Catálogo de revisões inválido")
    errors, warnings = [], []
    by_path = {}
    for i, item in enumerate(entries):
        if not isinstance(item, dict):
            errors.append(f"revisions[{i}]: entrada inválida")
            continue
        name = item.get("file")
        try:
            safe_path(root, name)
        except ValueError as exc:
            errors.append(f"revisions[{i}]: {exc}")
            continue
        if name in by_path:
            errors.append(f"revisions[{i}]: duplicidade de caminho {name}")
        else:
            by_path[name] = item

    head = catalog.get("authoring_source")
    if not isinstance(head, dict) or not head.get("file"):
        raise ValueError("Ponteiro de autoria ausente")
    tracked = tracked_paths(root)
    seen = set()
    records = []
    current = head
    while current is not None:
        key = current.get("file")
        if not isinstance(key, str) or key in seen:
            errors.append(f"Genealogia circular ou arquivo inválido: {key}")
            break
        seen.add(key)
        record = {
            "file": key,
            "revision": current.get("revision"),
            "status": current.get("status"),
            "parent_file": current.get("parent_file"),
            "evidence": current.get("evidence"),
            "production_ready": current.get("production_ready") is True,
            "problems": [],
            "warnings": [],
        }
        records.append(record)
        try:
            path = safe_path(root, key)
        except ValueError as exc:
            record["problems"].append(str(exc))
            break
        if path.suffix.lower() != ".blend":
            record["problems"].append("Fonte não é .blend")
        if not path.is_file():
            record["problems"].append("Fonte ausente")
        else:
            record["size_bytes"] = path.stat().st_size
            with path.open("rb") as f:
                if f.read(len(LFS_HEADER)) == LFS_HEADER:
                    record["problems"].append("Ponteiro LFS sem conteúdo .blend")
            expected = current.get("sha256")
            if not isinstance(expected, str) or not _SHA.fullmatch(expected):
                record["problems"].append("SHA-256 não declarado ou inválido")
            elif verify_sha and not record["problems"]:
                record["sha256_matches"] = file_digest(path) == expected
                if not record["sha256_matches"]:
                    record["problems"].append("SHA-256 divergente")
        if key not in tracked:
            record["warnings"].append("Fonte fora do Git")
        evidence = current.get("evidence")
        if evidence:
            try:
                ev = safe_path(root, evidence)
                if not ev.is_file():
                    record["problems"].append("Evidência ausente")
                elif evidence not in tracked:
                    record["warnings"].append("Evidência fora do Git")
            except ValueError:
                record["problems"].append("Caminho de evidência inseguro")
        else:
            record["warnings"].append("Evidência não declarada")
        if current.get("status") == "rejected_experiment":
            record["problems"].append("Ramo rejeitado em cadeia ativa")
        if current.get("production_ready") is True:
            record["warnings"].append("Marcado como production_ready; aprovação não auditada")

        declared = by_path.get(key)
        if declared is None:
            record["problems"].append("Revisão não catalogada no histórico")
        elif any(declared.get(field) != current.get(field)
                 for field in ("sha256", "parent_file", "revision")):
            record["problems"].append("Ponteiro diverge do histórico")
        parent = current.get("parent_file")
        if parent is None:
            break
        try:
            safe_path(root, parent)
        except ValueError:
            record["problems"].append("Caminho ancestral inseguro")
            break
        if parent not in by_path:
            record["problems"].append("Ancestral ausente no catálogo")
            break
        current = by_path[parent]

    for record in records:
        errors.extend(f"{record['revision']}:{v}" for v in record["problems"])
        warnings.extend(f"{record['revision']}:{v}" for v in record["warnings"])
    if require_tracked and any("fora do Git" in w for w in warnings):
        errors.append("Falha de consolidação: fontes/evidências não versionadas")
    return {
        "schema": "boas/authoring-chain-audit-v1",
        "head": head["file"],
        "production_file": production["world_source"]["file"],
        "production_unchanged": head["file"] != production["world_source"]["file"],
        "revisions_in_catalog": len(entries),
        "ancestry_count": len(records),
        "source_bytes": sum(record.get("size_bytes", 0) for record in records),
        "validated_sha256": sum("sha256_matches" in r for r in records),
        "source_untracked": sum("Fonte fora do Git" in r["warnings"] for r in records),
        "evidence_untracked": sum("Evidência fora do Git" in r["warnings"] for r in records),
        "errors": errors, "warnings": warnings, "records": records,
        "passed": not errors and head["file"] != production["world_source"]["file"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-sha", action="store_true", help="SHA-256 de todas as fontes ancestrais, pode ler vários GB")
    parser.add_argument("--require-tracked", action="store_true", help="Não permite fontes/evidências fora do Git")
    parser.add_argument("--report", type=Path, help="Arquivo JSON de diagnóstico, externo ao contrato SSOT")
    parser.add_argument("--summary", action="store_true", help="Oculta a lista extensa de objetos")
    args = parser.parse_args()
    result = audit_chain(args.root, verify_sha=args.verify_sha, require_tracked=args.require_tracked)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        output = args.report.with_suffix(args.report.suffix + ".tmp")
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        output.replace(args.report)
    visible = {k:v for k,v in result.items() if k not in ("records", "warnings")} if args.summary else result
    print(json.dumps(visible, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()
