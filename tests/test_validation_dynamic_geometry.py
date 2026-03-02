from __future__ import annotations

import unittest

from core.validation.validator_gate import validate_layer_c_completeness


class DynamicGeometryValidationTest(unittest.TestCase):
    def test_single_tubs_uses_family_required_paths(self) -> None:
        config = {
            "geometry": {
                "structure": "single_tubs",
                "params": {"child_rmax": 12.0, "child_hz": 30.0},
                "root_name": "target",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {"target": "G4_Cu"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.0,
                "position": {"type": "vector", "value": [0.0, 0.0, 0.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertTrue(report.ok)
        self.assertNotIn("geometry.params.module_x", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_y", report.missing_required_paths)
        self.assertNotIn("geometry.params.module_z", report.missing_required_paths)

    def test_single_tubs_reports_missing_family_params(self) -> None:
        config = {
            "geometry": {
                "structure": "single_tubs",
                "params": {"child_rmax": 12.0},
                "root_name": "target",
                "feasible": None,
            },
            "materials": {"selected_materials": ["G4_Cu"], "volume_material_map": {"target": "G4_Cu"}},
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.0,
                "position": {"type": "vector", "value": [0.0, 0.0, 0.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            },
            "physics": {"physics_list": "FTFP_BERT"},
            "output": {"format": "root", "path": "output/result.root"},
        }
        report = validate_layer_c_completeness(config)
        self.assertFalse(report.ok)
        self.assertIn("geometry.params.child_hz", report.missing_required_paths)


if __name__ == "__main__":
    unittest.main()
