import json
import os
import unittest

from helpers import HOME  # noqa: F401
import orders
import record
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

    def test_the_after_maker_check_counts_every_steps_spend(self):
        # the maker spent $0.5 of a $2 budget; the steps around it spent $1.6 more
        d = with_report(rec(spend=[{"step": "forecaster", "usd": 0.6, "tokens": 10},
                                   {"step": "scenario", "usd": 1.0, "tokens": 10},
                                   {"step": "maker", "usd": 0.5, "tokens": 10}]), "maker", "green")
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

    def test_a_stall_question_offers_to_reshape_the_slice(self):
        d = with_report(rec(), "maker", "stopped", stop={"reason": "repeated_failure"})
        d["checks"]["maker"] = {"suite": "red"}
        self.assertIn("reshape the slice", self.stop(d, "maker")["question"])

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

    def test_slice_only_moves_alone_do_not_stop_for_accept_moves(self):
        d = with_report(rec(shape_change="no", pitch_contradiction="no",
                            moved_tests=[{"file": "tests/a.py", "slice_only": True}]), "guardian")
        d["checks"]["guardian"] = {}
        self.assertEqual(self.stop(d, "guardian")["order"], "ready_to_merge")

    def test_a_slice_only_move_beside_a_plain_move_still_fires_accept_moves(self):
        d = with_report(rec(shape_change="no", pitch_contradiction="no",
                            moved_tests=[{"file": "tests/a.py", "slice_only": True},
                                         {"file": "tests/b.py"}]), "guardian")
        d["checks"]["guardian"] = {}
        self.assertEqual(self.stop(d, "guardian")["order"], "accept_moves")

    def test_slice_only_moves_do_not_hide_a_picture_change(self):
        d = with_report(rec(shape_change="no", pitch_contradiction="no",
                            moved_tests=[{"file": "tests/a.py", "slice_only": True}]), "guardian")
        d["checks"]["guardian"] = {"picture_change": "yes"}
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

    def test_a_raise_past_the_limit_stops_once(self):
        config = dict(DEFAULT_CONFIG, limits={"budget_raise_pct": 50})
        d = with_report(rec(budget={"usd": 4, "raised_from": {"usd": 2}}), "cleaner")
        self.assertNotEqual((self.stop(d, "cleaner", config) or {}).get("order"), "budget_past_limit")
        d["stops"] = [{"order": "budget_past_limit", "answer": "go on", "answered_by": ["a", "b"]}]
        d = with_report(d, "maker", "green")
        d["checks"]["maker"] = {"suite": "green"}
        self.assertIsNone(self.stop(d, "maker", config))

    def test_the_same_tests_failing_twice_is_a_repeated_failure(self):
        d = with_report(rec(), "maker", "green")
        d["checks"]["maker"] = {"suite": "red", "failing_history": [["test_a (t.T.test_a)"], ["test_a (t.T.test_a)"]]}
        fired = [f["order"] for f in orders.verdict(d, "maker", DEFAULT_CONFIG)["fired"]]
        self.assertIn("repeated_failure", fired)

    def test_solo_keeps_the_stop_and_tells_one_person_to_answer(self):
        config = dict(DEFAULT_CONFIG, seats={"two_people": "solo"})
        d = with_report(rec(shape_change="yes", pitch_contradiction="no"), "guardian")
        d["checks"]["guardian"] = {}
        s = self.stop(d, "guardian", config)
        self.assertEqual(s["seat"], "two_people")
        self.assertIn("runs solo", s["question"])

    def test_a_diff_that_more_than_doubles_between_maker_runs(self):
        d = with_report(rec(), "maker", "green")
        d["checks"]["maker"] = {"suite": "green", "diff_history": [40, 130]}
        self.assertEqual(self.stop(d, "maker")["order"], "diff_growing")

    def test_no_budget_after_the_forecast_asks_the_engineer(self):
        d = with_report(rec(budget=None), "forecaster")
        self.assertEqual(self.stop(d, "forecaster")["order"], "budget_not_set")

    def test_a_prototype_slice_without_prototype_budgets_asks_the_person_who_set_it_going(self):
        d = rec(kind="prototype")
        d = with_report(d, "prototype")
        s = self.stop(d, "prototype")
        self.assertEqual((s["order"], s["seat"]), ("prototype_budgets_not_set", "originator"))

    def test_prototype_budgets_for_all_three_variants_do_not_stop_it(self):
        d = with_report(rec(kind="prototype", prototype_budgets={n: {"usd": 1} for n in "abc"}), "prototype")
        self.assertNotEqual((self.stop(d, "prototype") or {}).get("order"), "prototype_budgets_not_set")

    def scenario_done(self, slice_only):
        d = with_report(rec(slice_only=slice_only), "scenario", "red")
        d["checks"]["scenario"] = {"outside_tests": [], "red_fails": True}
        return d

    def test_slice_only_marks_after_the_scenario_stop_for_the_person_who_set_it_going(self):
        marks = [{"file": "tests/test_a.py", "test": "test_file_is_ts", "why": "only proves the rename"},
                 {"file": "tests/test_b.py", "test": "test_old_flag_gone", "why": "dead after the slice"}]
        s = self.stop(self.scenario_done(marks), "scenario")
        self.assertIsNotNone(s)
        self.assertEqual(s["seat"], "originator")
        for m in marks:
            self.assertIn(m["test"], s["question"])
            self.assertIn(m["why"], s["question"])

    def test_no_slice_only_marks_add_no_stop_after_the_scenario(self):
        self.assertIsNone(self.stop(self.scenario_done([]), "scenario"))

    def test_unmarking_a_test_takes_it_off_the_stop_and_leaves_it_to_join_the_wall(self):
        a = {"file": "tests/test_a.py", "test": "test_file_is_ts", "why": "only proves the rename"}
        b = {"file": "tests/test_b.py", "test": "test_old_flag_gone", "why": "dead after the slice"}
        s = self.stop(self.scenario_done([b]), "scenario")  # the person unmarked test_file_is_ts
        self.assertIsNotNone(s)
        self.assertIn(b["test"], s["question"])
        self.assertNotIn(a["test"], s["question"])
        self.assertIn("unmark", s["question"].lower())
        # an unmarked test is not in slice_only, so removing it is a plain move the person must accept
        d = with_report(rec(shape_change="no", pitch_contradiction="no", slice_only=[b],
                            moved_tests=[{"file": a["file"], "assertion": a["test"]}]), "guardian")
        d["checks"]["guardian"] = {}
        self.assertEqual(self.stop(d, "guardian")["order"], "accept_moves")

    def guardian_with(self, recs):
        d = with_report(rec(shape_change="no", pitch_contradiction="no", wall_recommendations=recs), "guardian")
        d["checks"]["guardian"] = {}
        return d

    def test_a_wall_recommendation_waits_for_the_person_who_set_the_work_going(self):
        recs = [{"file": "tests/test_a.py", "test": "test_new_thing", "recommend": "stay off the wall",
                 "why": "not marked slice-only, covered by the packet", "accepted": False}]
        s = self.stop(self.guardian_with(recs), "guardian")
        self.assertEqual((s["order"], s["seat"]), ("accept_moves", "originator"))

    def test_accepted_wall_recommendations_do_not_stop_again(self):
        recs = [{"file": "tests/test_a.py", "test": "test_new_thing", "recommend": "remove",
                 "why": "the wall held it before the slice", "accepted": True}]
        self.assertEqual(self.stop(self.guardian_with(recs), "guardian")["order"], "ready_to_merge")

    def test_the_record_keeps_the_guardians_wall_recommendations(self):
        recs = [{"file": "tests/test_a.py", "test": "test_new_thing", "recommend": "stay on the wall",
                 "why": "marked slice-only"}]
        text = ("```xv-report\n" + json.dumps({"agent": "guardian", "status": "done", "summary": "p",
                "shape_change": "no", "pitch_contradiction": "no", "wall_recommendations": recs}) + "\n```\n")
        data = rec()
        record.apply_report(data, "", "guardian", text)
        self.assertEqual([{k: r[k] for k in ("file", "test", "recommend", "why")}
                          for r in data["wall_recommendations"]], recs)
        self.assertIn("wall_recommendations", record.LIST_FIELDS)

    def test_the_slice_record_doc_lists_the_recommendations(self):
        with open(os.path.join(HOME, "docs", "slice-record.md")) as f:
            self.assertIn("wall_recommendations", f.read())

    def test_the_stop_tables_list_the_slice_only_marks_order(self):
        for path, start in ((("skills", "watch", "SKILL.md"), "## The standing orders"),
                            (("README.md",), "### The stops")):
            with open(os.path.join(HOME, *path)) as f:
                table = f.read().split(start)[1].split("\n## ")[0].split("\n### ")[0]
            self.assertIn("slice-only", table, path)

    def miss_record(self, **kw):
        d = with_report(rec(shape_change="no", pitch_contradiction="no", scenario_miss="yes", **kw), "guardian")
        d["checks"]["guardian"] = {"picture_change": "yes"}
        return d

    def fired(self, data, after="guardian"):
        return [f["order"] for f in orders.verdict(data, after, DEFAULT_CONFIG)["fired"]]

    def test_a_scenario_miss_does_not_stop_and_fires_no_accept_moves_or_ready_to_merge(self):
        d = self.miss_record(moved_tests=[{"file": "tests/a.py"}],
                             wall_recommendations=[{"file": "tests/a.py", "test": "t", "recommend": "remove"}])
        self.assertIsNone(self.stop(d, "guardian"))
        self.assertFalse({"accept_moves", "ready_to_merge"} & set(self.fired(d)))

    def test_moved_tests_are_put_to_the_person_when_the_slice_comes_back_with_no_miss(self):
        d = self.miss_record(moved_tests=[{"file": "tests/a.py"}])
        d["scenario_miss"] = "no"
        self.assertEqual(self.stop(d, "guardian")["order"], "accept_moves")

    def test_a_scenario_miss_beside_a_shape_change_still_stops_for_two_people(self):
        d = self.miss_record()
        d["shape_change"] = "yes"
        self.assertEqual(self.stop(d, "guardian")["order"], "shape_or_pitch")

    def test_a_scenario_miss_with_the_budget_spent_stops_for_the_originator(self):
        d = self.miss_record(spend=[{"step": "maker", "usd": 2.5, "tokens": 10}])
        s = self.stop(d, "guardian")
        self.assertEqual((s["order"], s["seat"]), ("budget_spent", "originator"))

    def test_shape_or_pitch_does_not_fire_on_an_accepted_shape_change(self):
        d = with_report(rec(shape_change="accepted", pitch_contradiction="no"), "guardian")
        d["checks"]["guardian"] = {}
        fired = [f["order"] for f in orders.verdict(d, "guardian", DEFAULT_CONFIG)["fired"]]
        self.assertNotIn("shape_or_pitch", fired)
        self.assertEqual(self.stop(d, "guardian")["order"], "ready_to_merge")

    def test_shape_or_pitch_still_fires_on_yes(self):
        d = with_report(rec(shape_change="yes", pitch_contradiction="no"), "guardian")
        d["checks"]["guardian"] = {}
        s = self.stop(d, "guardian")
        self.assertEqual((s["order"], s["seat"]), ("shape_or_pitch", "two_people"))

    def test_an_accepted_shape_does_not_hide_a_pitch_contradiction(self):
        d = with_report(rec(shape_change="accepted", pitch_contradiction="yes"), "guardian")
        d["checks"]["guardian"] = {}
        s = self.stop(d, "guardian")
        self.assertEqual((s["order"], s["seat"]), ("shape_or_pitch", "two_people"))
        self.assertNotIn("shape_change", s["question"])

    def assert_names_the_four_choices(self, question):
        low = question.lower()
        self.assertNotIn("The shape conversation opens", question)
        for choice in ("continue", "reshape the slice", "raise the budget", "second person"):
            self.assertIn(choice, low)

    def test_a_stall_reported_by_the_maker_names_the_four_choices(self):
        d = with_report(rec(), "maker", "stopped", stop={"reason": "repeated_failure"})
        d["checks"]["maker"] = {"suite": "red"}
        self.assert_names_the_four_choices(self.stop(d, "maker")["question"])

    def test_the_same_tests_failing_twice_names_the_stall_and_the_four_choices(self):
        d = with_report(rec(), "maker", "green")
        d["checks"]["maker"] = {"suite": "red", "failing_history": [["test_a (t.T.test_a)"], ["test_a (t.T.test_a)"]]}
        fired = [f for f in orders.verdict(d, "maker", DEFAULT_CONFIG)["fired"] if f["order"] == "repeated_failure"]
        self.assertEqual(len(fired), 1)
        self.assertIn("test_a", fired[0]["question"])
        self.assert_names_the_four_choices(fired[0]["question"])

    def test_a_growing_diff_names_the_stall_and_the_four_choices(self):
        d = with_report(rec(), "maker", "green")
        d["checks"]["maker"] = {"suite": "red", "diff_history": [10, 30]}
        fired = [f for f in orders.verdict(d, "maker", DEFAULT_CONFIG)["fired"] if f["order"] == "diff_growing"]
        self.assertEqual(len(fired), 1)
        self.assertIn("10", fired[0]["question"])
        self.assertIn("30", fired[0]["question"])
        self.assert_names_the_four_choices(fired[0]["question"])

    def test_a_diff_past_the_team_limit_names_the_four_choices(self):
        config = dict(DEFAULT_CONFIG, limits={"max_diff_lines": 100})
        d = with_report(rec(), "maker", "green")
        d["checks"]["maker"] = {"suite": "red", "diff_lines": 150}
        fired = [f for f in orders.verdict(d, "maker", config)["fired"] if f["order"] == "diff_growing"]
        self.assertEqual(len(fired), 1)
        self.assertIn("150", fired[0]["question"])
        self.assert_names_the_four_choices(fired[0]["question"])

    def test_a_picture_change_is_a_proposal_from_the_guardian(self):
        d = with_report(rec(shape_change="no", pitch_contradiction="no"), "guardian")
        d["checks"]["guardian"] = {"picture_change": "yes"}
        s = self.stop(d, "guardian")
        self.assertEqual(s["order"], "accept_moves")
        self.assertIn("The guardian proposes a change to the picture", s["question"])
        self.assertNotIn("the picture changed", s["question"].lower())


class SendBackFromOrdersTest(unittest.TestCase):
    """The send-back is decided by orders.evaluate from the record alone: a fired entry that is not
    blocking and carries send_back = {"to": "maker"|"scenario", "misses": [refs]}."""

    def miss(self, ref="2", to="maker", amend=False, text="the red does not cover it"):
        return {"ref": ref, "to": to, "amend": amend, "text": text}

    def guardian(self, misses, **kw):
        d = with_report(rec(shape_change="no", pitch_contradiction="no", scenario_miss="yes", **kw), "guardian")
        d["checks"]["guardian"] = {"misses": misses}
        return d

    def after_scenario(self, points, **kw):
        d = with_report(rec(**kw), "scenario", "red")
        d["checks"]["scenario"] = {"red_fails": True, "missed_points": points}
        return d

    def verdict(self, data, after):
        return orders.verdict(data, after, DEFAULT_CONFIG)

    def send_backs(self, v):
        return [f for f in v["fired"] if f.get("send_back")]

    def test_orders_sends_a_guardian_miss_back_to_the_maker_without_a_stop(self):
        v = self.verdict(self.guardian([self.miss("2")]), "guardian")
        self.assertIsNone(v["stop"])
        back = self.send_backs(v)
        self.assertEqual([(f["order"], f["blocking"], f["send_back"]) for f in back],
                         [("scenario_miss", False, {"to": "maker", "misses": ["2"]})])

    def test_orders_sends_a_miss_the_red_does_not_cover_to_the_scenario_agent(self):
        v = self.verdict(self.guardian([self.miss("2"), self.miss("10", to="scenario")]), "guardian")
        self.assertIsNone(v["stop"])
        self.assertEqual([f["send_back"] for f in self.send_backs(v)],
                         [{"to": "scenario", "misses": ["10", "2"]}])

    def test_orders_stops_for_a_miss_marked_amend_yes_and_sends_nothing_back(self):
        v = self.verdict(self.guardian([self.miss("2", amend=True)]), "guardian")
        self.assertEqual((v["stop"]["order"], v["stop"]["seat"]), ("scenario_miss", "originator"))
        self.assertEqual(self.send_backs(v), [])

    def test_orders_stops_when_the_same_point_comes_back_worded_differently(self):
        prior = {"order": "scenario_miss", "seat": "watch", "keys": ["2"], "answer": "sent back to the maker"}
        v = self.verdict(self.guardian([self.miss("2", text="said another way entirely")], stops=[prior]), "guardian")
        self.assertEqual((v["stop"]["order"], v["stop"]["seat"]), ("scenario_miss", "originator"))
        self.assertEqual(self.send_backs(v), [])

    def test_orders_sends_back_a_new_point_after_an_earlier_send_back_for_another(self):
        prior = {"order": "scenario_miss", "seat": "watch", "keys": ["3"], "answer": "sent back to the maker"}
        v = self.verdict(self.guardian([self.miss("2")], stops=[prior]), "guardian")
        self.assertIsNone(v["stop"])
        self.assertEqual(len(self.send_backs(v)), 1)

    def test_orders_sends_nothing_back_beside_a_shape_change(self):
        d = self.guardian([self.miss("2")])
        d["shape_change"] = "yes"
        v = self.verdict(d, "guardian")
        self.assertEqual(v["stop"]["order"], "shape_or_pitch")
        self.assertEqual(self.send_backs(v), [])

    def test_orders_sends_nothing_back_when_the_budget_is_spent(self):
        v = self.verdict(self.guardian([self.miss("2")], spend=[{"step": "maker", "usd": 2.5, "tokens": 10}]), "guardian")
        self.assertEqual(v["stop"]["order"], "budget_spent")
        self.assertEqual(self.send_backs(v), [])

    def test_orders_sends_uncovered_scenario_points_back_to_the_scenario_agent(self):
        v = self.verdict(self.after_scenario(["3", "5"]), "scenario")
        self.assertIsNone(v["stop"])
        self.assertEqual([(f["order"], f["blocking"], f["send_back"]) for f in self.send_backs(v)],
                         [("red_misses_point", False, {"to": "scenario", "misses": ["3", "5"]})])

    def test_orders_stops_when_the_same_uncovered_point_comes_back(self):
        prior = {"order": "red_misses_point", "seat": "watch", "keys": ["3"], "answer": "sent back to the scenario"}
        v = self.verdict(self.after_scenario(["3"], stops=[prior]), "scenario")
        self.assertEqual((v["stop"]["order"], v["stop"]["seat"]), ("red_misses_point", "originator"))
        self.assertEqual(self.send_backs(v), [])


class GuardianFiveChecksTest(unittest.TestCase):
    def read(self, *path):
        with open(os.path.join(HOME, *path)) as f:
            return f.read()

    def test_the_fifth_check_names_the_three_recommendations(self):
        text = self.read("skills", "guardian", "SKILL.md").split("## The five checks")[1].split("## The evidence rule")[0]
        self.assertIn("5. ", text)
        self.assertIn("slice-only", text)
        self.assertIn("should not join the wall", text)
        self.assertIn("removed", text)

    def test_the_packet_template_has_a_section_for_wall_recommendations(self):
        text = self.read("skills", "guardian", "packet.md")
        self.assertIn("## 5. ", text)

if __name__ == "__main__":
    unittest.main()
