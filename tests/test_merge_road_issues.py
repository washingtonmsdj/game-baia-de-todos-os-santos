import unittest

from tools.world.merge_road_issues import merge


class RoadIssueLedgerTests(unittest.TestCase):
    def test_pending_evidence_change_is_historized(self):
        issue = {
            "issue_id": "area/way-1/test",
            "priority": 1,
            "classification": "NEEDS_REVIEW",
            "status": "pending",
            "evidence": {"occurrences": 2},
            "required_action": "review",
            "acceptance": None,
        }
        prior = {
            "area_id": "area",
            "issues": [{
                **issue,
                "evidence": {"occurrences": 1},
                "first_seen_cycle": "A",
                "last_seen_cycle": "A",
                "history": [{"cycle": "A", "event": "detected", "evidence": {"occurrences": 1}}],
            }],
            "applied_corrections": [],
        }
        result = merge({"area_id": "area", "issues": [issue]}, prior, "B")
        current = result["issues"][0]
        self.assertEqual(current["evidence"], {"occurrences": 2})
        self.assertEqual(current["history"][-1]["event"], "evidence_updated")
        self.assertEqual(current["history"][-1]["before"], {"occurrences": 1})
        self.assertEqual(current["history"][-1]["after"], {"occurrences": 2})

    def test_missing_pending_issue_requires_confirmation(self):
        prior = {
            "area_id": "area",
            "issues": [{
                "issue_id": "area/way-1/test",
                "priority": 0,
                "classification": "NEEDS_REVIEW",
                "status": "pending",
                "evidence": {"occurrences": 1},
                "required_action": "review",
                "acceptance": None,
                "first_seen_cycle": "A",
                "last_seen_cycle": "A",
                "history": [],
            }],
            "applied_corrections": [],
        }
        result = merge({"area_id": "area", "issues": []}, prior, "B")
        current = result["issues"][0]
        self.assertEqual(current["status"], "not_observed_needs_confirmation")
        self.assertEqual(current["history"][-1]["event"], "not_observed")

    def test_resolved_issue_observed_again_reopens(self):
        prior = {
            "area_id": "area",
            "issues": [{
                "issue_id": "area/way-1/test",
                "priority": 0,
                "classification": "NEEDS_REVIEW",
                "status": "resolved",
                "evidence": {"occurrences": 1},
                "required_action": "review",
                "acceptance": {"cycle": "A"},
                "first_seen_cycle": "A",
                "last_seen_cycle": "A",
                "history": [],
            }],
            "applied_corrections": [],
        }
        active = [{
            "issue_id": "area/way-1/test",
            "priority": 1,
            "classification": "ERROR",
            "status": "pending",
            "evidence": {"occurrences": 3},
            "required_action": "recheck",
            "acceptance": None,
        }]
        result = merge({"area_id": "area", "issues": active}, prior, "B")
        current = result["issues"][0]
        self.assertEqual(current["status"], "pending")
        self.assertEqual(current["classification"], "ERROR")
        self.assertEqual(current["required_action"], "recheck")
        self.assertEqual(current["history"][-1]["event"], "observed_again")


if __name__ == "__main__":
    unittest.main()
