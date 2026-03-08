from __future__ import annotations

import unittest

from core.validation.minimal_schema import get_minimal_required_paths, get_local_required_paths
from core.orchestrator.types import Phase


class MinimalSchemaTest(unittest.TestCase):
    def test_point_source_does_not_require_direction(self) -> None:
        config = {
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": {"value": 1.0, "unit": "MeV"},
                "position": {"type": "point", "value": [0.0, 0.0, 0.0]},
            }
        }
        required = get_minimal_required_paths(config)
        self.assertNotIn("source.direction", required)

    def test_beam_source_still_requires_direction(self) -> None:
        config = {
            "source": {
                "type": "beam",
                "particle": "gamma",
                "energy": {"value": 1.0, "unit": "MeV"},
                "position": {"type": "point", "value": [0.0, 0.0, 0.0]},
            }
        }
        required = get_local_required_paths(Phase.SOURCE, config=config)
        self.assertIn("source.direction", required)


if __name__ == "__main__":
    unittest.main()
