# Bay of All Saints — revisão R30A de pré-flight não destrutiva
# Uso:
# blender cena_r27.blend --factory-startup --background \
#   --python tools/blender/r30a_preflight.py -- \
#   --save-as cena_r30a_preflight.blend

from __future__ import annotations

import argparse
import os
import sys

import bpy


CAPTURE_ID = "aleph-20260924T205631Z-aqqo7pkx"
TEXT_NAME = "R30A_PREFLIGHT"


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-as", required=True)
    return parser.parse_args(argv)


def main():
    args = parse_args()
    scene = bpy.context.scene

    report = """R30A — PRÉ-FLIGHT NÃO DESTRUTIVO

Status: BLOQUEADA — captura Aleph histórica não recuperada nesta estação.

Captura esperada: aleph-20260924T205631Z-aqqo7pkx
Referência registrada na cena: data/aleph/aleph-20260924T205631Z-aqqo7pkx/map.osm

Nenhuma geometria, material, coleção de gameplay ou Hero asset foi alterado
nesta revisão. O arquivo é uma cópia de trabalho com metadados de pre-flight
para preservar o estado R27 enquanto aguardamos manifest.json, map.osm e
terrain.tif correspondentes.

Não promover transformação OSM → Blender, fit vertical, referência estrutural
ou correção de terreno sem esses dados-fonte.
"""

    text = bpy.data.texts.get(TEXT_NAME) or bpy.data.texts.new(TEXT_NAME)
    text.clear()
    text.write(report)

    scene["boas_r30a_revision"] = "R30A_PREFLIGHT"
    scene["boas_r30a_status"] = "blocked_pending_historical_capture"
    scene["boas_r30a_capture_id"] = CAPTURE_ID
    scene["boas_r30a_geometry_changed"] = False
    scene["boas_r30a_structural_reference_loaded"] = False

    target = os.path.abspath(args.save_as)
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=target)
    print(f"[r30a] pre-flight salvo em: {target}")
    print("[r30a] geometria alterada: não")
    print(f"[r30a] objetos: {len(bpy.data.objects)} | meshes: {len(bpy.data.meshes)}")


if __name__ == "__main__":
    main()
