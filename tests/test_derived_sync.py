from __future__ import annotations

import unittest

from core.orchestrator.derived_sync import build_derived_sync_candidate


class DerivedSyncTest(unittest.TestCase):
    def test_syncs_volume_material_map_to_selected_material(self) -> None:
        config = {
            "geometry": {"structure": "single_box", "root_name": "box"},
            "materials": {
                "selected_materials": ["G4_Al"],
                "volume_material_map": {"box": "G4_Cu"},
            },
            "source": {},
            "physics": {},
            "output": {},
        }
        candidate = build_derived_sync_candidate(config, turn_id=3)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        mapped = {u.path: u.value for u in candidate.updates}
        self.assertEqual(mapped["materials.volume_material_map"], {"box": "G4_Al"})

    def test_generates_output_path_from_format(self) -> None:
        config = {
            "geometry": {},
            "materials": {},
            "source": {},
            "physics": {},
            "output": {"format": "json", "path": None},
        }
        candidate = build_derived_sync_candidate(config, turn_id=1)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        mapped = {u.path: u.value for u in candidate.updates}
        self.assertEqual(mapped["output.path"], "output/result.json")

    def test_updates_output_path_extension_when_format_changes(self) -> None:
        config = {
            "geometry": {},
            "materials": {},
            "source": {},
            "physics": {},
            "output": {"format": "hdf5", "path": "output/result.root"},
        }
        candidate = build_derived_sync_candidate(config, turn_id=2)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        mapped = {u.path: u.value for u in candidate.updates}
        self.assertEqual(mapped["output.path"], "output/result.hdf5")

    def test_fills_physics_selection_metadata_for_explicit_list(self) -> None:
        config = {
            "geometry": {},
            "materials": {},
            "source": {},
            "physics": {
                "physics_list": "FTFP_BERT",
                "selection_source": None,
                "selection_reasons": [],
            },
            "output": {},
        }
        candidate = build_derived_sync_candidate(config, turn_id=2)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        mapped = {u.path: u.value for u in candidate.updates}
        self.assertEqual(mapped["physics.selection_source"], "explicit_request")
        self.assertEqual(
            mapped["physics.selection_reasons"],
            ["Physics list provided explicitly by user or extracted semantics."],
        )

    def test_fills_material_selection_metadata_for_explicit_material(self) -> None:
        config = {
            "geometry": {"structure": "single_box", "root_name": "box"},
            "materials": {
                "selected_materials": ["G4_Cu"],
                "volume_material_map": {"box": "G4_Cu"},
                "selection_source": None,
                "selection_reasons": [],
            },
            "source": {},
            "physics": {},
            "output": {},
        }
        candidate = build_derived_sync_candidate(config, turn_id=4)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        mapped = {u.path: u.value for u in candidate.updates}
        self.assertEqual(mapped["materials.selection_source"], "explicit_request")
        self.assertEqual(
            mapped["materials.selection_reasons"],
            ["Material provided explicitly by user or extracted semantics."],
        )

    def test_infers_source_type_and_metadata_from_vectors(self) -> None:
        config = {
            "geometry": {},
            "materials": {},
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
            "output": {},
        }
        candidate = build_derived_sync_candidate(config, turn_id=5)
        self.assertIsNotNone(candidate)
        assert candidate is not None
        mapped = {u.path: u.value for u in candidate.updates}
        self.assertEqual(mapped["source.type"], "point")
        self.assertEqual(mapped["source.selection_source"], "explicit_request")
        self.assertEqual(
            mapped["source.selection_reasons"],
            [
                "Source parameters provided explicitly by user or extracted semantics.",
                "Source type inferred as point because position or direction was provided.",
            ],
        )


if __name__ == "__main__":
    unittest.main()
