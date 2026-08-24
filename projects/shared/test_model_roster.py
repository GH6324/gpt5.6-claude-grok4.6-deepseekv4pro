from __future__ import annotations

import unittest

from model_roster import claude_line, claude_labels, resolve_claude_model


class RosterTests(unittest.TestCase):
    def test_core_family_present(self) -> None:
        labels = claude_labels()
        for name in ("Opus 5", "Fable 5", "4.8", "Opus 4.6", "Sonnet 4.6"):
            self.assertIn(name, labels)

    def test_aliases(self) -> None:
        self.assertEqual(resolve_claude_model("opus5"), "opus-5")
        self.assertEqual(resolve_claude_model("Fable 5"), "fable-5")
        self.assertEqual(resolve_claude_model("4.8"), "claude-4.8")

    def test_line_has_separators(self) -> None:
        line = claude_line()
        self.assertIn("Opus 5", line)
        self.assertIn("Fable 5", line)
        self.assertIn("4.8", line)


if __name__ == "__main__":
    unittest.main()
