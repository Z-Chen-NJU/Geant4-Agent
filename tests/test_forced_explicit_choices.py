from __future__ import annotations

import unittest

from core.orchestrator.session_manager import _build_forced_explicit_candidate
from core.orchestrator.types import CandidateUpdate, Intent, Producer


class ForcedExplicitChoicesTest(unittest.TestCase):
    def test_builds_physics_and_output_updates(self) -> None:
        user_candidate = CandidateUpdate(
            producer=Producer.USER_EXPLICIT,
            intent=Intent.SET,
            target_paths=["physics.physics_list", "output.format"],
            updates=[],
            confidence=1.0,
            rationale="test",
        )
        forced = _build_forced_explicit_candidate(
            text="Use QBBC physics list and output root.",
            normalized_text="",
            user_candidate=user_candidate,
            turn_id=1,
        )
        self.assertIsNotNone(forced)
        assert forced is not None
        values = {u.path: u.value for u in forced.updates}
        self.assertEqual(values.get("physics.physics_list"), "QBBC")
        self.assertEqual(values.get("output.format"), "root")


if __name__ == "__main__":
    unittest.main()

