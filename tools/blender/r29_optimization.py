# Bay of All Saints / Salvador MVP — Revisão R29
# Otimização conservadora de meshes idênticas e geração de candidatos de LOD/colisão.
# Uso:
#   blender cena_r28.blend --python tools/blender/r29_optimization.py
#   blender cena_r28.blend --python tools/blender/r29_optimization.py -- --apply-exact
#
# Sem --apply-exact o script funciona em modo de auditoria e NÃO religa datablocks de mesh.

import bpy
import hashlib
import json
import math
import os
import re
import struct
import sys
from collections import Counter, defaultdict

REV = "R29"
TEXT_REPORT = "R29_OPTIMIZATION_REPORT"
TEXT_DUPES = "R29_EXACT_DUPLICATE_CANDIDATES"
TEXT_LOD = "R29_LOD_COLLISION_CANDIDATES"
PROTECTED_CLASSES = {"HERO", "GAMEPLAY"}
R28_CLASS_PROP = "allsaints_r28_class"
APPLY_EXACT = "--apply-exact" in sys.argv
CHUNK_SIZE = 128.0

SUPPORTED_ATTR_PROPS = {
    "FLOAT": ("value", 1),
    "INT": ("value", 1),
    "BOOLEAN": ("value", 1),
    "FLOAT_VECTOR": ("vector", 3),
    "FLOAT_COLOR": ("color", 4),
    "BYTE_COLOR": ("color", 4),
    "INT8": ("value", 1),
    "FLOAT2": ("vector", 2),
}


def write_num(h, value):
    if isinstance(value, bool):
        h.update(b"\x01" if value else b"\x00")
    elif isinstance(value, int):
        h.update(struct.pack("<q", value))
    else:
        h.update(struct.pack("<d", float(value)))


def write_text(h, value):
    data = str(value).encode("utf-8", "surrogatepass")
    h.update(struct.pack("<I", len(data)))
    h.update(data)


def write_seq(h, values):
    for value in values:
        write_num(h, value)


def mesh_user_classes(mesh):
    classes = set()
    names = []
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.data == mesh:
            classes.add(str(obj.get(R28_CLASS_PROP, "")))
            names.append(obj.name)
    return classes, names


def mesh_is_eligible(mesh):
    classes, users = mesh_user_classes(mesh)

    if not users:
        return False, "sem objetos usuários"
    if not classes or "" in classes:
        return False, "objeto sem classificação R28"
    if classes & PROTECTED_CLASSES:
        return False, "usado por HERO/GAMEPLAY"
    if mesh.shape_keys is not None:
        return False, "shape keys"
    if getattr(mesh, "animation_data", None) is not None:
        return False, "animation_data no mesh"
    if getattr(mesh, "use_fake_user", False):
        return False, "fake user"

    custom_keys = [k for k in mesh.keys() if k != "_RNA_UI"]
    if custom_keys:
        return False, "custom properties no mesh"

    for attr in mesh.attributes:
        if attr.data_type not in SUPPORTED_ATTR_PROPS:
            return False, f"atributo não suportado: {attr.name}/{attr.data_type}"

    return True, ""


def coarse_key(mesh):
    material_names = tuple(slot.name if slot else "" for slot in mesh.materials)
    uv_names = tuple(layer.name for layer in mesh.uv_layers)
    color_meta = tuple((a.name, a.domain, a.data_type) for a in mesh.color_attributes)
    attr_meta = tuple((a.name, a.domain, a.data_type) for a in mesh.attributes)

    return (
        len(mesh.vertices),
        len(mesh.edges),
        len(mesh.loops),
        len(mesh.polygons),
        material_names,
        uv_names,
        color_meta,
        attr_meta,
    )


def update_attribute_digest(h, attr):
    prop, width = SUPPORTED_ATTR_PROPS[attr.data_type]
    write_text(h, attr.name)
    write_text(h, attr.domain)
    write_text(h, attr.data_type)
    h.update(struct.pack("<I", len(attr.data)))

    for item in attr.data:
        value = getattr(item, prop)
        if width == 1:
            write_num(h, value)
        else:
            write_seq(h, value[:width])


def mesh_digest(mesh):
    h = hashlib.sha256()
    write_text(h, "mesh-content-v1")

    h.update(
        struct.pack(
            "<IIII",
            len(mesh.vertices),
            len(mesh.edges),
            len(mesh.loops),
            len(mesh.polygons),
        )
    )

    for v in mesh.vertices:
        write_seq(h, v.co)

    for e in mesh.edges:
        write_num(h, e.vertices[0])
        write_num(h, e.vertices[1])
        write_num(h, bool(e.use_edge_sharp))
        write_num(h, bool(e.use_seam))

    for loop in mesh.loops:
        write_num(h, loop.vertex_index)
        write_num(h, loop.edge_index)

    for poly in mesh.polygons:
        write_num(h, poly.loop_start)
        write_num(h, poly.loop_total)
        write_num(h, poly.material_index)
        write_num(h, bool(poly.use_smooth))

    write_num(h, len(mesh.materials))
    for slot in mesh.materials:
        write_text(h, slot.name if slot else "")

    write_num(h, len(mesh.uv_layers))
    for layer in mesh.uv_layers:
        write_text(h, layer.name)
        write_num(h, bool(layer.active))
        write_num(h, bool(layer.active_render))
        h.update(struct.pack("<I", len(layer.data)))
        for item in layer.data:
            write_seq(h, item.uv)

    write_num(h, len(mesh.attributes))
    for attr in mesh.attributes:
        update_attribute_digest(h, attr)

    return h.hexdigest()


def find_exact_groups():
    eligible = []
    skipped = Counter()

    for mesh in bpy.data.meshes:
        ok, reason = mesh_is_eligible(mesh)
        if ok:
            eligible.append(mesh)
        else:
            skipped[reason] += 1

    buckets = defaultdict(list)
    for mesh in eligible:
        buckets[coarse_key(mesh)].append(mesh)

    digest_groups = defaultdict(list)
    for bucket in buckets.values():
        if len(bucket) < 2:
            continue
        for mesh in bucket:
            digest_groups[mesh_digest(mesh)].append(mesh)

    groups = [group for group in digest_groups.values() if len(group) >= 2]
    groups.sort(key=lambda group: (-len(group), group[0].name))
    return groups, skipped


def canonical_mesh(group):
    return sorted(group, key=lambda mesh: (-mesh.users, mesh.name))[0]


def apply_exact_groups(groups):
    changed_objects = []
    orphaned_duplicates = 0

    for group in groups:
        canonical = canonical_mesh(group)
        duplicates = [mesh for mesh in group if mesh != canonical]

        for duplicate in duplicates:
            users = [
                obj
                for obj in bpy.data.objects
                if obj.type == "MESH" and obj.data == duplicate
            ]
            for obj in users:
                if str(obj.get(R28_CLASS_PROP, "")) in PROTECTED_CLASSES:
                    continue
                obj.data = canonical
                obj["allsaints_r29_deduplicated"] = True
                obj["allsaints_r29_canonical_mesh"] = canonical.name
                changed_objects.append(obj.name)

            if duplicate.users == 0:
                orphaned_duplicates += 1

    return changed_objects, orphaned_duplicates


def object_poly_count(obj):
    if obj.type != "MESH" or not obj.data:
        return 0
    return len(obj.data.polygons)


def collect_lod_collision_candidates():
    lod = []
    collision = []

    for obj in bpy.data.objects:
        if obj.type != "MESH" or not obj.data:
            continue

        cls = str(obj.get(R28_CLASS_PROP, ""))
        if not cls:
            continue

        polys = object_poly_count(obj)
        dims = tuple(round(abs(v), 3) for v in obj.dimensions)

        if cls == "HERO" and polys >= 5000:
            lod.append((polys, obj.name, cls, dims, "LOD manual prioritário"))
        elif cls == "ENVIRONMENT" and polys >= 2500:
            lod.append((polys, obj.name, cls, dims, "candidato a LOD1/LOD2"))
        elif cls == "DECOR" and polys >= 1200:
            lod.append((polys, obj.name, cls, dims, "avaliar simplificação/instância"))

        if cls in {"ROADS", "TERRAIN", "ENVIRONMENT"} and polys >= 1500:
            collision.append(
                (polys, obj.name, cls, dims, "candidato a colisão simplificada")
            )

    lod.sort(reverse=True)
    collision.sort(reverse=True)
    return lod, collision


def collect_chunk_stats():
    cells = defaultdict(lambda: Counter(objects=0, polygons=0))

    for obj in bpy.data.objects:
        if obj.type != "MESH" or not obj.data:
            continue

        cls = str(obj.get(R28_CLASS_PROP, ""))
        if cls not in {"ROADS", "TERRAIN", "ENVIRONMENT", "DECOR"}:
            continue

        x = obj.matrix_world.translation.x
        y = obj.matrix_world.translation.y
        cx = math.floor(x / CHUNK_SIZE)
        cy = math.floor(y / CHUNK_SIZE)

        cells[(cx, cy)]["objects"] += 1
        cells[(cx, cy)]["polygons"] += len(obj.data.polygons)

    rows = [
        (stats["polygons"], stats["objects"], cx, cy)
        for (cx, cy), stats in cells.items()
    ]
    rows.sort(reverse=True)
    return rows


def write_duplicate_report(groups, skipped):
    text = bpy.data.texts.get(TEXT_DUPES) or bpy.data.texts.new(TEXT_DUPES)
    text.clear()

    lines = [
        "BAY OF ALL SAINTS — R29 — CANDIDATOS DE MESH EXATAMENTE IDÊNTICA\n\n",
        f"Modo: {'APLICAÇÃO EXATA' if APPLY_EXACT else 'AUDITORIA'}\n",
        f"Grupos elegíveis idênticos: {len(groups)}\n\n",
        "CRITÉRIO\n",
        "- mesma geometria, topologia, ordem de materiais, UVs e atributos suportados;\n",
        "- sem shape keys, animation_data ou custom properties no mesh;\n",
        "- nenhum usuário classificado como HERO ou GAMEPLAY;\n",
        "- equivalência não é inferida pelo nome do objeto.\n\n",
        "IGNORADOS POR SEGURANÇA\n",
    ]

    for reason, count in skipped.most_common():
        lines.append(f"- {reason}: {count}\n")

    lines.append("\nGRUPOS\n")
    for index, group in enumerate(groups, start=1):
        canonical = canonical_mesh(group)
        lines.append(
            f"\n[{index}] canonical={canonical.name} | meshes={len(group)}\n"
        )

        for mesh in group[:50]:
            classes, users = mesh_user_classes(mesh)
            lines.append(
                f"  - {mesh.name} | users={mesh.users} | "
                f"classes={sorted(classes)} | objects={users[:8]}\n"
            )

        if len(group) > 50:
            lines.append(f"  ... +{len(group) - 50} meshes\n")

    text.write("".join(lines))


def write_lod_report(lod, collision, chunks):
    text = bpy.data.texts.get(TEXT_LOD) or bpy.data.texts.new(TEXT_LOD)
    text.clear()

    lines = [
        "BAY OF ALL SAINTS — R29 — CANDIDATOS DE LOD, COLISÃO E CHUNKS\n\n",
        "Nenhuma simplificação é aplicada automaticamente nesta revisão.\n\n",
        "TOP CANDIDATOS DE LOD\n",
    ]

    for polys, name, cls, dims, note in lod[:100]:
        lines.append(
            f"- {polys:>8,} polys | {cls:<11} | {name} | "
            f"dims={dims} | {note}\n"
        )

    lines.append("\nTOP CANDIDATOS DE COLISÃO SIMPLIFICADA\n")
    for polys, name, cls, dims, note in collision[:100]:
        lines.append(
            f"- {polys:>8,} polys | {cls:<11} | {name} | "
            f"dims={dims} | {note}\n"
        )

    lines.append(f"\nCHUNKS DE REFERÊNCIA ({CHUNK_SIZE:.0f} m)\n")
    for polys, objects, cx, cy in chunks[:100]:
        min_x = cx * CHUNK_SIZE
        min_y = cy * CHUNK_SIZE
        lines.append(
            f"- célula ({cx},{cy}) origem=({min_x:.1f},{min_y:.1f}) | "
            f"objetos={objects:,} | polys={polys:,}\n"
        )

    text.write("".join(lines))


def revision_output_path(source_path):
    if not source_path:
        return os.path.join(
            os.path.expanduser("~"),
            "bay_of_all_saints_mvp_r29.blend",
        )

    root, ext = os.path.splitext(source_path)
    root = re.sub(r"_r\d+$", "", root, flags=re.IGNORECASE)
    return root + "_r29" + (ext or ".blend")


def main():
    scene = bpy.context.scene

    r28_count = sum(
        1 for obj in bpy.data.objects if obj.get(R28_CLASS_PROP)
    )
    if r28_count == 0:
        raise RuntimeError(
            "R29 exige a classificação da R28. "
            "Execute r28_gameplay_export.py e valide a cena antes."
        )

    before = {
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        "mesh_object_links": sum(
            1
            for obj in bpy.data.objects
            if obj.type == "MESH" and obj.data
        ),
        "r28_classified_objects": r28_count,
    }

    groups, skipped = find_exact_groups()
    write_duplicate_report(groups, skipped)

    changed_objects = []
    orphaned_duplicates = 0
    if APPLY_EXACT:
        changed_objects, orphaned_duplicates = apply_exact_groups(groups)

    lod, collision = collect_lod_collision_candidates()
    chunks = collect_chunk_stats()
    write_lod_report(lod, collision, chunks)

    after = {
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        "changed_objects": len(changed_objects),
        "duplicate_meshes_now_orphaned": orphaned_duplicates,
        "exact_duplicate_groups": len(groups),
        "lod_candidates": len(lod),
        "collision_candidates": len(collision),
        "chunk_cells": len(chunks),
    }

    report = bpy.data.texts.get(TEXT_REPORT) or bpy.data.texts.new(TEXT_REPORT)
    report.clear()
    report.write(
        "BAY OF ALL SAINTS — RELATÓRIO R29\n\n"
        + f"Modo: {'APLICAÇÃO EXATA' if APPLY_EXACT else 'AUDITORIA'}\n\n"
        + "ANTES\n"
        + json.dumps(before, ensure_ascii=False, indent=2)
        + "\n\nDEPOIS\n"
        + json.dumps(after, ensure_ascii=False, indent=2)
        + "\n\nSEGURANÇA\n"
        + "- HERO/GAMEPLAY não são relinkados automaticamente.\n"
        + "- nenhuma mesh é unida, decimada, triangulada ou apagada explicitamente.\n"
        + "- sem --apply-exact, nenhuma referência de obj.data é alterada.\n"
        + "- LOD, colisão e chunks são apenas candidatos para a próxima revisão.\n"
    )

    scene["allsaints_r29_status"] = (
        "exact mesh dedup applied" if APPLY_EXACT else "audit only"
    )
    scene["allsaints_r29_changed_objects"] = len(changed_objects)
    scene["allsaints_r29_exact_groups"] = len(groups)

    output = revision_output_path(bpy.data.filepath)
    bpy.ops.wm.save_as_mainfile(filepath=output)

    print(
        "[R29] Modo:",
        "APLICAÇÃO EXATA" if APPLY_EXACT else "AUDITORIA",
    )
    print("[R29] Grupos exatos:", len(groups))
    print("[R29] Objetos relinkados:", len(changed_objects))
    print("[R29] Salvo:", output)


if __name__ == "__main__":
    main()
