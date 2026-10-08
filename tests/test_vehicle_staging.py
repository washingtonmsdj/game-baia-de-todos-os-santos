import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path

from tools.runtime.vehicle_staging import inspect_vehicle_glb, validate_vehicle_staging


SCENE = "ONIBUS | Torino 31065 v03"


def glb(document):
    data = json.dumps(document, separators=(",", ":")).encode("utf-8")
    data += b" " * (-len(data) % 4)
    binary = bytes(range(12))
    size = 28 + len(data) + len(binary)
    return (struct.pack("<III", 0x46546C67, 2, size)
            + struct.pack("<II", len(data), 0x4E4F534A) + data
            + struct.pack("<II", len(binary), 0x004E4942) + binary)


def scene_doc():
    return {"asset": {"version": "2.0"}, "scene": 0,
            "scenes": [{"name": SCENE, "nodes": [0]}],
            "nodes": [{"name": "BUS02 | Carroceria", "mesh": 0}],
            "meshes": [{"primitives": []}]}


class VehicleStagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "onibus.glb"
        self.vehicle = {"id": "vehicle-torino-salvador-31065",
                        "source": {"file": "blender/assets/onibus_torino_31065_v03.blend",
                                   "sha256": "a" * 64, "scene": SCENE}}
        self.save(scene_doc())

    def save(self, document):
        self.path.write_bytes(glb(document))
        manifest = {"schema": "boas/vehicle-export-v1", "vehicle_id": self.vehicle["id"],
                    "source_file": self.vehicle["source"]["file"],
                    "source_sha256": self.vehicle["source"]["sha256"],
                    "source_scene": SCENE,
                    "export_sha256": hashlib.sha256(self.path.read_bytes()).hexdigest(),
                    "scene_count": 1,
                    "selected_objects": ["BUS02 | Carroceria"]}
        self.path.with_suffix(".json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_accepts_single_scene_with_valid_provenance(self):
        result = validate_vehicle_staging(self.path, self.vehicle)
        self.assertEqual(1, result["scene_count"])
        self.assertEqual(1, result["selected_object_count"])

    def test_rejects_stale_binary(self):
        self.path.write_bytes(self.path.read_bytes() + b"XXXX")
        with self.assertRaisesRegex(ValueError, "alterado"):
            validate_vehicle_staging(self.path, self.vehicle)

    def test_rejects_missing_manifest(self):
        self.path.with_suffix(".json").unlink()
        with self.assertRaisesRegex(ValueError, "Manifesto"):
            validate_vehicle_staging(self.path, self.vehicle)

    def test_rejects_unrelated_source(self):
        self.vehicle["source"]["sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "Proveniência"):
            validate_vehicle_staging(self.path, self.vehicle)

    def test_rejects_multiple_scenes(self):
        doc = scene_doc()
        doc["scenes"].append({"name": "SALVADOR | ESBOCO OFICIAL", "nodes": [0]})
        self.save(doc)
        with self.assertRaisesRegex(ValueError, "cenas adicionais"):
            validate_vehicle_staging(self.path, self.vehicle)

    def test_rejects_wrong_default_scene(self):
        doc = scene_doc()
        doc["scene"] = 1
        self.save(doc)
        with self.assertRaisesRegex(ValueError, "ativa outra"):
            validate_vehicle_staging(self.path, self.vehicle)

    def test_rejects_studio_floor(self):
        doc = scene_doc()
        doc["nodes"].append({"name": "BUS02 | Chao estudio", "mesh": 0})
        self.save(doc)
        with self.assertRaisesRegex(ValueError, "estúdio"):
            validate_vehicle_staging(self.path, self.vehicle)

    def test_rejects_unrelated_selected_object(self):
        manifest_path = self.path.with_suffix(".json")
        obj = json.loads(manifest_path.read_text(encoding="utf-8"))
        obj["selected_objects"].append("Camera")
        manifest_path.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "fora do ônibus"):
            validate_vehicle_staging(self.path, self.vehicle)

    def test_invalid_glb_header(self):
        self.path.write_bytes(b"not a GLB")
        with self.assertRaises(ValueError):
            inspect_vehicle_glb(self.path, SCENE)


if __name__ == "__main__":
    unittest.main()
