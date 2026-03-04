from __future__ import annotations

import unittest

from knowledge.validate import validate_material_spec, validate_min_config


class KnowledgeValidateTest(unittest.TestCase):
    def test_validate_material_spec_reports_non_numeric_fields(self) -> None:
        issues = validate_material_spec({"material": "G4_Cu", "temperature_K": "hot"})
        messages = [i.message for i in issues]
        self.assertIn("temperature_K must be numeric", messages)

    def test_validate_min_config_accepts_current_nested_schema(self) -> None:
        config = {
            "physics": {"physics_list": "FTFP_BERT"},
            "source": {
                "particle": "gamma",
                "energy": 1.0,
                "direction": [0.0, 0.0, 1.0],
            },
            "output": {"format": "hdf5", "path": "out/result.h5"},
            "geometry": {"volume_names": ["box"]},
            "materials": {"volume_material_map": {"box": "G4_Cu"}},
        }
        issues = validate_min_config(config)
        messages = [i.message for i in issues]
        self.assertNotIn("physics.physics_list not in curated list", messages)
        self.assertNotIn("output.format not in curated list", messages)
        self.assertNotIn("volume_material_map missing volumes: ['box']", messages)

    def test_validate_min_config_rejects_zero_direction_and_unknown_output(self) -> None:
        config = {
            "physics": {"physics_list": "FTFP_BERT"},
            "source": {
                "particle": "gamma",
                "energy": 1.0,
                "direction": [0.0, 0.0, 0.0],
            },
            "output": {"format": "ascii", "path": "out/result.txt"},
        }
        issues = validate_min_config(config)
        messages = [i.message for i in issues]
        self.assertIn("source.direction vector cannot be zero", messages)
        self.assertIn("output.format not in curated list", messages)

    def test_validate_min_config_reports_non_numeric_source_values(self) -> None:
        config = {
            "physics": {"physics_list": "FTFP_BERT"},
            "source": {
                "particle": "gamma",
                "energy": "one",
                "direction": ["x", 0.0, 1.0],
            },
            "output": {"format": "root", "path": "out/result.root"},
        }
        issues = validate_min_config(config)
        messages = [i.message for i in issues]
        self.assertIn("source.energy must be numeric", messages)
        self.assertIn("source.direction must be numeric", messages)


if __name__ == "__main__":
    unittest.main()
