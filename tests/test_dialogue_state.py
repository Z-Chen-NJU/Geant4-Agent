from __future__ import annotations

import unittest

from types import SimpleNamespace

from core.dialogue.state import build_dialogue_summary, build_raw_dialogue, sync_dialogue_state
from core.dialogue.types import DialogueAction, DialogueDecision


class DialogueStateTest(unittest.TestCase):
    def test_build_raw_dialogue_trims_and_normalizes(self) -> None:
        history = [
            {"role": "user", "content": "u1"},
            {"role": "assistant", "content": "a1"},
            {"role": "user", "content": "u2"},
        ]
        raw = build_raw_dialogue(history, limit=2)
        self.assertEqual(raw, [{"role": "assistant", "content": "a1"}, {"role": "user", "content": "u2"}])

    def test_build_dialogue_summary_uses_friendly_fields(self) -> None:
        decision = DialogueDecision(
            action=DialogueAction.ASK_CLARIFICATION,
            asked_fields=["source.energy"],
            updated_paths=["materials.selected_materials"],
            missing_fields=["source.energy"],
            answered_this_turn=["materials.selected_materials"],
            user_intent="SET",
        )
        summary = build_dialogue_summary(decision, lang="en", is_complete=False)
        self.assertEqual(summary["status"], "pending")
        self.assertEqual(summary["last_action"], "ask_clarification")
        self.assertIn("source energy", summary["pending_fields"])
        self.assertIn("source energy", summary["next_questions"])
        self.assertIn("source", summary["grouped_status"])
        self.assertIn("materials", summary["grouped_status"])

    def test_build_dialogue_summary_hides_internal_metadata_fields(self) -> None:
        decision = DialogueDecision(
            action=DialogueAction.SUMMARIZE_PROGRESS,
            updated_paths=[
                "materials.selected_materials",
                "materials.selection_source",
                "geometry.graph_program",
                "physics.backup_physics_list",
                "physics.covered_processes",
                "physics.selection_reasons",
            ],
            missing_fields=["output.format"],
            answered_this_turn=["materials.selection_source"],
            user_intent="SET",
        )
        summary = build_dialogue_summary(
            decision,
            lang="en",
            is_complete=False,
            confirmed_fact_paths=["materials.selected_materials", "physics.selection_reasons"],
        )
        self.assertIn("selected materials", summary["updated_fields"])
        self.assertNotIn("materials.selection_source", summary["updated_fields"])
        self.assertNotIn("backup physics list", summary["updated_fields"])
        self.assertNotIn("geometry.graph_program", summary["updated_fields"])
        self.assertNotIn("physics.covered_processes", summary["updated_fields"])
        self.assertEqual(summary["answered_fields"], [])
        self.assertEqual(summary["recent_confirmed"], ["selected materials"])
        grouped = summary["grouped_status"]
        self.assertEqual(grouped["materials"]["updated_fields"], ["selected materials"])
        self.assertNotIn("physics", grouped)

    def test_sync_dialogue_state_accumulates_memory(self) -> None:
        state = SimpleNamespace(
            history=[{"role": "user", "content": "set energy"}],
            dialogue_summary={},
            confirmed_fact_paths=[],
            dialogue_memory=[],
            config={
                "materials": {
                    "selected_materials": ["G4_Cu"],
                    "selection_source": "explicit_request",
                    "selection_reasons": ["Material provided explicitly."],
                },
                "source": {},
                "physics": {},
            },
        )
        decision = DialogueDecision(
            action=DialogueAction.SUMMARIZE_PROGRESS,
            updated_paths=["source.energy"],
            missing_fields=["output.path"],
            answered_this_turn=["source.energy"],
            user_intent="SET",
        )
        summary, raw_dialogue, memory = sync_dialogue_state(
            state,
            decision=decision,
            lang="en",
            is_complete=False,
        )
        self.assertIn("source energy", summary["recent_confirmed"])
        self.assertEqual(summary["memory_depth"], 1)
        self.assertEqual(len(memory), 1)
        self.assertIn("materials", summary["available_explanations"])
        self.assertEqual(raw_dialogue, [{"role": "user", "content": "set energy"}])


if __name__ == "__main__":
    unittest.main()
