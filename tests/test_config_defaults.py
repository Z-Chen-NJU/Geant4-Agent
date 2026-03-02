from __future__ import annotations

import unittest

from core.config.defaults import build_legacy_default_config, build_strict_default_config


class ConfigDefaultsTest(unittest.TestCase):
    def test_strict_and_legacy_share_semantic_blocks(self) -> None:
        strict_cfg = build_strict_default_config()
        legacy_cfg = build_legacy_default_config()

        self.assertEqual(strict_cfg["materials"], legacy_cfg["materials"])
        self.assertEqual(strict_cfg["source"], legacy_cfg["source"])
        self.assertEqual(strict_cfg["physics"], legacy_cfg["physics"])
        self.assertEqual(strict_cfg["output"], legacy_cfg["output"])

    def test_strict_and_legacy_keep_expected_geometry_shape(self) -> None:
        strict_cfg = build_strict_default_config()
        legacy_cfg = build_legacy_default_config()

        self.assertIn("root_name", strict_cfg["geometry"])
        self.assertNotIn("graph_program", strict_cfg["geometry"])

        self.assertIn("graph_program", legacy_cfg["geometry"])
        self.assertIn("chosen_skeleton", legacy_cfg["geometry"])
        self.assertIn("notes", legacy_cfg)
        self.assertIn("environment", legacy_cfg)


if __name__ == "__main__":
    unittest.main()
