from __future__ import annotations

import unittest

from core.interpreter import EvidenceSpan, GeometryCandidate, SourceCandidate, TurnSummary


class InterpreterSpecTests(unittest.TestCase):
    def test_turn_summary_payload_is_plain_dict(self) -> None:
        summary = TurnSummary(
            intent="set",
            focus="mixed",
            scope="full_request",
            user_goal="Create a copper target and define a gamma source.",
            explicit_domains=["geometry", "source"],
        )
        self.assertEqual(
            summary.to_payload(),
            {
                "intent": "set",
                "focus": "mixed",
                "scope": "full_request",
                "user_goal": "Create a copper target and define a gamma source.",
                "explicit_domains": ["geometry", "source"],
                "uncertain_domains": [],
            },
        )

    def test_geometry_candidate_payload_preserves_dimension_hints(self) -> None:
        candidate = GeometryCandidate(
            kind_candidate="box",
            material_candidate="G4_Cu",
            dimension_hints={"size_triplet_mm": [10.0, 20.0, 30.0]},
            confidence=0.92,
            evidence_spans=[
                EvidenceSpan(text="10 mm x 20 mm x 30 mm", role="dimensions"),
                EvidenceSpan(text="copper box target", role="geometry"),
            ],
        )
        payload = candidate.to_payload()
        self.assertEqual(payload["kind_candidate"], "box")
        self.assertEqual(payload["material_candidate"], "G4_Cu")
        self.assertEqual(payload["dimension_hints"]["size_triplet_mm"], [10.0, 20.0, 30.0])
        self.assertEqual(payload["evidence_spans"][0]["role"], "dimensions")

    def test_source_candidate_payload_preserves_relative_relation(self) -> None:
        candidate = SourceCandidate(
            source_type_candidate="point",
            particle_candidate="gamma",
            energy_candidate_mev=1.0,
            position_mode="relative_to_target_center",
            position_hint={"offset_mm": 20.0, "axis": "-z"},
            direction_mode="toward_target_center",
            confidence=0.95,
            evidence_spans=[
                EvidenceSpan(text="20 mm outside the target center", role="position"),
                EvidenceSpan(text="toward target center", role="direction"),
            ],
        )
        payload = candidate.to_payload()
        self.assertEqual(payload["source_type_candidate"], "point")
        self.assertEqual(payload["position_mode"], "relative_to_target_center")
        self.assertEqual(payload["position_hint"]["axis"], "-z")
        self.assertEqual(payload["direction_mode"], "toward_target_center")


if __name__ == "__main__":
    unittest.main()
