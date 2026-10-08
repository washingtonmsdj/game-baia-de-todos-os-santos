import copy
import math
import unittest

from tools.world.market_access import evaluate_access_candidates, evaluate_direct_approach


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




def proxy():
    return {
        "scene_file": "blender/salvador_lacerda_r30b82_gameplay_proxy.blend",
        "local_frame": {"origin_xy": [-48.321311950683594, 48.90056800842285],
                        "angle": -0.7536059503636807},
        "lower_route": [[-3, 0], [-69.33086893763439, 14.014297508040542, 7.25566864]],
    }


def ground():
    return [{"t": 0.0, "terrain_z": 7.25566},
            {"t": 0.5, "terrain_z": 7.25566},
            {"t": 1.0, "terrain_z": 7.25566}]


class MarketApproachTests(unittest.TestCase):
    def test_real_gap_and_measured_visible_hits(self):
        observations = [
            {"name": "banco | posição aproximada encosto.002", "distance_m": 5.145, "ray_z": 8.0},
            {"name": "ACESSO | fachada Praça Cairu | ombreira D",
             "distance_m": 58.896, "ray_z": 7.6},
        ]
        r = evaluate_direct_approach(proxy(), [-126.491974, 154.290283],
                                     ground(), observations,
                                     nav_bounds=[[-89.29, -47.07], [54.16, 116.06]])
        self.assertAlmostEqual(r["segment"]["length_m"], 60.515, places=2)
        self.assertAlmostEqual(r["segment"]["start_world_xy"][0], -89.289593, places=3)
        self.assertEqual("DIRECT_LINE_INTERSECTS_VISIBLE_GEOMETRY", r["status"])
        self.assertEqual("banco | posição aproximada encosto.002", r["visual_ray_hits"][0]["name"])
        self.assertTrue(r["nav_hint_start_inside_bbox"])
        self.assertFalse(r["nav_hint_target_inside_bbox"])
        self.assertFalse(r["route_approved"])
        self.assertFalse(r["complete_collision_test"])

    def test_no_visual_hit_is_not_certification(self):
        r = evaluate_direct_approach(proxy(), [-126.491974, 154.290283], ground(), [])
        self.assertEqual("NO_VISUAL_HIT_NOT_CERTIFIED", r["status"])
        self.assertTrue(r["visual_line_clear"])
        self.assertFalse(r["route_approved"])
        self.assertFalse(r["navigation_approved"])

    def test_requires_whole_segment_terrain_sampling(self):
        samples = ground()[1:]
        with self.assertRaisesRegex(ValueError, "extremidades"):
            evaluate_direct_approach(proxy(), [-126, 154], samples, [])

    def test_missing_terrain_does_not_approve(self):
        samples = ground()
        samples[1]["terrain_z"] = None
        r = evaluate_direct_approach(proxy(), [-126, 154], samples, [])
        self.assertEqual(1, r["terrain_missing"])
        self.assertFalse(r["route_approved"])

    def test_outside_hit_and_duplicate_t_rejected(self):
        with self.assertRaisesRegex(ValueError, "fora do segmento"):
            evaluate_direct_approach(proxy(), [-126, 154], ground(),
                                     [{"name": "obstacle", "distance_m": 999, "ray_z": 8}])
        bad = ground()
        bad[1]["t"] = 0
        with self.assertRaisesRegex(ValueError, "sequência"):
            evaluate_direct_approach(proxy(), [-126, 154], bad, [])

    def test_unchanged_inputs(self):
        p = proxy()
        t = ground()
        h = [{"name": "bench", "distance_m": 2, "ray_z": 8}]
        before = copy.deepcopy((p, t, h))
        evaluate_direct_approach(p, [-126, 154], t, h)
        self.assertEqual((p, t, h), before)


if __name__ == "__main__":
    unittest.main()
