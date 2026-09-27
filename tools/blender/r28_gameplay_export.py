# All Saints / Salvador MVP — Revisão R28
# Passe não destrutivo de guias de gameplay, classificação de exportação e auditoria.
# Compatibilidade pretendida: Blender 4.x / 5.x.
# Uso:
#   blender cena_atual.blend --python tools/blender/r28_gameplay_export.py

import bpy
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

REV = "R28"
PREFIX = "R28 | "
ROOT_GAMEPLAY = "32 MVP | GAMEPLAY R28"
ROUTE_COLLECTION = "32A GAMEPLAY | ROTA R28"
ZONE_COLLECTION = "32B GAMEPLAY | ZONAS R28"
ROOT_EXPORT = "33 EXPORT | R28"
EXPORT_CLASSES = ["HERO", "GAMEPLAY", "TERRAIN", "ROADS", "DECOR", "PROXY_OSM", "ENVIRONMENT"]
TEXT_README = "R28_README"
TEXT_AUDIT = "R28_PERFORMANCE_AUDIT"

# Pontos derivados de checkpoints já presentes na cena analisada.
# São guias de design/gameplay, não coordenadas de levantamento topográfico certificado.
ROUTE_SEGMENTS = [
    ("ROTA ALTA", [
        (-5.66, -0.67, 70.32),
        (-18.00, 12.00, 70.25),
        (-35.43, 39.07, 70.10),
        (-46.05, 51.32, 71.45),
    ]),
    ("EIXO ELEVADOR", [
        (-46.05, 51.32, 71.45),
        (-47.20, 50.20, 42.00),
        (-48.33, 49.00, 12.45),
    ]),
    ("ROTA BAIXA", [
        (-48.33, 49.00, 12.45),
        (-57.47, 59.75, 7.41),
        (-82.00, 93.00, 9.00),
        (-105.00, 125.00, 10.00),
        (-126.49, 154.29, 10.50),
        (-148.95, 172.78, 14.26),
    ]),
]

ZONES = [
    ("ENTRADA SUPERIOR", (-5.66, -0.67, 70.32), (10.0, 10.0, 5.0), "spawn / entrada"),
    ("PASSARELA", (-35.43, 39.07, 70.10), (12.0, 8.0, 5.0), "transicao / passarela"),
    ("CABINES SUPERIORES", (-46.05, 51.32, 71.45), (9.0, 9.0, 6.0), "interacao do elevador"),
    ("CABINES INFERIORES", (-48.33, 49.00, 12.45), (9.0, 9.0, 6.0), "interacao do elevador"),
    ("SAIDA INFERIOR", (-57.47, 59.75, 7.41), (12.0, 10.0, 5.0), "entrada na Cidade Baixa"),
    ("PRACA CAIRU", (-126.49, 154.29, 10.50), (42.0, 42.0, 8.0), "hub externo"),
    ("MERCADO MODELO", (-148.95, 172.78, 14.26), (46.0, 42.0, 14.0), "POI / interior"),
]


def norm(text):
    value = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in value if not unicodedata.combining(c)).upper()


def get_or_create_collection(name, parent=None):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)

    target = bpy.context.scene.collection if parent is None else parent
    if collection.name not in target.children:
        try:
            target.children.link(collection)
        except RuntimeError:
            pass
    return collection


def remove_generated():
    for obj in list(bpy.data.objects):
        if obj.name.startswith(PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)
    for curve in list(bpy.data.curves):
        if curve.name.startswith(PREFIX):
            bpy.data.curves.remove(curve, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.name.startswith(PREFIX):
            bpy.data.meshes.remove(mesh, do_unlink=True)
    for material in list(bpy.data.materials):
        if material.name.startswith(PREFIX):
            bpy.data.materials.remove(material, do_unlink=True)


def create_material(name, base_color, emission_strength=0.0):
    material = bpy.data.materials.get(PREFIX + name)
    if material is None:
        material = bpy.data.materials.new(PREFIX + name)

    material.diffuse_color = (*base_color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF") if material.node_tree else None
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.45
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*base_color, 1.0)
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*base_color, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return material


def create_route_curve(collection, label, points, material):
    data = bpy.data.curves.new(PREFIX + label, type="CURVE")
    data.dimensions = "3D"
    data.resolution_u = 2
    data.bevel_depth = 0.14
    data.bevel_resolution = 2

    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (*coordinate, 1.0)

    obj = bpy.data.objects.new(PREFIX + label, data)
    collection.objects.link(obj)
    obj.show_in_front = True
    obj.hide_render = True
    obj["allsaints_revision"] = REV
    obj["allsaints_role"] = "gameplay_route_guide"
    obj["allsaints_accuracy"] = "guia baseado em checkpoint da cena / nao topografico"
    data.materials.append(material)
    return obj


def create_zone_box(collection, label, location, dimensions, role, material):
    mesh = bpy.data.meshes.new(PREFIX + "ZONE MESH " + label)
    verts = [
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(PREFIX + "ZONE | " + label, mesh)
    collection.objects.link(obj)
    obj.location = location
    obj.dimensions = dimensions
    obj.display_type = "WIRE"
    obj.show_in_front = True
    obj.hide_render = True
    obj["allsaints_revision"] = REV
    obj["allsaints_role"] = "gameplay_zone"
    obj["allsaints_gameplay_zone"] = role
    obj["allsaints_accuracy"] = "guia baseado em checkpoint da cena / nao topografico"
    mesh.materials.append(material)
    return obj


def collection_context(obj):
    return " | ".join(norm(collection.name) for collection in obj.users_collection)


def classify_object(obj):
    if obj.name.startswith("R27 | ") or obj.name.startswith(PREFIX):
        return None

    search_text = norm(obj.name) + " | " + collection_context(obj)

    gameplay_tokens = (
        "CABINE", "PASSARELA", "ACESSO", "SAIDA", "ENTRADA", "CORREDOR",
        "PORTA", "SOLEIRA", "ESCADA", "BOTOEIRA", "BOTAO", "PISO JOG",
        "VOLUME JOG", "SISTEMA FUNCIONAL",
    )
    hero_tokens = (
        "ELEVADOR LACERDA", "LACERDA |", "MERCADO MODELO", "MERCADO |",
        "PALACIO THOME", "PALACIO RIO BRANCO", "PREFEITURA", "CAMARA",
        "FORTE SAO MARCELO", "FORTE |",
    )
    terrain_tokens = ("TERRENO", "RELEVO", "ENCOSTA", "CONTENCAO", "DEM")
    road_tokens = (
        "RUA ", "AVENIDA ", "LADEIRA ", "VIA ", "VIAS ", "CALCADA", "PASSEIO",
        "TRAVESSIA", "ASFALTO", "EIXOS REAIS DAS RUAS",
    )
    decor_tokens = (
        "BANCO", "POSTE", "GRADE", "COPA", "ARVORE", "PLACA", "FONTE",
        "LUMINARIA", "CORRIMAO", "MOBILIARIO", "MARIA FELIPA",
    )
    proxy_tokens = (
        "OSM ", "| OSM", "MAPA AMPLIADO", "IMPLANTACAO | OSM", "VOLUMES OSM",
        "CONTORNOS SEM ALTURA", "REFERENCIA FORA DO RECORTE",
    )

    if any(token in search_text for token in gameplay_tokens):
        return "GAMEPLAY"
    if any(token in search_text for token in hero_tokens):
        return "HERO"
    if any(token in search_text for token in terrain_tokens):
        return "TERRAIN"
    if any(token in search_text for token in road_tokens):
        return "ROADS"
    if any(token in search_text for token in decor_tokens):
        return "DECOR"
    if any(token in search_text for token in proxy_tokens):
        return "PROXY_OSM"
    if obj.type in {"MESH", "CURVE"}:
        return "ENVIRONMENT"
    return None


def safe_link_object(collection, obj):
    if obj.name not in collection.objects:
        try:
            collection.objects.link(obj)
        except RuntimeError:
            pass


def tag_and_organize(export_collections):
    counts = Counter()
    export_defaults = {
        "HERO": True,
        "GAMEPLAY": True,
        "TERRAIN": True,
        "ROADS": True,
        "DECOR": True,
        "PROXY_OSM": False,
        "ENVIRONMENT": True,
    }
    lod_hints = {
        "HERO": "LOD0 + LOD1/2 manual",
        "GAMEPLAY": "LOD0 / colisao revisada",
        "TERRAIN": "terreno em chunks / colisao simplificada",
        "ROADS": "unir por material/chunk somente apos validacao",
        "DECOR": "instanciar props repetidos somente apos prova de equivalencia",
        "PROXY_OSM": "somente referencia / excluir da exportacao padrao",
        "ENVIRONMENT": "candidato a LOD1",
    }

    for obj in bpy.data.objects:
        object_class = classify_object(obj)
        if not object_class:
            continue

        counts[object_class] += 1
        obj["allsaints_r28_class"] = object_class
        obj["allsaints_export_default"] = export_defaults[object_class]
        obj["allsaints_lod_hint"] = lod_hints[object_class]
        safe_link_object(export_collections[object_class], obj)

    return counts


def audit_scene(class_counts):
    objects = list(bpy.data.objects)
    meshes = list(bpy.data.meshes)
    materials = list(bpy.data.materials)

    type_counts = Counter(obj.type for obj in objects)
    mesh_objects = [obj for obj in objects if obj.type == "MESH" and obj.data]

    total_vertices = sum(len(obj.data.vertices) for obj in mesh_objects)
    total_polygons = sum(len(obj.data.polygons) for obj in mesh_objects)
    unique_vertices = sum(len(mesh.vertices) for mesh in meshes)
    unique_polygons = sum(len(mesh.polygons) for mesh in meshes)

    shared_meshes = sorted(
        ((mesh.users, mesh.name, len(mesh.vertices), len(mesh.polygons)) for mesh in meshes if mesh.users > 1),
        reverse=True,
    )

    base_groups = defaultdict(list)
    for obj in mesh_objects:
        base_name = re.sub(r"\.\d{3}$", "", obj.name)
        base_groups[base_name].append(obj.name)

    repeated_groups = sorted(
        ((len(names), base, names[:8]) for base, names in base_groups.items() if len(names) >= 3),
        reverse=True,
    )

    material_users = sorted(((material.users, material.name) for material in materials), reverse=True)

    non_uniform = []
    for obj in mesh_objects:
        sx, sy, sz = map(abs, obj.scale)
        if max(sx, sy, sz) - min(sx, sy, sz) > 1e-4:
            non_uniform.append(obj.name)

    lines = [
        "ALL SAINTS / SALVADOR MVP — AUDITORIA DE PERFORMANCE R28\n\n",
        f"Objetos: {len(objects):,}\n",
        f"Datablocks de mesh: {len(meshes):,}\n",
        f"Materiais: {len(materials):,}\n",
        f"Vertices somados por objeto (meshes compartilhadas contam por objeto): {total_vertices:,}\n",
        f"Poligonos somados por objeto (meshes compartilhadas contam por objeto): {total_polygons:,}\n",
        f"Vertices em datablocks de mesh unicos: {unique_vertices:,}\n",
        f"Poligonos em datablocks de mesh unicos: {unique_polygons:,}\n",
        f"Objetos mesh com escala nao uniforme: {len(non_uniform):,}\n\n",
        "CLASSES R28\n",
    ]

    for key in EXPORT_CLASSES:
        lines.append(f"- {key}: {class_counts.get(key, 0):,}\n")

    lines += [
        "\nNOTAS OPERACIONAIS\n",
        f"- {class_counts.get('PROXY_OSM', 0):,} objetos classificados como PROXY_OSM/referencia com allsaints_export_default=False. Nada e apagado ou ocultado.\n",
        f"- {class_counts.get('HERO', 0):,} objetos HERO e {class_counts.get('GAMEPLAY', 0):,} GAMEPLAY devem ter prioridade em revisao de LOD/colisao.\n",
        "- 33 EXPORT | R28 adiciona vinculos de colecao aos objetos existentes; nao duplica geometria de mesh.\n",
        "- R28 nao executa Join, Decimate, triangulacao ou renomeacao em massa.\n\n",
        "TIPOS DE OBJETO\n",
    ]

    for key, value in type_counts.most_common():
        lines.append(f"- {key}: {value:,}\n")

    lines.append("\nDATABLOCKS DE MESH COMPARTILHADOS — TOP 30\n")
    if shared_meshes:
        for users, name, vertices, polygons in shared_meshes[:30]:
            lines.append(f"- {name}: usuarios={users}, vertices={vertices:,}, poligonos={polygons:,}\n")
    else:
        lines.append("- Nenhum datablock de mesh com mais de um usuario foi encontrado. Pode existir grande potencial de instanciamento.\n")

    lines.append("\nGRUPOS DE NOMES REPETIDOS — TOP 40\n")
    lines.append("Repeticao de nome e apenas uma pista de auditoria e nunca deve ser usada sozinha para instanciar geometria.\n")
    for count, base, sample in repeated_groups[:40]:
        lines.append(f"- {base}: {count} objetos | amostra: {', '.join(sample)}\n")

    lines.append("\nMATERIAIS MAIS USADOS — TOP 30\n")
    for users, name in material_users[:30]:
        lines.append(f"- {name}: usuarios={users}\n")

    lines.append("\nESCALA NAO UNIFORME — PRIMEIROS 80\n")
    for name in non_uniform[:80]:
        lines.append(f"- {name}\n")
    if len(non_uniform) > 80:
        lines.append(f"- ... +{len(non_uniform) - 80} objetos\n")

    return "".join(lines)


def write_text(name, content):
    text = bpy.data.texts.get(name) or bpy.data.texts.new(name)
    text.clear()
    text.write(content)
    return text


def build_readme(class_counts):
    return """ALL SAINTS / SALVADOR MVP — R28

OBJETIVO
Preparar a cena existente para revisao de gameplay, organizacao de exportacao e otimizacao medida sem reorganizacao destrutiva.

ADICIONADO
1. 32 MVP | GAMEPLAY R28
   - guia da rota superior;
   - eixo vertical do elevador;
   - guia da rota inferior ate Praca Cairu / Mercado Modelo;
   - volumes wireframe das zonas de gameplay.
   Os helpers aparecem no viewport e usam hide_render=True.

2. 33 EXPORT | R28
   - HERO
   - GAMEPLAY
   - TERRAIN
   - ROADS
   - DECOR
   - PROXY_OSM
   - ENVIRONMENT
   Os objetos existentes recebem vinculos adicionais de colecao e permanecem nas colecoes originais.

3. Metadados de objeto
   - allsaints_r28_class
   - allsaints_export_default
   - allsaints_lod_hint

4. R28_PERFORMANCE_AUDIT
   Auditoria em runtime de geometria, escalas, meshes compartilhadas, grupos de nomes repetidos e uso de materiais.

IMPORTANTE
- Nenhum objeto existente e apagado.
- Nenhum objeto existente e renomeado em massa.
- Nao ha Join/Decimate/triangulacao em massa.
- PROXY_OSM e marcado para exclusao da exportacao padrao, mas continua visivel e intacto.
- As linhas de rota sao guias de design baseados em checkpoints existentes, nao dados topograficos certificados.

PROXIMO — R29
Usar R28_PERFORMANCE_AUDIT para um passe controlado de otimizacao. Nao otimizar apenas pelo nome do objeto.

CONTAGEM DAS CLASSES R28
""" + json.dumps(dict(class_counts), ensure_ascii=False, indent=2)


def revision_output_path(source_path):
    if not source_path:
        return os.path.join(os.path.expanduser("~"), "salvador_lacerda_mvp_r28.blend")

    root, ext = os.path.splitext(source_path)
    root = re.sub(r"_r\d+$", "", root, flags=re.IGNORECASE)
    return root + "_r28" + (ext or ".blend")


def main():
    scene = bpy.context.scene
    remove_generated()

    gameplay_root = get_or_create_collection(ROOT_GAMEPLAY)
    route_collection = get_or_create_collection(ROUTE_COLLECTION, gameplay_root)
    zone_collection = get_or_create_collection(ZONE_COLLECTION, gameplay_root)

    route_material = create_material("GUIA ROTA", (0.15, 0.55, 1.0), 1.5)
    zone_material = create_material("GUIA ZONAS", (1.0, 0.45, 0.08), 0.4)

    for label, points in ROUTE_SEGMENTS:
        create_route_curve(route_collection, label, points, route_material)

    for label, location, dimensions, role in ZONES:
        create_zone_box(zone_collection, label, location, dimensions, role, zone_material)

    export_root = get_or_create_collection(ROOT_EXPORT)
    export_collections = {
        key: get_or_create_collection(f"33 {key} | R28", export_root)
        for key in EXPORT_CLASSES
    }

    class_counts = tag_and_organize(export_collections)

    write_text(TEXT_README, build_readme(class_counts))
    write_text(TEXT_AUDIT, audit_scene(class_counts))

    scene["allsaints_r28_status"] = "guias de gameplay + classificacao de exportacao + auditoria de performance"
    scene["allsaints_r28_class_counts"] = json.dumps(dict(class_counts), ensure_ascii=False)

    output = revision_output_path(bpy.data.filepath)
    bpy.ops.wm.save_as_mainfile(filepath=output)
    print("[R28] Arquivo salvo:", output)
    print("[R28] Classes:", dict(class_counts))


if __name__ == "__main__":
    main()
