import unittest

from analytics.tutor_stats import build_summary, recommend_actions


class TutorStatsTest(unittest.TestCase):
    def test_build_summary_counts_roles_and_workflow_states(self):
        data = {
            "users": [
                {"role": "PARENT"},
                {"role": "PARENT"},
                {"role": "TUTOR"},
                {"role": "ADMIN"},
            ],
            "demands": [
                {"status": "OPEN"},
                {"status": "MATCHED"},
                {"status": "PENDING_REVIEW"},
            ],
            "applications": [
                {"status": "SUBMITTED"},
                {"status": "ACCEPTED"},
            ],
            "orders": [
                {"status": "ACTIVE"},
            ],
        }

        summary = build_summary(data)

        self.assertEqual(summary["roles"]["PARENT"], 2)
        self.assertEqual(summary["demands"]["OPEN"], 1)
        self.assertEqual(summary["applications"]["ACCEPTED"], 1)
        self.assertEqual(summary["application_conversion_rate"], 0.5)

    def test_recommend_actions_reports_pending_review_pressure(self):
        summary = {
            "demands": {"PENDING_REVIEW": 3, "OPEN": 1},
            "applications": {"SUBMITTED": 2},
            "orders": {"ACTIVE": 0},
            "application_conversion_rate": 0.0,
        }

        actions = recommend_actions(summary)

        self.assertTrue(any("审核" in action for action in actions))
        self.assertTrue(any("申请" in action for action in actions))


if __name__ == "__main__":
    unittest.main()
