from __future__ import annotations

import unittest
from unittest import mock

from planner.agent import naturalize_response


class DialogueNaturalizationTest(unittest.TestCase):
    def test_naturalize_response_uses_llm_reply(self) -> None:
        with mock.patch("planner.agent.chat", return_value={"response": "Naturalized response."}) as mocked_chat:
            out = naturalize_response(
                "Base response.",
                lang="en",
                action="answer_status",
                updated_paths=["source.energy"],
                missing_fields=["output.path"],
                asked_fields=[],
                overwrite_preview=[],
                dialogue_summary={"updated_fields": ["source energy"]},
                raw_dialogue=[{"role": "user", "content": "set source energy to 1 MeV"}],
                ollama_config="nlu/bert_lab/configs/ollama_config.json",
                temperature=1.0,
            )
        self.assertEqual(out, "Naturalized response.")
        mocked_chat.assert_called_once()

    def test_naturalize_response_falls_back_on_error(self) -> None:
        with mock.patch("planner.agent.chat", side_effect=RuntimeError("network down")):
            out = naturalize_response(
                "Base response.",
                lang="en",
                action="answer_status",
                updated_paths=[],
                missing_fields=[],
                asked_fields=[],
                overwrite_preview=[],
                dialogue_summary={},
                raw_dialogue=[],
                ollama_config="nlu/bert_lab/configs/ollama_config.json",
                temperature=1.0,
            )
        self.assertEqual(out, "Base response.")


if __name__ == "__main__":
    unittest.main()
