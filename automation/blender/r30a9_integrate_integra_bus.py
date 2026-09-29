from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector


REVISION = "R30A.9"
ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE_BLEND = ROOT / "blender" / "salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a8_ocean.blend"
OUTPUT_BLEND = ROOT / "blender" / "salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a9_integra_bus.blend"
REPORT_DIR = ROOT / "docs" / "reports" / "blender" / "r30a9"
REPORT_PATH = REPORT_DIR / "integra_bus_scene.json"

EXPECTED_GLB_SHA256 = "F3D5DEE69DCAB15379817A9AE13E562DF8023FD7AF38E8B6A0CDB4742AB650A2"
TARGET_LENGTH_M = 12.0
TARGET_WIDTH_M = 2.55
TARGET_HEIGHT_M = 3.25
ROOT_COLLECTION = "37 VEHICLES | INTEGRA SALVADOR R30A9"
SOURCE_COLLECTION = "37.1 SOURCE | INTEGRA SALVADOR"
ROOT_OBJECT = "R30A9 | BUS | INTEGRA SALVADOR 01"
ROAD_COLLECTION = "35 GAMEPLAY | ROAD GRAPH R30A7"


def fail(message: str) -> None:
    raise RuntimeError(f"{REVISION}: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def source_glb() -> Path:
    candidates: list[Path] = []
    env_path = os.environ.get("BOAS_INTEGRA_BUS_GLB")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(
        [
            ROOT / "artifacts" / "incoming" / "integra-salvador" / "yellow city bus 3d model.glb",
            ROOT / "artifacts" / "incoming" / "yellow city bus 3d model.glb",
        ]
    )

    for candidate in candidates:
        if not candidate.is_file():
            continue
        actual = sha256(candidate)
        if actual != EXPECTED_GLB_SHA256:
            fail(
                "arquivo GLB encontrado, mas o SHA-256 não corresponde ao asset aprovado "
                f"({candidate}; esperado={EXPECTED_GLB_SHA256}; atual={actual})"
            )
        return candidate.resolve()

    searched = "\n- ".join(str(p) for p in candidates)
    fail(
        "asset GLB não encontrado. Defina BOAS_INTEGRA_BUS_GLB ou coloque o arquivo em um "
        f"dos caminhos aprovados:\n- {searched}"
    )


def ensure_clean_expected_scene() -> None:
    if not bpy.data.filepath:
        fail("nenhum .blend está aberto")

    current = Path(bpy.data.filepath).resolve()
    if current != EXPECTED_SOURCE_BLEND.resolve():
        fail(
            "a revisão foi preparada exclusivamente para a cena oficial R30A.8. "
            f"Atual={current}; esperado={EXPECTED_SOURCE_BLEND}"
        )
    if bpy.data.is_dirty:
        fail("a cena possui alterações não salvas; crie checkpoint/salve antes de importar o ônibus")
    if OUTPUT_BLEND.exists():
        fail(f"a saída já existe; não sobrescrever automaticamente: {OUTPUT_BLEND}")
    if bpy.data.objects.get(ROOT_OBJECT) is not None:
        fail(f"o objeto {ROOT_OBJECT!r} já existe; não duplicar o asset")


def ensure_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    target_parent = parent or bpy.context.scene.collection
    if collection.name not in {c.name for c in target_parent.children}:
        target_parent.children.link(collection)
    return collection


def unlink_from_all_collections(obj: bpy.types.Object) -> None:
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points: list[Vector] = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    if not points:
        fail("o GLB não gerou meshes utilizáveis")
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def mesh_stats(objects: list[bpy.types.Object]) -> dict[str, int]:
    meshes = [obj for obj in objects if obj.type == "MESH"]
    return {
        "mesh_objects": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "polygons": sum(len(obj.data.polygons) for obj in meshes),
        "materials": len({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material}),
    }


def curve_segment_candidates() -> list[tuple[float, Vector, Vector, str]]:
    collection = bpy.data.collections.get(ROAD_COLLECTION)
    if collection is None:
        fail(f"coleção de vias não encontrada: {ROAD_COLLECTION!r}")

    candidates: list[tuple[float, Vector, Vector, str]] = []
    for obj in collection.all_objects:
        if obj.type != "CURVE" or not obj.name.startswith("R30A7 | ROAD |"):
            continue
        for spline in obj.data.splines:
            if spline.type == "BEZIER":
                coords = [obj.matrix_world @ p.co for p in spline.bezier_points]
            else:
                coords = [obj.matrix_world @ Vector((p.co.x, p.co.y, p.co.z)) for p in spline.points]
            for start, end in zip(coords, coords[1:]):
                direction = end - start
                horizontal = Vector((direction.x, direction.y, 0.0))
                if horizontal.length < 8.0:
                    continue
                midpoint = (start + end) * 0.5
                score = midpoint.x * midpoint.x + midpoint.y * midpoint.y
                candidates.append((score, start, end, obj.name))
    candidates.sort(key=lambda item: item[0])
    return candidates


def choose_staging_segment() -> tuple[Vector, Vector, str]:
    candidates = curve_segment_candidates()
    if not candidates:
        fail("nenhum segmento de via R30A.7 com comprimento suficiente foi encontrado")
    _, start, end, name = candidates[0]
    return start, end, name


def create_revision_text(source: Path, stats: dict[str, int], road_name: str) -> None:
    name = "R30A9_INTEGRA_BUS"
    text = bpy.data.texts.get(name) or bpy.data.texts.new(name)
    text.clear()
    text.write(
        "\n".join(
            [
                f"revision={REVISION}",
                "purpose=integração inicial do ônibus Integra Salvador como asset de veículo",
                f"source_glb_sha256={EXPECTED_GLB_SHA256}",
                f"source_glb_name={source.name}",
                f"collection={ROOT_COLLECTION}",
                f"root_object={ROOT_OBJECT}",
                f"staging_road={road_name}",
                "traffic_binding=candidate_only",
                "runtime_status=authoring_only_needs_lod_and_vehicle_rig",
                f"mesh_objects={stats['mesh_objects']}",
                f"vertices={stats['vertices']}",
                f"polygons={stats['polygons']}",
                "note=R30A.8 preservada; esta revisão não altera terreno, água, georreferenciamento ou grafo viário.",
            ]
        )
        + "\n"
    )


def main() -> None:
    ensure_clean_expected_scene()
    source = source_glb()

    before_names = set(bpy.data.objects.keys())
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = [obj for obj in bpy.data.objects if obj.name not in before_names]
    if not imported:
        fail("importação glTF não criou objetos")

    root_collection = ensure_collection(ROOT_COLLECTION)
    source_collection = ensure_collection(SOURCE_COLLECTION, parent=root_collection)

    top_level = [obj for obj in imported if obj.parent is None]
    bus_root = bpy.data.objects.new(ROOT_OBJECT, None)
    root_collection.objects.link(bus_root)

    for obj in imported:
        unlink_from_all_collections(obj)
        source_collection.objects.link(obj)
        obj["boas_revision"] = REVISION
        obj["boas_asset_id"] = "vehicle-integra-salvador-01"

    for obj in top_level:
        matrix_world = obj.matrix_world.copy()
        obj.parent = bus_root
        obj.matrix_world = matrix_world

    bpy.context.view_layer.update()

    minimum, maximum = world_bounds(imported)
    dimensions = maximum - minimum
    length_axis = max(range(3), key=lambda axis: dimensions[axis])

    if length_axis == 2:
        fail(
            "o maior eixo do ônibus veio no Z após importação; orientação inesperada. "
            "Abortando antes de deformar/rotacionar automaticamente."
        )

    width_axis = 1 if length_axis == 0 else 0
    if width_axis == 2:
        fail("não foi possível determinar largura horizontal do ônibus")

    if min(dimensions) <= 0:
        fail(f"bounding box inválida: {tuple(dimensions)}")

    target = [None, None, TARGET_HEIGHT_M]
    target[length_axis] = TARGET_LENGTH_M
    target[width_axis] = TARGET_WIDTH_M

    bus_root.scale = Vector(
        (
            target[0] / dimensions[0],
            target[1] / dimensions[1],
            target[2] / dimensions[2],
        )
    )

    start, end, road_name = choose_staging_segment()
    road_direction = end - start
    heading = math.atan2(road_direction.y, road_direction.x)
    bus_root.rotation_euler.z = heading if length_axis == 0 else heading - math.pi / 2.0

    bpy.context.view_layer.update()
    minimum, maximum = world_bounds(imported)
    center = (minimum + maximum) * 0.5
    road_midpoint = (start + end) * 0.5

    bus_root.location.x += road_midpoint.x - center.x
    bus_root.location.y += road_midpoint.y - center.y
    bus_root.location.z += road_midpoint.z - minimum.z + 0.05

    bpy.context.view_layer.update()
    minimum, maximum = world_bounds(imported)
    final_dimensions = maximum - minimum
    stats = mesh_stats(imported)

    bus_root["boas_revision"] = REVISION
    bus_root["boas_asset_id"] = "vehicle-integra-salvador-01"
    bus_root["boas_asset_type"] = "vehicle"
    bus_root["boas_vehicle_class"] = "urban_bus"
    bus_root["boas_source_sha256"] = EXPECTED_GLB_SHA256
    bus_root["boas_source_name"] = source.name
    bus_root["boas_traffic_binding"] = "candidate_only"
    bus_root["boas_placement"] = "road_graph_centerline_staging"
    bus_root["boas_runtime_status"] = "authoring_only_needs_lod_and_vehicle_rig"
    bus_root["boas_requires_visual_review"] = True
    bus_root["boas_requires_collision_proxy"] = True
    bus_root["boas_requires_wheel_rig"] = True
    bus_root["boas_source_polygons"] = stats["polygons"]

    create_revision_text(source, stats, road_name)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "bay-of-all-saints/r30a9-integra-bus-v1",
        "revision": REVISION,
        "source_blend": str(EXPECTED_SOURCE_BLEND),
        "output_blend": str(OUTPUT_BLEND),
        "source_glb_name": source.name,
        "source_glb_sha256": EXPECTED_GLB_SHA256,
        "collection": ROOT_COLLECTION,
        "root_object": ROOT_OBJECT,
        "staging_road": road_name,
        "placement_status": "candidate_centerline_staging",
        "traffic_binding": "candidate_only",
        "runtime_status": "authoring_only_needs_lod_and_vehicle_rig",
        "target_dimensions_m": {
            "length": TARGET_LENGTH_M,
            "width": TARGET_WIDTH_M,
            "height": TARGET_HEIGHT_M,
        },
        "final_bounds_m": {
            "min": [round(v, 6) for v in minimum],
            "max": [round(v, 6) for v in maximum],
            "dimensions": [round(v, 6) for v in final_dimensions],
        },
        "mesh_stats": stats,
        "validation_required": [
            "visual_review_multiview",
            "wheel_identification_and_rig",
            "lod_generation",
            "collision_proxy",
            "material_cleanup",
            "lane_level_traffic_placement",
        ],
        "notes": [
            "A R30A.8 permanece intacta.",
            "O ônibus é inicialmente posicionado no helper central do grafo viário apenas para revisão visual.",
            "O grafo R30A.7 não é lane graph final; o veículo não deve ser tratado como tráfego pronto.",
            "O GLB é pesado e não deve ser exportado diretamente para runtime antes de LOD/otimização.",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))

    digest = sha256(OUTPUT_BLEND)
    report["output_sha256"] = digest
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        {
            "revision": REVISION,
            "output_blend": str(OUTPUT_BLEND),
            "output_sha256": digest,
            "root_object": ROOT_OBJECT,
            "staging_road": road_name,
            "mesh_stats": stats,
            "final_dimensions": [round(v, 4) for v in final_dimensions],
        }
    )


if __name__ == "__main__":
    main()
