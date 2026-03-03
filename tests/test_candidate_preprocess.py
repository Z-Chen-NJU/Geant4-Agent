from __future__ import annotations

import unittest

from core.orchestrator.candidate_preprocess import filter_candidate_by_explicit_targets
from core.orchestrator.types import CandidateUpdate, Intent, Producer, UpdateOp


class CandidatePreprocessTest(unittest.TestCase):
    def test_path_level_filter_keeps_only_requested_updates(self) -> None:
        candidate = CandidateUpdate(
            producer=Producer.BERT_EXTRACTOR,
            intent=Intent.SET,
            target_paths=["output.format", "source.position"],
            updates=[
                UpdateOp(
                    path="source.position",
                    op="set",
                    value=[0, 0, -100],
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=0.7,
                    turn_id=1,
                ),
                UpdateOp(
                    path="output.format",
                    op="set",
                    value="json",
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=0.7,
                    turn_id=1,
                ),
            ],
            confidence=0.7,
            rationale="test",
        )

        filtered = filter_candidate_by_explicit_targets(candidate, ["output.format"])

        self.assertEqual([update.path for update in filtered.updates], ["output.format"])
        self.assertEqual(filtered.target_paths, ["output.format"])


if __name__ == "__main__":
    unittest.main()
