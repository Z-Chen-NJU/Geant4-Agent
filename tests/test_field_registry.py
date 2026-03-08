from __future__ import annotations

import unittest

from core.config.field_registry import (
    clarification_items,
    friendly_labels,
    missing_field_question,
)
from core.config.path_registry import canonical_field_path


class FieldRegistryTest(unittest.TestCase):
    def test_canonicalizes_legacy_paths(self) -> None:
        self.assertEqual(canonical_field_path("source.energy_MeV"), "source.energy")
        self.assertEqual(canonical_field_path("physics_list.name"), "physics.physics_list")

    def test_friendly_labels_handle_legacy_aliases(self) -> None:
        labels = friendly_labels(["source.energy_MeV", "physics_list.name"], "en")
        self.assertEqual(labels, ["source energy", "physics list"])

    def test_missing_field_question_uses_shared_registry(self) -> None:
        self.assertEqual(
            missing_field_question("physics_list.name", "zh"),
            "请提供物理列表名称（例如 FTFP_BERT 或 QBBC）。",
        )

    def test_clarification_items_use_canonical_descriptions(self) -> None:
        items = clarification_items(["source.energy_MeV", "geometry.params.radius"], "en")
        self.assertEqual(items, ["source energy (MeV)", "radius"])

    def test_geometry_param_labels_are_humanized(self) -> None:
        labels = friendly_labels(
            ["geometry.params.module_x", "geometry.params.child_rmax", "geometry.params.t1"],
            "en",
        )
        self.assertEqual(labels, ["box size along x", "radius", "layer 1 thickness"])

    def test_graph_family_labels_are_human_readable(self) -> None:
        labels = friendly_labels(
            ["geometry.ask.ring.module_size", "geometry.ask.stack.thicknesses"],
            "en",
        )
        self.assertEqual(labels, ["ring module size", "stack layer thicknesses"])

    def test_graph_family_questions_are_family_aware(self) -> None:
        self.assertEqual(
            missing_field_question("geometry.ask.boolean.solid_a_size", "en"),
            "Please provide the size of boolean solid A as x, y, z.",
        )


if __name__ == "__main__":
    unittest.main()
