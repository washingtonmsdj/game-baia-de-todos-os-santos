"""Fechamento de dependências glTF por setor, preservando índices e semântica.

A otimização só é aplicada quando as relações de recursos são conhecidas.
Materiais ou texturas com extensões desconhecidas mantêm as tabelas originais.
"""
from copy import deepcopy


_TEXTURE_SLOTS = ("normalTexture", "occlusionTexture", "emissiveTexture")
_PBR_TEXTURE_SLOTS = ("baseColorTexture", "metallicRoughnessTexture")
_RESOURCE_TABLES = ("materials", "textures", "images", "samplers")


def _at(source, kind, index):
    items = source.get(kind, [])
    if type(index) is not int or index < 0 or index >= len(items):
        raise ValueError(f"Índice glTF inválido: {kind}[{index!r}]")
    return items[index]


def _slots(material):
    pbr = material.get("pbrMetallicRoughness", {})
    for key in _PBR_TEXTURE_SLOTS:
        if key in pbr:
            yield pbr[key]
    for key in _TEXTURE_SLOTS:
        if key in material:
            yield material[key]


def prune_render_resources(source, target):
    """Restringe recursos às meshes presentes em target, in-place.

    Retorna False se extensões requererem preservar as tabelas completas;
    nunca altera o documento de origem e nunca deixa referências pendentes.
    """
    material_ids = set()
    for mesh in target.get("meshes", []):
        for primitive in mesh["primitives"]:
            if "material" in primitive:
                material_ids.add(primitive["material"])
    ordered_materials = sorted(material_ids)
    materials = [_at(source, "materials", i) for i in ordered_materials]

    # Referências dentro de extensões podem usar índices de texturas diferentes.
    # Preservar as tabelas completas é preferível a publicar GLB corrompido.
    if any(item.get("extensions") for item in materials):
        return False

    texture_ids = set()
    for material in materials:
        for slot in _slots(material):
            if not isinstance(slot, dict) or "index" not in slot:
                raise ValueError("TextureInfo glTF inválido")
            texture_ids.add(slot["index"])
    ordered_textures = sorted(texture_ids)
    textures = [_at(source, "textures", i) for i in ordered_textures]
    if any(item.get("extensions") for item in textures):
        return False

    image_ids = set()
    sampler_ids = set()
    for texture in textures:
        if "source" not in texture:
            raise ValueError("Texture sem imagem de origem")
        image_ids.add(texture["source"])
        if "sampler" in texture:
            sampler_ids.add(texture["sampler"])
    ordered_images = sorted(image_ids)
    images = [_at(source, "images", i) for i in ordered_images]
    if any(item.get("extensions") for item in images):
        return False
    ordered_samplers = sorted(sampler_ids)
    for i in ordered_samplers:
        _at(source, "samplers", i)

    maps = {
        "materials": {old: new for new, old in enumerate(ordered_materials)},
        "textures": {old: new for new, old in enumerate(ordered_textures)},
        "images": {old: new for new, old in enumerate(ordered_images)},
        "samplers": {old: new for new, old in enumerate(ordered_samplers)},
    }

    for mesh in target.get("meshes", []):
        for primitive in mesh["primitives"]:
            if "material" in primitive:
                primitive["material"] = maps["materials"][primitive["material"]]

    new_materials = [deepcopy(item) for item in materials]
    for material in new_materials:
        for slot in _slots(material):
            slot["index"] = maps["textures"][slot["index"]]

    new_textures = [deepcopy(item) for item in textures]
    for texture in new_textures:
        texture["source"] = maps["images"][texture["source"]]
        if "sampler" in texture:
            texture["sampler"] = maps["samplers"][texture["sampler"]]

    selected = {
        "materials": new_materials,
        "textures": new_textures,
        "images": [deepcopy(item) for item in images],
        "samplers": [deepcopy(_at(source, "samplers", i)) for i in ordered_samplers],
    }
    for kind in _RESOURCE_TABLES:
        if kind in source:
            target[kind] = selected[kind]
        else:
            target.pop(kind, None)
    return True
