from __future__ import annotations

import unittest

from core.orchestrator.candidate_preprocess import (
    drop_updates_shadowed_by_anchor,
    filter_candidate_by_target_scopes,
)
from core.orchestrator.types import CandidateUpdate, Intent, Producer, UpdateOp


class CandidatePreprocessTest(unittest.TestCase):
    def test_filter_candidate_by_target_scopes_keeps_matching_root(self) -> None:
        candidate = CandidateUpdate(
            producer=Producer.BERT_EXTRACTOR,
            intent=Intent.SET,
            target_paths=["geometry.params.module_x", "source.energy"],
            updates=[
                UpdateOp(
                    path="geometry.params.module_x",
                    op="set",
                    value=1000.0,
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=0.8,
                    turn_id=1,
                ),
                UpdateOp(
                    path="source.energy",
                    op="set",
                    value=1.0,
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=0.8,
                    turn_id=1,
                ),
            ],
            confidence=0.8,
            rationale="scope_test",
        )
        filtered = filter_candidate_by_target_scopes(candidate, ["geometry.kind", "geometry.params.module_x"])
        self.assertEqual([u.path for u in filtered.updates], ["geometry.params.module_x"])

    def test_drop_updates_shadowed_by_anchor_removes_duplicate_paths(self) -> None:
        anchor = CandidateUpdate(
            producer=Producer.SLOT_MAPPER,
            intent=Intent.SET,
            target_paths=["geometry.params.module_x"],
            updates=[
                UpdateOp(
                    path="geometry.params.module_x",
                    op="set",
                    value=1000.0,
                    producer=Producer.SLOT_MAPPER,
                    confidence=0.9,
                    turn_id=1,
                )
            ],
            confidence=0.9,
            rationale="anchor",
        )
        candidate = CandidateUpdate(
            producer=Producer.BERT_EXTRACTOR,
            intent=Intent.SET,
            target_paths=["geometry.params.module_x", "source.energy"],
            updates=[
                UpdateOp(
                    path="geometry.params.module_x",
                    op="set",
                    value=1000.0,
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=0.7,
                    turn_id=1,
                ),
                UpdateOp(
                    path="source.energy",
                    op="set",
                    value=1.0,
                    producer=Producer.BERT_EXTRACTOR,
                    confidence=0.7,
                    turn_id=1,
                ),
            ],
            confidence=0.7,
            rationale="candidate",
        )
        filtered = drop_updates_shadowed_by_anchor(candidate, anchor)
        self.assertEqual([u.path for u in filtered.updates], ["source.energy"])


if __name__ == "__main__":
    unittest.main()
