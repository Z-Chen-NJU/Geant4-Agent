from __future__ import annotations

import unittest

from core.contracts.slots import GeometrySlots, SlotFrame
from core.geometry.catalog import get_geometry_catalog_entry, resolve_geometry_structure
from core.geometry.compiler import compile_geometry_spec_from_slot_frame


class GeometryCompilerTests(unittest.TestCase):
    def test_catalog_resolves_box_alias(self) -> None:
        self.assertEqual(resolve_geometry_structure("box"), "single_box")
        entry = get_geometry_catalog_entry("cube")
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.structure, "single_box")

    def test_compile_single_box_from_slot_frame(self) -> None:
        frame = SlotFrame(confidence=0.92, geometry=GeometrySlots(kind="box", size_triplet_mm=[10, 20, 30]))
        result = compile_geometry_spec_from_slot_frame(frame)

        self.assertTrue(result.ok)
        assert result.spec is not None
        self.assertEqual(result.spec.structure, "single_box")
        self.assertEqual(result.spec.params["size_triplet_mm"], [10.0, 20.0, 30.0])
        self.assertIn("geometry.params.module_x", result.spec.required_paths)

    def test_compile_single_tubs_from_slot_frame(self) -> None:
        frame = SlotFrame(confidence=0.88, geometry=GeometrySlots(kind="cylinder", radius_mm=15, half_length_mm=40))
        result = compile_geometry_spec_from_slot_frame(frame)

        self.assertTrue(result.ok)
        assert result.spec is not None
        self.assertEqual(result.spec.structure, "single_tubs")
        self.assertEqual(result.spec.params["radius_mm"], 15.0)
        self.assertEqual(result.spec.params["half_length_mm"], 40.0)

    def test_compile_keeps_missing_required_geometry_fields(self) -> None:
        frame = SlotFrame(confidence=0.81, geometry=GeometrySlots(kind="box"))
        result = compile_geometry_spec_from_slot_frame(frame)

        self.assertFalse(result.ok)
        self.assertEqual(result.missing_fields, ("size_triplet_mm",))

    def test_compile_rejects_unknown_geometry_kind(self) -> None:
        frame = SlotFrame(confidence=0.75, geometry=GeometrySlots(kind="ring_lattice"))
        result = compile_geometry_spec_from_slot_frame(frame)

        self.assertFalse(result.ok)
        self.assertEqual(result.errors, ("missing_geometry_structure",))


if __name__ == "__main__":
    unittest.main()
