import unittest

from helpers import HOME  # noqa: F401
import agentcli


class CapsTest(unittest.TestCase):
    def test_claude_gets_dollars_and_turns_before_the_prompt(self):
        argv = agentcli.with_caps(["claude", "-p", "--model", "sonnet", "{prompt}"], {"usd": 2, "turns": 30})
        self.assertEqual(argv[-5:], ["--max-budget-usd", "2", "--max-turns", "30", "{prompt}"])

    def test_grok_gets_turns_outside_its_prompt_flag(self):
        argv = agentcli.with_caps(["grok", "-m", "grok-4.7", "-p", "{prompt}"], {"usd": 2, "turns": 30})
        self.assertEqual(argv, ["grok", "-m", "grok-4.7", "--max-turns", "30", "-p", "{prompt}"])

    def test_opencode_has_no_cap(self):
        argv = ["opencode", "run", "{prompt}"]
        self.assertEqual(agentcli.with_caps(argv, {"usd": 2, "turns": 30}), argv)

    def test_model_and_harness_from_argv(self):
        argv = ["opencode", "run", "--model", "ollama/gpt-oss:20b", "{prompt}"]
        self.assertEqual((agentcli.harness_of(argv), agentcli.model_of(argv)), ("opencode", "gpt-oss:20b"))


if __name__ == "__main__":
    unittest.main()
