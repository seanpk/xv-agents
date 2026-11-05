import os
import re
import unittest

from helpers import HOME


def brief(*parts):
    with open(os.path.join(HOME, *parts)) as f:
        return f.read()


def section(text, heading):
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


class PictureInTheBriefsTest(unittest.TestCase):
    def test_the_maker_may_read_the_picture_and_may_not_edit_it(self):
        text = brief("skills", "maker", "SKILL.md")
        may_not = section(text, "May not")
        self.assertNotRegex(may_not, r"(?i)read or edit[^\n]*picture\.md")
        self.assertRegex(may_not, r"(?im)^- edit[^\n]*\.xv/picture\.md")
        self.assertRegex(text, r"(?i)may read[^\n]*\.xv/picture\.md")

    def test_the_maker_pulls_the_binding_decisions_before_it_writes_code(self):
        text = brief("skills", "maker", "SKILL.md")
        self.assertRegex(text, r"(?i)binding decisions[^\n]*before[^\n]*code|before[^\n]*code[^\n]*binding decisions")

    def test_the_scenario_agent_may_read_the_picture_and_pull_the_binding_decisions(self):
        text = brief("skills", "scenario", "SKILL.md")
        self.assertIn(".xv/picture.md", section(text, "Read"))
        self.assertRegex(text, r"(?i)binding decisions")

    def test_the_scenario_brief_says_each_numbered_point_must_be_in_covers_or_not_covered(self):
        text = brief("skills", "scenario", "SKILL.md")
        self.assertRegex(text, r"(?is)each numbered point[^\n]*amendment[^\n]*covers[^\n]*not_covered")

    def test_the_watch_may_edit_the_picture_when_a_person_directs_it(self):
        text = brief("skills", "watch", "SKILL.md")
        self.assertIn("edit the pitch, or edit the picture unless a person directs it", text)
        self.assertRegex(text, r"(?is)picture[^\n]*own commit[^\n]*(names|naming)[^\n]*person")


OPENERS = [
    "skills/cleaner/SKILL.md", "skills/forecaster/SKILL.md", "skills/guardian/SKILL.md",
    "skills/listener/SKILL.md", "skills/maker/SKILL.md", "skills/maker/prototype.md",
    "skills/scenario/SKILL.md", "skills/watch/SKILL.md", "skills/xv-check/SKILL.md",
    "skills/xv-init/SKILL.md", "skills/xv-init/outsider-read.md", "skills/xv-promote/SKILL.md",
    "skills/xv-retro/SKILL.md", "skills/xv-retro/retro-brief.md", "skills/xv-slice/SKILL.md",
]
OWN = ("Own the result: even when agents write all of the code, a person is responsible "
       "for what it does. An agent may stop. It may not decide.")

# The rest each brief already had after the stop line. The watch brief is
# absent: the scenario amendment lets it drop its old last sentence.
OPENER_RESTS = {
    "skills/maker/prototype.md": "You do not pick, and you do not say which version is better.",
    "skills/guardian/SKILL.md": "You give findings. You never fix, approve, or merge.",
    "skills/xv-promote/SKILL.md": "You list, search and draft. People promote, approve, post and decide.",
    "skills/xv-init/outsider-read.md": "You describe; you do not decide what the system is for.",
    "skills/xv-init/SKILL.md": "You may not invent what the system is for.",
    "skills/xv-retro/SKILL.md": ("The retro proposes. The person who set the work going picks. "
                                 "A standard enters `.xv/standards.md` only when they accept it."),
    "skills/xv-check/SKILL.md": "You report; people remove, keep, or re-agree.",
    "skills/xv-slice/SKILL.md": ("The scenario is the person's statement of what must be true; "
                                 "you write it down, you do not choose it."),
    "skills/maker/SKILL.md": ("Stopping is a good outcome. A green you had to cheat for is the "
                              "worst one."),
    "skills/xv-retro/retro-brief.md": "You propose; you never write a rule, a check, or a brief.",
}


class OwnTheResultTest(unittest.TestCase):
    def test_each_of_the_15_brief_openers_names_own_the_result_first(self):
        for rel in OPENERS:
            with self.subTest(brief=rel):
                lines = brief(*rel.split("/")).splitlines()
                stop = [l for l in lines if "An agent may stop. It may not decide." in l]
                self.assertTrue(stop, "no stop line")
                self.assertTrue(stop[0].startswith(OWN), stop[0])

    def test_each_opener_keeps_its_agent_specific_rest_after_the_stop_line(self):
        for rel, rest in OPENER_RESTS.items():
            with self.subTest(brief=rel):
                stop = [l for l in brief(*rel.split("/")).splitlines()
                        if "An agent may stop. It may not decide." in l]
                self.assertEqual(stop[0], OWN + " " + rest)

    def test_the_one_rule_label_is_gone_from_the_openers(self):
        for rel in OPENERS:
            with self.subTest(brief=rel):
                self.assertNotIn("The one rule:", brief(*rel.split("/")))

    def test_briefs_doc_says_own_the_result_opens_each_brief_and_the_stop_line_stays(self):
        every = section(brief("docs", "briefs.md"), "Every brief")
        self.assertRegex(every, r"(?i)own the result opens each brief")
        self.assertRegex(every, r"(?i)stop line")
        self.assertNotRegex(every, r"(?i)the one rule opens")

    def test_picture_item_13_says_own_the_result_opens_each_brief(self):
        item = re.search(r"^13\. (.*)$", brief(".xv", "picture.md"), re.M).group(1)
        self.assertRegex(item, r"(?i)own the result")
        self.assertRegex(item, r"(?i)stop line")
        self.assertNotRegex(item, r"(?i)opens with the one rule")

    def test_ci_pins_and_readme_mentions_say_v0_4_1(self):
        for rel in ["ci/github/xv-wall.yml", "ci/github/xv-guardian.yml", "ci/github/xv-listener.yml"]:
            with self.subTest(file=rel):
                text = brief(*rel.split("/"))
                self.assertRegex(text, r"ref: v0\.4\.1")
                self.assertNotIn("v0.4.0", text)
        readme = brief("README.md")
        self.assertIn("git checkout v0.4.1", readme)
        self.assertIn("pin `v0.4.1`", readme)
        self.assertNotIn("git checkout v0.4.0", readme)
        self.assertNotIn("pin `v0.4.0`", readme)


def paragraphs(text, *words):
    """Paragraphs and list items of a brief that hold every word, case aside."""
    blocks = re.split(r"\n\s*\n|\n(?=\d+[a-z]?\. |- )", text)
    return [b for b in blocks if all(w.lower() in b.lower() for w in words)]


class ScenarioCatchesTest(unittest.TestCase):
    def test_the_scenario_brief_marks_a_one_time_wording_check_slice_only(self):
        text = brief("skills", "scenario", "SKILL.md")
        self.assertTrue(paragraphs(text, "slice_only", "wording", "README"), "no slice_only line for a wording change")
        self.assertTrue(paragraphs(text, "slice_only", "version pin"))

    def test_the_scenario_report_names_each_old_test_the_red_forces_to_change(self):
        text = brief("skills", "scenario", "SKILL.md")
        hits = paragraphs(text, "old test", "force", "report", "why")
        self.assertTrue([h for h in hits if "file" in h and "test" in h], "no report line naming old tests")

    def test_the_scenario_report_names_the_may_not_files_the_red_needs_changed(self):
        text = brief("skills", "scenario", "SKILL.md")
        hits = paragraphs(text, "may-not", "report", ".xv/picture.md")
        self.assertTrue(hits, "no report line naming may-not files")

    def test_the_maker_may_change_a_named_old_test_without_stopping_and_records_it(self):
        text = brief("skills", "maker", "SKILL.md")
        hits = paragraphs(text, "scenario agent", "report", "names", "record")
        self.assertTrue([h for h in hits if "stop" in h.lower() and "test" in h.lower()],
                        "the maker brief does not let it change a test the report names")

    def test_the_maker_may_change_a_named_may_not_file_and_no_other(self):
        text = brief("skills", "maker", "SKILL.md")
        hits = paragraphs(text, "scenario agent", "report", "may-not")
        self.assertTrue([h for h in hits if re.search(r"(?i)no other|only", h)],
                        "the maker brief does not limit the change to the files the report names")

    def test_an_unnamed_old_test_still_follows_the_recorded_move_rule(self):
        text = brief("skills", "maker", "SKILL.md")
        self.assertRegex(text, r"(?is)not named[^\n]*(rule|stop|scenario forces)")

    def test_the_guardian_lists_the_may_not_file_changes_in_the_packet(self):
        text = brief("skills", "guardian", "SKILL.md") + brief("skills", "guardian", "packet.md")
        self.assertTrue(paragraphs(text, "may-not", "packet", "scenario agent"),
                        "the guardian brief does not list the changes the scenario agent's report allowed")

    def test_the_scenario_brief_asks_a_red_case_for_each_way_a_value_can_be_wrong(self):
        text = brief("skills", "scenario", "SKILL.md")
        hits = paragraphs(text, "missing", "empty", "wrong type", "not_covered")
        self.assertTrue([h for h in hits if re.search(r"(?i)on the list", h)],
                        "no line asks for missing, empty, wrong type and off-list cases")
        self.assertTrue([h for h in hits if re.search(r"(?i)flag|field|report key", h)])

    def test_the_scenario_brief_asks_a_case_where_a_read_only_agent_claims_a_persons_word(self):
        text = brief("skills", "scenario", "SKILL.md")
        hits = paragraphs(text, "read-only agent", "only a person")
        self.assertTrue(hits, "no case for an agent claiming what only a person may give")

    def test_the_watch_names_four_things_in_each_amendment_it_drafts(self):
        text = brief("skills", "watch", "SKILL.md")
        hits = paragraphs(text, "amendment", "exact name", "where", "when it applies", "does not cover", "may-not")
        self.assertTrue([h for h in hits if "binding decision" in h.lower()],
                        "no watch line lists the four things an amendment names")


if __name__ == "__main__":
    unittest.main()
