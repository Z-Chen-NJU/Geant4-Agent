from __future__ import annotations

import unittest

from core.dialogue.grounding import enforce_message_grounding


class DialogueGroundingTest(unittest.TestCase):
    def test_conflicting_physics_mention_is_replaced(self) -> None:
        cfg = {
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "json"},
            "source": {"type": "point", "particle": "gamma"},
        }
        msg = "好的，已配置为 QBBC，输出 root。"
        out = enforce_message_grounding(msg, config=cfg, action="finalize", lang="zh")
        self.assertIn("FTFP_BERT", out)
        self.assertIn("json", out)
        self.assertNotIn("QBBC", out)


if __name__ == "__main__":
    unittest.main()

