import unittest

from helpers import HOME  # noqa: F401
import orders
from xvlib import DEFAULT_CONFIG


def rec(**kw):
    data = {"id": "s1", "set_by": "pat", "budget": {"usd": 2}, "moved_tests": [], "spend": [],
            "stops": [], "checks": {"reports": []}}
    data.update(kw)
    return data


def with_report(data, agent, status="done", **extra):
    data["checks"]["reports"].append(dict(agent=agent, status=status, **extra))
    return data


class OrdersTest(unittest.TestCase):
    def stop(self, data, after, config=DEFAULT_CONFIG):
        return orders.verdict(data, after, config)["stop"]

    def test_a_step_with_no_report_stops(self):
        s = self.stop(rec(), "maker")
        self.assertEqual((s["order"], s["seat"]), ("no_report", "originator"))

    def test_a_missing_report_fires_one_order(self):
        d = with_report(rec(), "maker", "no-report")
        fired = [f["order"] for f in orders.verdict(d, "maker", DEFAULT_CONFIG)["fired"]]
        self.assertEqual(fired, ["no_report"])

    def test_the_budget_is_spent_and_the_suite_is_red(self):
        d = with_report(rec(spend=[{"step": "maker", "usd": 2.5, "tokens": 10}]), "maker", "green")
        d["checks"]["maker"] = {"suite": "red"}
        self.assertEqual(self.stop(d, "maker")["order"], "budget_spent")

    def test_a_spent_budget_with_a_green_suite_goes_on(self):
        d = with_report(rec(spend=[{"step": "maker", "usd": 2.5}]), "maker", "green")
        d["checks"]["maker"] = {"suite": "green"}
        self.assertIsNone(self.stop(d, "maker"))

    def test_an_unrecorded_move_stops(self):
        d = with_report(rec(), "maker", "green")
        d["checks"]["maker"] = {"suite": "green", "wall": {"unrecorded": ["tests/test_a.py"]}}
        self.assertEqual(self.stop(d, "maker")["order"], "unrecorded_move")

    def test_a_stall_opens_the_shape_conversation(self):
        d = with_report(rec(), "maker", "stopped", stop={"reason": "repeated_failure"})
        d["checks"]["maker"] = {"suite": "red"}
        self.assertIn("shape conversation", self.stop(d, "maker")["question"])

    def test_scenario_must_stay_in_the_tests_and_be_red(self):
        d = with_report(rec(), "scenario", "red")
        d["checks"]["scenario"] = {"outside_tests": ["pantry/store.py"], "red_fails": False}
        fired = {f["order"] for f in orders.verdict(d, "scenario", DEFAULT_CONFIG)["fired"]}
        self.assertEqual(fired, {"scenario_touched_source", "scenario_not_red"})

    def test_shape_or_pitch_is_for_two_people_and_outranks_moves(self):
        d = with_report(rec(shape_change="no", pitch_contradiction="yes",
                            moved_tests=[{"file": "tests/a.py"}]), "guardian")
        d["checks"]["guardian"] = {"picture_change": "no"}
        s = self.stop(d, "guardian")
        self.assertEqual((s["order"], s["seat"]), ("shape_or_pitch", "two_people"))

    def test_moved_tests_alone_go_to_the_originator(self):
        d = with_report(rec(shape_change="no", pitch_contradiction="no",
                            moved_tests=[{"file": "tests/a.py"}]), "guardian")
        d["checks"]["guardian"] = {}
        self.assertEqual(self.stop(d, "guardian")["order"], "accept_moves")

    def test_green_and_nothing_stopped_the_merge_is_theirs(self):
        d = with_report(rec(shape_change="no", pitch_contradiction="no"), "guardian")
        d["checks"]["guardian"] = {}
        s = self.stop(d, "guardian")
        self.assertEqual((s["order"], s["seat"]), ("ready_to_merge", "originator"))

    def test_a_feature_asks_the_person_to_watch_the_first_green(self):
        d = with_report(rec(kind="feature", shape_change="no", pitch_contradiction="no",
                            red={"watch_first_green": "Use the last loaf; bread leaves the list."}), "guardian")
        d["checks"]["guardian"] = {}
        self.assertIn("watch the first green run: Use the last loaf", self.stop(d, "guardian")["question"])

    def test_a_raise_past_the_team_limit_is_for_two_people(self):
        config = dict(DEFAULT_CONFIG, limits={"budget_raise_pct": 50})
        d = with_report(rec(budget={"usd": 4, "raised_from": {"usd": 2}}), "forecaster")
        self.assertEqual(self.stop(d, "forecaster", config)["seat"], "two_people")

    def test_no_budget_after_the_forecast_asks_the_engineer(self):
        d = with_report(rec(budget=None), "forecaster")
        self.assertEqual(self.stop(d, "forecaster")["order"], "budget_not_set")


if __name__ == "__main__":
    unittest.main()
