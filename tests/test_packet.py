import os
import tempfile
import unittest

from helpers import HOME  # noqa: F401
import packet

GOOD = """---
slice: s1
shape_change: yes
pitch_contradiction: no
door: two-way
---

# Packet

## 1. Shape

- A new module `pantry/grocer.py` calls out of the process (pantry/grocer.py:13).
- This feels like a big change to me.
- None beyond that.

## 2. Pitch

- "It never sends the household's data anywhere else" (.xv/pitch.md:15).

## Door

**Door:** two-way.
"""


class PacketTest(unittest.TestCase):
    def test_an_uncited_finding_is_dropped_and_kept_visible(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(GOOD)
        res = packet.fix(f.name)
        text = open(f.name).read()
        os.unlink(f.name)
        self.assertEqual(res["problems"], [])
        self.assertEqual(res["dropped"], ["- This feels like a big change to me."])
        self.assertIn("## Dropped by the evidence rule", text)
        self.assertIn("None beyond that.", text.split("## Dropped")[0])

    def test_the_fixed_fields_must_be_yes_or_no(self):
        _, _, problems, _ = packet.lint(GOOD.replace("shape_change: yes", "shape_change: maybe"))
        self.assertTrue(any("shape_change" in p for p in problems))

    def test_shape_change_may_be_accepted_when_a_decision_already_accepted_it(self):
        _, _, problems, _ = packet.lint(GOOD.replace("shape_change: yes", "shape_change: accepted"))
        self.assertEqual(problems, [])

    def test_pitch_contradiction_may_not_be_accepted(self):
        _, _, problems, _ = packet.lint(GOOD.replace("pitch_contradiction: no", "pitch_contradiction: accepted"))
        self.assertTrue(any("pitch_contradiction" in p for p in problems))

    def test_scenario_miss_must_be_yes_or_no(self):
        with_field = GOOD.replace("door: two-way\n---", "door: two-way\nscenario_miss: no\n---", 1)
        _, _, problems, _ = packet.lint(with_field)
        self.assertEqual(problems, [])
        _, _, problems, _ = packet.lint(with_field.replace("scenario_miss: no", "scenario_miss: maybe"))
        self.assertTrue(any("scenario_miss" in p for p in problems))
        # optional: a packet without the field is not a lint problem
        _, _, problems, _ = packet.lint(GOOD)
        self.assertFalse(any("scenario_miss" in p for p in problems))

    def test_the_packet_template_shows_the_fields_and_a_misses_section(self):
        text = open(os.path.join(HOME, "skills", "guardian", "packet.md")).read()
        front = text.split("---")[1]
        self.assertRegex(front, r"(?m)^scenario_miss: ")
        self.assertRegex(front, r"(?m)^shape_change: .*accepted")
        self.assertIn("accepted_by", front)
        self.assertRegex(text, r"(?im)^## .*miss")

    def test_the_guardian_brief_names_scenario_miss_and_what_a_miss_cites(self):
        text = open(os.path.join(HOME, "skills", "guardian", "SKILL.md")).read()
        self.assertIn("scenario_miss", text)
        self.assertRegex(text, r"(?i)binding decision")

    def test_a_miss_is_keyed_by_its_point_not_by_its_wording(self):
        def ref(line):
            body = "## Scenario misses\n\n- %s (evidence: tests/test_red.py:7)\n" % line
            return packet.misses(body)[0]["ref"]
        self.assertEqual(ref("Point 2 is not met: milk is left out, to: maker"),
                         ref("2: the list still skips milk, to: maker"))
        self.assertEqual(ref("Decision 10 is broken: the order sits in run.py"),
                         ref("decision 10: another wording"))

    MISSES = GOOD.replace("door: two-way\n---", "door: two-way\nscenario_miss: yes\n---", 1) + """
## Scenario misses

- 2: the list leaves out milk that runs out today (evidence: tests/test_store.py:7; to: maker)
- amendment 1, item 3: no heading for the section (evidence: a run of `xv packet lint`; to: scenario)
- decision 4: breaks the by-name rule (evidence: pantry/store.py:12; to: maker)
- The list feels thin (evidence: tests/test_store.py:9; to: maker)
- 3: the stop is missing; to: maker
"""

    def fixed(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(text)
        packet.fix(f.name)
        out = open(f.name).read()
        os.unlink(f.name)
        return out

    def test_a_miss_that_names_no_point_or_decision_or_no_evidence_leaves_the_misses_section(self):
        out = self.fixed(self.MISSES)
        kept, dropped = out.split("## Dropped")[0], out.split("## Dropped")[1]
        self.assertIn("## Scenario misses", kept)
        for line in ("2: the list leaves out milk", "amendment 1, item 3", "decision 4"):
            self.assertIn(line, kept)
        for line in ("The list feels thin", "3: the stop is missing"):
            self.assertNotIn(line, kept)
            self.assertIn(line, dropped)
        self.assertIn("scenario_miss: yes", out.split("---")[1])

    def test_with_no_miss_left_scenario_miss_reads_as_no(self):
        only_bad = self.MISSES.split("- 2:")[0] + (
            "- The list feels thin (evidence: tests/test_store.py:9; to: maker)\n")
        out = self.fixed(only_bad)
        self.assertIn("scenario_miss: no", out.split("---")[1])
        self.assertNotIn("scenario_miss: yes", out)


class PacketFieldDocsTest(unittest.TestCase):
    """Every value the code allows for a packet field is named where the docs name the field."""

    FIELDS = ("shape_change", "pitch_contradiction")
    CANDIDATES = ("yes", "no", "accepted")

    def allowed(self, field):
        # asked of the code itself: the values the packet lint lets through
        return [v for v in self.CANDIDATES
                if not any(field in p for p in packet.lint(GOOD.replace(f"{field}: yes", f"{field}: {v}")
                                                           .replace(f"{field}: no", f"{field}: {v}"))[2])]

    def read(self, *path):
        with open(os.path.join(HOME, *path)) as f:
            return f.read()

    def lines_naming(self, text, field):
        return [ln for ln in text.splitlines() if field in ln]

    def check(self, text, where, rows_only=False):
        for field in self.FIELDS:
            lines = self.lines_naming(text, field)
            if rows_only:
                lines = [ln for ln in lines if ln.lstrip().startswith("|")]
            for value in self.allowed(field):
                self.assertTrue(any(value in ln for ln in lines),
                                f"{where} never says {value} on a line that names {field}")

    def test_the_code_allows_accepted_for_shape_change_only(self):
        self.assertEqual(self.allowed("shape_change"), ["yes", "no", "accepted"])
        self.assertEqual(self.allowed("pitch_contradiction"), ["yes", "no"])

    def test_the_packet_template_names_every_allowed_value(self):
        self.check(self.read("skills", "guardian", "packet.md"), "skills/guardian/packet.md")

    def test_the_readme_names_every_allowed_value(self):
        self.check(self.read("README.md"), "README.md")

    def test_the_docs_tables_name_every_allowed_value(self):
        docs = os.path.join(HOME, "docs")
        for name in sorted(os.listdir(docs)):
            text = self.read("docs", name)
            if any(ln.lstrip().startswith("|") and f in ln for ln in text.splitlines() for f in self.FIELDS):
                self.check(text, f"docs/{name}", rows_only=True)

    def test_the_slice_record_doc_gives_the_stop_shape_and_the_decision_rules(self):
        text = self.read("docs", "slice-record.md")
        stops = [ln for ln in text.splitlines() if ln.lstrip().startswith("| `stops`")][0]
        for key in ("accepted_wall", "refused_wall", "settled"):
            self.assertIn(key, stops)
        decisions = [ln for ln in text.splitlines() if ln.lstrip().startswith("| `decisions`")][0]
        self.assertIn("ready_to_merge", decisions)
        self.assertIn("list", decisions)


class CrowdedPictureNoteTest(unittest.TestCase):
    """defects-tools 15: the note on crowded picture lines is left once, and an old note is stripped only where it starts a line."""

    NOTE = "Note: the picture should hold one sentence per line;"

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xv-note-")
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        os.makedirs(os.path.join(self.tmp, ".xv"))
        self.picture("One sentence. Another sentence on the same line.\n")
        self.path = os.path.join(self.tmp, "packet.md")

    def picture(self, text):
        with open(os.path.join(self.tmp, ".xv", "picture.md"), "w") as f:
            f.write(text)

    def packet(self, text):
        with open(self.path, "w") as f:
            f.write(text)

    def run_note(self):
        packet.note_crowded_picture_lines(self.path, self.tmp)
        with open(self.path) as f:
            return f.read()

    def starting_a_line(self, text):
        return [ln for ln in text.splitlines() if ln.startswith(self.NOTE)]

    def test_a_second_run_leaves_exactly_one_note(self):
        self.packet(GOOD)
        self.run_note()
        text = self.run_note()
        self.assertEqual(len(self.starting_a_line(text)), 1, text)
        self.assertEqual(text.count(self.NOTE), 1, text)

    def test_a_note_quoted_inside_a_line_is_not_stripped(self):
        quote = f"- The guardian saw that {self.NOTE} more than one sentence on .xv/picture.md:9 (evidence: x:1)"
        self.packet(GOOD.rstrip("\n") + "\n\n" + quote + "\n")
        text = self.run_note()
        self.assertIn(quote, text, "a line that quotes the note lost its text")
        self.assertEqual(len(self.starting_a_line(text)), 1, text)

    def test_an_old_note_that_starts_a_line_is_replaced_by_the_new_one(self):
        self.packet(GOOD.rstrip("\n") + f"\n\n{self.NOTE} more than one sentence on .xv/picture.md:9.\n")
        text = self.run_note()
        self.assertEqual(len(self.starting_a_line(text)), 1, text)
        self.assertNotIn(".xv/picture.md:9", text)
        self.assertIn(".xv/picture.md:1", text)

    def test_an_old_note_goes_when_no_picture_line_is_crowded(self):
        self.packet(GOOD.rstrip("\n") + f"\n\n{self.NOTE} more than one sentence on .xv/picture.md:9.\n")
        self.picture("One sentence per line.\n")
        self.assertEqual(self.starting_a_line(self.run_note()), [])


if __name__ == "__main__":
    unittest.main()
