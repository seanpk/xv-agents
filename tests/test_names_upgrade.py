import unittest

from helpers import HOME  # noqa: F401
import orders
from xvlib import DEFAULT_CONFIG, split_front_matter


OLD = """---
id: s1
set_by: pat
scenario_miss: yes
old_tests_forced: [{"file": "t.py", "test": "a", "why": "w"}]
may_not_files: [{"file": ".xv/picture.md", "why": "w"}]
amended_at_report: 2
moved_tests: 3
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 5}], "shape": "narrow", "breadth": "one line"}
red: {"files": ["t.py"], "command": "true", "watch_first_green": "watch it"}
stops: [{"order": "accept_moves", "seat": "originator", "sent_back": true, "sent_back_to": "maker"}, {"order": "red_misses_point", "seat": "watch", "keys": ["1"]}]
checks: {"scenario": {"missed_points": ["1. a"], "red_joined": "a; b", "covered_kept": [{"item": "x", "test": "t"}]}}
---
body
"""


class OldNamesAreStillReadTest(unittest.TestCase):
    def setUp(self):
        self.data, _ = split_front_matter(OLD)

    def test_a_record_written_before_the_rename_reads_under_the_new_names(self):
        d = self.data
        self.assertEqual((d["originator"], d["change_misses_scenario"], d["reports_before_amend"]), ("pat", "yes", 2))
        self.assertEqual(d["old_tests_to_move"][0]["file"], "t.py")
        self.assertEqual(d["may_not_files_needed"][0]["file"], ".xv/picture.md")
        self.assertEqual(d["moved_tests_count"], 3)
        self.assertEqual(d["forecast"]["rows"][0]["tokens"], 5)
        self.assertEqual((d["forecast"]["shape_breadth"], d["forecast"]["shape_note"]), ("narrow", "one line"))
        self.assertEqual(d["red"]["watch_before_merge"], "watch it")
        for old in ("set_by", "scenario_miss", "old_tests_forced", "may_not_files", "amended_at_report"):
            self.assertNotIn(old, d)

    def test_old_stops_and_checks_read_under_the_new_names(self):
        first, second = self.data["stops"]
        self.assertEqual((first["order"], first["sendback"], first["sendback_to"]), ("moves_to_accept", True, "maker"))
        self.assertEqual(second["order"], "report_misses_outcome")
        scenario = self.data["checks"]["scenario"]
        self.assertEqual((scenario["missed_outcomes"], scenario["red_joined_unsafely"]), (["1. a"], "a; b"))
        self.assertEqual(scenario["covered_kept"][0]["outcome"], "x")

    def test_an_old_record_still_counts_a_repeated_miss(self):
        d = dict(self.data, stops=[{"order": "report_misses_outcome", "seat": "watch", "keys": ["1"]}],
                 checks={"reports": [], "scenario": {}})
        self.assertEqual(orders.miss_run(d, "report_misses_outcome", "scenario"), {"1": 1})
        self.assertEqual(DEFAULT_CONFIG is not None, True)


if __name__ == "__main__":
    unittest.main()
