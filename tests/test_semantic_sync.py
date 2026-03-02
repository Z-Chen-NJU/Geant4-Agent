from __future__ import annotations

import unittest

from core.orchestrator.semantic_sync import build_semantic_sync_candidate


class SemanticSyncTest(unittest.TestCase):
    def test_builds_semantic_sync_candidate(self) -> None:
        config = {
            "geometry": {"structure": "single_box", "root_name": None},
            "materials": {
                "selected_materials": ["G4_Cu"],
                "volume_material_map": {},
                "selection_source": None,
                "selection_reasons": [],
            },
            "source": {
                "type": None,
                "particle": "gamma",
                "energy": 1.0,
                "position": [0.0, 0.0, -100.0],
                "direction": [0.0, 0.0, 1.0],
                "selection_source": None,
                "selection_reasons": [],
            },
            "physics": {},
            "output": {"format": "root", "path": None},
        }
        candidate = build_semantic_sync_candidate(config, turn_id=9)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.rationale, "semantic_sync")
        mapped = {u.path: u.value for u in candidate.updates}
        self.assertEqual(mapped["geometry.root_name"], "box")
        self.assertEqual(mapped["materials.volume_material_map"], {"box": "G4_Cu"})
        self.assertEqual(mapped["output.path"], "output/result.root")
        self.assertEqual(mapped["source.type"], "point")


if __name__ == "__main__":
    unittest.main()
