from __future__ import annotations

import unittest

from core.dialogue.renderer import render_dialogue_message
from core.dialogue.types import DialogueAction, DialogueDecision


class DialogueRendererTest(unittest.TestCase):
    def test_non_llm_clarification_uses_structured_question_for_graph_path(self) -> None:
        message = render_dialogue_message(
            DialogueDecision(
                action=DialogueAction.ASK_CLARIFICATION,
                asked_fields=["geometry.ask.ring.radius"],
                missing_fields=["geometry.ask.ring.radius"],
                user_intent="SET",
            ),
            lang="en",
            use_llm_question=False,
            ollama_config="",
            user_temperature=1.0,
            dialogue_summary={},
            raw_dialogue=[],
        )
        self.assertEqual(message, "Please provide the ring radius.")

    def test_non_llm_clarification_uses_structured_question_for_source_paths(self) -> None:
        message = render_dialogue_message(
            DialogueDecision(
                action=DialogueAction.ASK_CLARIFICATION,
                asked_fields=["source.position", "source.direction"],
                missing_fields=["source.position", "source.direction"],
                user_intent="SET",
            ),
            lang="en",
            use_llm_question=False,
            ollama_config="",
            user_temperature=1.0,
            dialogue_summary={},
            raw_dialogue=[],
        )
        self.assertIn("I still need two details.", message)
        self.assertIn("Please provide the source position vector as (x, y, z).", message)
        self.assertIn("Please provide the source direction vector as (dx, dy, dz).", message)

    def test_non_llm_overwrite_confirmation_uses_friendly_field_names(self) -> None:
        message = render_dialogue_message(
            DialogueDecision(
                action=DialogueAction.CONFIRM_OVERWRITE,
                overwrite_preview=[{"path": "materials.selected_materials", "old": "G4_Cu", "new": "G4_Al"}],
                user_intent="MODIFY",
            ),
            lang="en",
            use_llm_question=False,
            ollama_config="",
            user_temperature=1.0,
            dialogue_summary={},
            raw_dialogue=[],
        )
        self.assertIn("material", message.lower())
        self.assertIn("Reply 'confirm' to apply it", message)


if __name__ == "__main__":
    unittest.main()
