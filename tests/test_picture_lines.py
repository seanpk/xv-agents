import json
import os
import re
import shutil
import tempfile

from helpers import HOME, RepoCase

import check

def read(*parts):
    with open(os.path.join(HOME, *parts), encoding="utf-8") as f:
        return f.read()


def lines_outside_fences(text):
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield n, line


class ThePictureIsOneSentencePerLineTest(RepoCase):
    fixture = False

    def test_a_list_items_extra_lines_line_up_with_the_items_text(self):
        in_item, width, bad = False, 0, []
        for n, line in lines_outside_fences(read(".xv", "picture.md")):
            m = re.match(r"^((?:[-*]|\d+\.) +)", line)
            if m:
                in_item, width = True, len(m.group(1))
            elif not line.strip() or line.startswith("#"):
                in_item = False
            elif in_item and re.match(r"^ +[-*] ", line):
                continue  # a nested list keeps its own indent
            elif in_item and not re.match(r"^ {%d}\S" % width, line):
                bad.append(n)
        self.assertEqual(bad, [])

    def relaxations_of(self, text):
        tmp = tempfile.mkdtemp(prefix="xv-pic-")
        self.addCleanup(shutil.rmtree, tmp, True)
        os.makedirs(os.path.join(tmp, ".xv"))
        shutil.copy(os.path.join(HOME, ".xv", "config.yml"), os.path.join(tmp, ".xv", "config.yml"))
        with open(os.path.join(tmp, ".xv", "picture.md"), "w") as f:
            f.write(text)
        return [h["why"] for h in check.relaxations(tmp) if h["where"].startswith(".xv/picture.md")]

    def test_xv_check_sees_a_relaxing_sentence_on_its_own_line_as_in_a_wrapped_paragraph(self):
        for text in ("Merge automatically when nothing is found.\n",
                     "A sentence before. Merge automatically when nothing is found. One after.\n"):
            self.assertIn("merges or approves without a person", self.relaxations_of(text))


class TheBriefsStateTheRuleTest(RepoCase):
    fixture = False

    def rule(self, *path):
        text = read(*path)
        self.assertRegex(text, r"(?i)one sentence per line")
        self.assertRegex(text, r"(?i)line[sd]? up with the item's text")

    def test_the_guardian_brief_states_it(self):
        self.rule("skills", "guardian", "SKILL.md")

    def test_the_maker_brief_states_it(self):
        self.rule("skills", "maker", "SKILL.md")

    def test_the_watch_brief_states_it(self):
        self.rule("skills", "watch", "SKILL.md")

    def test_the_xv_init_brief_states_it_so_an_adopting_repo_gets_it(self):
        self.rule("skills", "xv-init", "SKILL.md")


class ALongPictureLineGetsAPacketNoteTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice()

    def packet_after(self, picture_text):
        with open(os.path.join(self.wt, ".xv", "picture.md"), "w") as f:
            f.write(picture_text)
        packet = os.path.join(self.wt, "hand-packet.md")
        with open(packet, "w") as f:
            f.write("---\nshape_change: no\npitch_contradiction: no\ndoor: two-way\nexpected_moves: 0\n---\nA packet.\n")
        self.xv("record", "packet", "s1", packet, cwd=self.wt)
        self.record = json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)
        with open(packet) as f:
            return f.read()

    def noted_lines(self, packet):
        return sorted({int(n) for n in re.findall(r"picture\.md:(\d+)", packet)})

    def test_a_line_with_two_sentences_is_named_in_the_packet_by_its_line_number(self):
        packet = self.packet_after("# Picture\n\nOne sentence.\nThis is one. And this is two.\nThree.\n")
        self.assertEqual(self.noted_lines(packet), [4])

    def test_it_is_a_note_and_not_a_stop(self):
        self.packet_after("# Picture\n\nThis is one. And this is two.\n")
        self.assertEqual([s for s in self.record["stops"] if "picture" in json.dumps(s).lower()], [])

    def test_a_picture_with_one_sentence_per_line_gets_no_note(self):
        packet = self.packet_after("# Picture\n\nOne.\nTwo.\n- An item.\n  Its second sentence.\n")
        self.assertEqual(self.noted_lines(packet), [])

    def test_a_full_stop_inside_backticks_does_not_count(self):
        packet = self.packet_after("# Picture\n\nRun `a. B` and see.\n")
        self.assertEqual(self.noted_lines(packet), [])

    def test_a_full_stop_not_followed_by_a_capital_does_not_count(self):
        packet = self.packet_after("# Picture\n\nIt is v0.5. then it moves; e.g. foo, 1.5 times.\n")
        self.assertEqual(self.noted_lines(packet), [])

    def test_a_full_stop_with_no_space_after_it_does_not_count(self):
        packet = self.packet_after("# Picture\n\nSee file.Next and x.Y.\n")
        self.assertEqual(self.noted_lines(packet), [])

    def test_a_list_item_line_with_two_sentences_is_named(self):
        packet = self.packet_after("# Picture\n\n- An item. With two.\n  Fine here.\n")
        self.assertEqual(self.noted_lines(packet), [3])

    def test_a_list_marker_is_not_a_sentence_end(self):
        packet = self.packet_after("# Picture\n\n1. An item.\n12. Another item.\n    Its extra line.\n* A star item.\n- A dash item.\n")
        self.assertEqual(self.noted_lines(packet), [])

    def test_a_numbered_item_with_two_sentences_is_named(self):
        packet = self.packet_after("# Picture\n\n1. An item. With two.\n")
        self.assertEqual(self.noted_lines(packet), [3])

    def record_packet_again(self, packet):
        self.xv("record", "packet", "s1", packet, cwd=self.wt)
        with open(packet) as f:
            return f.read()

# What a person should watch on the first green run: open .xv/picture.md and read a few list items.
# Each sentence should sit on its own line, with a list item's extra lines lined up with the item's text, and the
# packet of the slice should carry no picture-line note. Then put two sentences on one line and run
# `xv record packet`: the packet should name that line, and the slice should not stop.
