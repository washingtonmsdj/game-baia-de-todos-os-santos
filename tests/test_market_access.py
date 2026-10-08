import copy
import math
import unittest

from tools.world.market_access import evaluate_access_candidates


def location():
    return {"area_id": "mvp-centro-lacerda", "locations": [{
        "location_id": "mercado-modelo", "blender_binding": None,
        "reference_status": "partial", "osm": {"id": 59392558, "verified": False},
    }]}


def candidate():
    return {
        "name": "ACESSO | fachada Praça Cairu", "visible": True,
        "center_xy": [-126.491974, 154.290283],
        "clear_gap_m": 2.75891, "headroom_m": 4.5,
        "reference_status": "esboço tipológico; OSM; sem planta cadastral",
        "samples": [{"offset_m": -1, "terrain_z": 7.25566, "floor_z": None},
                    {"offset_m": 0, "terrain_z": 7.25566, "floor_z": 7.25566},
                    {"offset_m": 1, "terrain_z": 7.25566, "floor_z": 7.25566}],
    }


class MarketAccessTests(unittest.TestCase):
    def test_visible_cairu_portal_is_only_candidate_not_approved_route(self):
        result = evaluate_access_candidates(location(), "mercado-modelo", [candidate()])
        self.assertEqual(1, result["geometry_candidates"])
        self.assertFalse(result["market_route_approved"])
        self.assertEqual(0, result["approved_access_count"])
        self.assertFalse(result["candidates"][0]["route_certified"])
        self.assertIn("LOCAL_SEM_BINDING_VERIFICADO", result["candidates"][0]["blockers"])
        self.assertIn("MODELO_TIPOLOGICO_NAO_CADASTRAL", result["candidates"][0]["blockers"])

    def test_missing_floor_at_center_does_not_infer_passage(self):
        portal = candidate()
        portal["samples"][1]["floor_z"] = None
        result = evaluate_access_candidates(location(), "mercado-modelo", [portal])
        self.assertFalse(result["candidates"][0]["center_levels_match"])
        self.assertFalse(result["candidates"][0]["geometry_candidate"])

    def test_legacy_hidden_door_never_becomes_candidate(self):
        portal = candidate()
        portal["visible"] = False
        result = evaluate_access_candidates(location(), "mercado-modelo", [portal])
        self.assertFalse(result["candidates"][0]["geometry_candidate"])

    def test_level_mismatch_requires_review(self):
        portal = candidate()
        portal["samples"][1]["terrain_z"] = 8.0
        result = evaluate_access_candidates(location(), "mercado-modelo", [portal])
        self.assertFalse(result["candidates"][0]["geometry_candidate"])

    def test_verified_osm_does_not_certify_route_without_full_gates(self):
        registry = location()
        registry["locations"][0]["osm"]["verified"] = True
        registry["locations"][0]["blender_binding"] = {"candidate": "x"}
        result = evaluate_access_candidates(registry, "mercado-modelo", [candidate()])
        self.assertFalse(result["market_route_approved"])
        self.assertIn("SEM_ENSAIO_COMPLETO_DE_COLISAO_E_NAVEGACAO",
                      result["candidates"][0]["blockers"])

    def test_missing_registry_or_duplicate_portal_fails_closed(self):
        with self.assertRaises(ValueError):
            evaluate_access_candidates({"locations": []}, "mercado-modelo", [candidate()])
        with self.assertRaises(ValueError):
            evaluate_access_candidates(location(), "mercado-modelo", [candidate(), candidate()])

    def test_invalid_geometry_rejected(self):
        for bad in (float("nan"), -1.0, float("inf")):
            portal = candidate()
            portal["clear_gap_m"] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                evaluate_access_candidates(location(), "mercado-modelo", [portal])

    def test_measurement_is_not_modified(self):
        source = candidate()
        before = copy.deepcopy(source)
        evaluate_access_candidates(location(), "mercado-modelo", [source])
        self.assertEqual(before, source)


if __name__ == "__main__":
    unittest.main()
