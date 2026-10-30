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


if __name__ == "__main__":
    unittest.main()
