from __future__ import annotations

import unittest

from core.orchestrator.types import Phase
from planner.question_planner import advance_question_state, plan_questions, update_question_attempts


class QuestionPlannerTest(unittest.TestCase):
    def test_advance_question_state_tracks_answered_paths(self) -> None:
        remaining_open, answered_this_turn = advance_question_state(
            previous_missing_paths=["source.energy", "source.position"],
            current_missing_paths=["source.position"],
            open_questions=["source.energy", "source.position"],
        )

        self.assertEqual(remaining_open, ["source.position"])
        self.assertEqual(answered_this_turn, ["source.energy"])

    def test_plan_questions_avoids_immediate_reask_when_alternatives_exist(self) -> None:
        planned = plan_questions(
            ["source.energy", "source.position", "source.direction"],
            Phase.SOURCE,
            open_questions=["source.energy"],
            last_asked_paths=["source.energy"],
        )

        self.assertEqual(planned, ["source.position", "source.direction"])

    def test_plan_questions_deprioritizes_high_retry_open_question(self) -> None:
        planned = plan_questions(
            ["source.energy", "source.position", "source.direction"],
            Phase.SOURCE,
            open_questions=["source.energy"],
            question_attempts={"source.energy": 3},
        )

        self.assertEqual(planned, ["source.position", "source.direction"])

    def test_update_question_attempts_drops_answered_and_increments_asked(self) -> None:
        attempts = update_question_attempts(
            previous_attempts={"source.energy": 2, "source.position": 1},
            current_missing_paths=["source.position", "source.direction"],
            answered_paths=["source.energy"],
            asked_paths=["source.position", "source.direction"],
        )

        self.assertEqual(attempts, {"source.position": 2, "source.direction": 1})


if __name__ == "__main__":
    unittest.main()
