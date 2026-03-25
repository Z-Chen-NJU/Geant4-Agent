from __future__ import annotations

import unittest
from unittest.mock import patch

from ui.web import legacy_api


class LegacyApiGlueTest(unittest.TestCase):
    def setUp(self) -> None:
        legacy_api.SESSIONS.clear()

    def test_legacy_step_empty_text_rejected(self) -> None:
        result = legacy_api.legacy_step({"text": "", "session_id": "s1"})
        self.assertEqual(result["error"], "missing text")

    def test_legacy_solve_empty_text_rejected(self) -> None:
        result = legacy_api.legacy_solve({"text": ""})
        self.assertEqual(result["error"], "missing text")


if __name__ == "__main__":
    unittest.main()
