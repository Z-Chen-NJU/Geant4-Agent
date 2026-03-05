from __future__ import annotations

import unittest

from core.orchestrator.session_manager import _apply_explicit_user_controls
from core.orchestrator.types import CandidateUpdate, Intent, Producer


class ExplicitControlsTest(unittest.TestCase):
    def test_explicit_set_targets_override_spurious_question_intent(self) -> None:
        user_candidate = CandidateUpdate(
            producer=Producer.USER_EXPLICIT,
            intent=Intent.QUESTION,
            target_paths=[],
            updates=[],
            confidence=0.8,
            rationale="llm_user_candidate",
        )
        out = _apply_explicit_user_controls(
            user_candidate,
            {
                "intent": Intent.SET,
                "target_paths": ["physics.physics_list", "output.format"],
            },
        )
        self.assertEqual(out.intent, Intent.SET)
        self.assertEqual(sorted(out.target_paths), ["output.format", "physics.physics_list"])


if __name__ == "__main__":
    unittest.main()

