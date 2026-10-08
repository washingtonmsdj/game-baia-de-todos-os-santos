"""Valida a exportação do veículo antes de distribuí-la ao runtime.

O arquivo de staging não é autoridade; só o contrato da fonte e o
manifesto ligado ao hash do GLB podem autorizar o empacotamento.
"""
import json
import struct
from pathlib import Path

from tools.runtime.production import sha256


def inspect_vehicle_glb(path, expected_scene):
    path = Path(path)
    with path.open("rb") as stream:
        header = stream.read(20)
        if len(header) != 20:
            raise ValueError("GLB veículo truncado")
        magic, version, size, json_size, json_kind = struct.unpack("<IIIII", header)
        if (magic, version, json_kind) != (0x46546C67, 2, 0x4E4F534A):
            raise ValueError("Cabeçalho GLB veículo inválido")
        if size != path.stat().st_size or json_size == 0 or json_size % 4:
            raise ValueError("GLB veículo com comprimento inválido")
        document = json.loads(stream.read(json_size))
        tail = stream.read(8)
        if len(tail) != 8:
            raise ValueError("BIN do veículo ausente")
        bin_size, bin_kind = struct.unpack("<II", tail)
        if bin_kind != 0x004E4942 or size != 28 + json_size + bin_size:
            raise ValueError("BIN do veículo inválido")
    scenes = document.get("scenes", [])
    if len(scenes) != 1 or document.get("scene", 0) != 0:
        raise ValueError("GLB veículo contém cenas adicionais ou ativa outra cena")
    if scenes[0].get("name") != expected_scene:
        raise ValueError("Cena do GLB diverge do contrato do veículo")
    nodes = document.get("nodes", [])
    if not scenes[0].get("nodes") or not nodes:
        raise ValueError("Cena exportada do veículo vazia")
    if document.get("cameras") or "KHR_lights_punctual" in document.get("extensionsUsed", []):
        raise ValueError("Exportação de veículo contém câmeras ou luzes")
    if any("estudio" in item.get("name", "").casefold()
           or "estúdio" in item.get("name", "").casefold()
           or "apresentacao" in item.get("name", "").casefold()
           for item in nodes):
        raise ValueError("GLB veículo contém elementos do estúdio")
    return {"scene_name": expected_scene, "node_count": len(nodes), "scene_count": 1}


def validate_vehicle_staging(glb_path, vehicle):
    path = Path(glb_path)
    manifest_path = path.with_suffix(".json")
    if not manifest_path.is_file():
        raise ValueError("Manifesto de exportação do veículo ausente; reexportação canônica necessária")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = vehicle["source"]
    expected = {
        "schema": "boas/vehicle-export-v1",
        "vehicle_id": vehicle["id"],
        "source_file": source["file"],
        "source_sha256": source["sha256"],
        "source_scene": source["scene"],
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"Proveniência do ônibus divergente: {key}")
    digest = sha256(path)
    if manifest.get("export_sha256") != digest:
        raise ValueError("GLB do ônibus foi alterado após a exportação")
    selected = manifest.get("selected_objects")
    if not isinstance(selected, list) or not selected or len(set(selected)) != len(selected):
        raise ValueError("Inventário de objetos do ônibus ausente ou duplicado")
    if not all(isinstance(name, str) and name.startswith(("BUS02 | ", "BUS03 | "))
               and "estudio" not in name.casefold() and "estúdio" not in name.casefold()
               for name in selected):
        raise ValueError("Objetos fora do ônibus no inventário de exportação")
    inspected = inspect_vehicle_glb(path, source["scene"])
    if manifest.get("scene_count") != inspected["scene_count"]:
        raise ValueError("Contagem de cenas do veículo adulterada")
    return {**inspected, "export_sha256": digest, "selected_object_count": len(selected)}
