import copy
import json
import struct
import unittest

from tools.runtime.glb_resources import prune_render_resources
from tools.runtime.package_world import subset


def fixture():
    return {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0, 1]}],
        "nodes": [{"mesh": 0}, {"mesh": 1}],
        "meshes": [
            {"primitives": [{"attributes": {"POSITION": 0}, "material": 0}]},
            {"primitives": [{"attributes": {"POSITION": 0}, "material": 1}]},
        ],
        "accessors": [{"bufferView": 0, "componentType": 5126, "count": 1,
                       "type": "VEC3", "min": [0, 0, 0], "max": [1, 1, 1]}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": 12},
            {"buffer": 0, "byteOffset": 12, "byteLength": 4},
            {"buffer": 0, "byteOffset": 16, "byteLength": 4},
        ],
        "buffers": [{"byteLength": 20}],
        "materials": [
            {"pbrMetallicRoughness": {"baseColorTexture": {"index": 0}}},
            {"pbrMetallicRoughness": {"baseColorTexture": {"index": 1}}},
        ],
        "textures": [{"source": 0, "sampler": 0}, {"source": 1, "sampler": 1}],
        "images": [{"bufferView": 1, "mimeType": "image/png"},
                   {"bufferView": 2, "mimeType": "image/png"}],
        "samplers": [{"magFilter": 9729}, {"magFilter": 9728}],
    }


def unpack(package):
    magic, version, length = struct.unpack_from("<III", package)
    if magic != 0x46546C67 or version != 2 or length != len(package):
        raise AssertionError("GLB inválido")
    json_size, json_kind = struct.unpack_from("<II", package, 12)
    if json_kind != 0x4E4F534A:
        raise AssertionError("JSON GLB ausente")
    document = json.loads(package[20:20 + json_size])
    offset = 20 + json_size
    bin_size, bin_kind = struct.unpack_from("<II", package, offset)
    if bin_kind != 0x004E4942:
        raise AssertionError("BIN GLB ausente")
    return document, package[offset + 8:offset + 8 + bin_size]


class GLBResourceClosureTests(unittest.TestCase):
    def test_sector_keeps_only_its_material_and_embedded_image(self):
        source = fixture()
        untouched = copy.deepcopy(source)
        result = subset(source, bytes(range(20)), [1], {})
        sector, binary = unpack(result)
        self.assertEqual(source, untouched)
        self.assertEqual(1, len(sector["meshes"]))
        self.assertEqual(0, sector["meshes"][0]["primitives"][0]["material"])
        self.assertEqual(1, len(sector["materials"]))
        self.assertEqual(1, len(sector["textures"]))
        self.assertEqual(1, len(sector["images"]))
        self.assertEqual(1, len(sector["samplers"]))
        self.assertEqual(0, sector["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"]["index"])
        self.assertEqual(0, sector["textures"][0]["source"])
        self.assertEqual(0, sector["textures"][0]["sampler"])
        self.assertEqual(2, len(sector["bufferViews"]))
        self.assertEqual(bytes(range(12)) + bytes(range(16, 20)), binary)
        self.assertEqual(16, sector["buffers"][0]["byteLength"])

    def test_unknown_material_extension_preserves_tables(self):
        source = fixture()
        source["materials"][1]["extensions"] = {"VENDOR_example": {"resource": 1}}
        target = {"meshes": copy.deepcopy(source["meshes"][1:]),
                  **{key: copy.deepcopy(source[key])
                     for key in ("materials", "textures", "images", "samplers")}}
        self.assertFalse(prune_render_resources(source, target))
        self.assertEqual(source["materials"], target["materials"])
        self.assertEqual(1, target["meshes"][0]["primitives"][0]["material"])

    def test_absent_material_removes_unreferenced_resources(self):
        source = fixture()
        target = {"meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
                  **{key: copy.deepcopy(source[key])
                     for key in ("materials", "textures", "images", "samplers")}}
        self.assertTrue(prune_render_resources(source, target))
        for kind in ("materials", "textures", "images", "samplers"):
            self.assertEqual([], target[kind])

    def test_broken_texture_reference_fails_closed(self):
        source = fixture()
        source["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"]["index"] = 9
        target = {"meshes": copy.deepcopy(source["meshes"][:1]),
                  **{key: copy.deepcopy(source[key])
                     for key in ("materials", "textures", "images", "samplers")}}
        with self.assertRaisesRegex(ValueError, "Índice glTF inválido"):
            prune_render_resources(source, target)

    def test_texture_extension_is_not_reindexed(self):
        source = fixture()
        source["textures"][0]["extensions"] = {"KHR_texture_basisu": {"source": 1}}
        target = {"meshes": copy.deepcopy(source["meshes"][:1]),
                  **{key: copy.deepcopy(source[key])
                     for key in ("materials", "textures", "images", "samplers")}}
        self.assertFalse(prune_render_resources(source, target))
        self.assertEqual(source["textures"], target["textures"])


if __name__ == "__main__":
    unittest.main()
