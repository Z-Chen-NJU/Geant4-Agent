from __future__ import annotations

import unittest

from core.orchestrator.turn_transaction import begin_turn, commit_turn
from core.orchestrator.types import ConstraintItem, LockReason, Phase, Scope, SessionState


class TurnTransactionTest(unittest.TestCase):
    def test_draft_isolation_until_commit(self) -> None:
        state = SessionState(
            session_id="s1",
            phase=Phase.GEOMETRY,
            turn_id=1,
            config={"geometry": {"structure": "single_box"}},
            constraint_ledger=[
                ConstraintItem(
                    path="geometry.structure",
                    value="single_box",
                    locked=True,
                    reason_code=LockReason.USER_EXPLICIT,
                    scope=Scope.EXACT,
                    source="user_explicit",
                    turn_id=1,
                )
            ],
            field_sources={"geometry.structure": "user_explicit"},
        )

        draft = begin_turn(state)
        draft.config["geometry"]["structure"] = "single_tubs"
        draft.constraint_ledger[0].locked = False
        draft.field_sources["geometry.structure"] = "llm_semantic_frame"
        draft.phase = Phase.MATERIALS

        self.assertEqual(state.config["geometry"]["structure"], "single_box")
        self.assertTrue(state.constraint_ledger[0].locked)
        self.assertEqual(state.field_sources["geometry.structure"], "user_explicit")
        self.assertEqual(state.phase, Phase.GEOMETRY)

        commit_turn(state, draft)
        self.assertEqual(state.config["geometry"]["structure"], "single_tubs")
        self.assertFalse(state.constraint_ledger[0].locked)
        self.assertEqual(state.field_sources["geometry.structure"], "llm_semantic_frame")
        self.assertEqual(state.phase, Phase.MATERIALS)


if __name__ == "__main__":
    unittest.main()
