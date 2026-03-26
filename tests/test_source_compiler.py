from __future__ import annotations

import unittest

from core.contracts.semantic import SemanticFrame, SourceFrame
from core.contracts.slots import SlotFrame, SourceSlots
from core.source.adapters import (
    compare_slot_frame_source,
    diff_source_config_fragment,
    source_spec_to_config_fragment,
    source_spec_to_runtime_payload,
)
from core.source.catalog import get_source_catalog_entry, resolve_source_type
from core.source.compiler import (
    compile_source_spec_from_config,
    compile_source_spec_from_semantic_frame,
    compile_source_spec_from_slot_frame,
)


class SourceCompilerTests(unittest.TestCase):
    def test_catalog_resolves_beam_alias(self) -> None:
        self.assertEqual(resolve_source_type("pencil_beam"), "beam")
        entry = get_source_catalog_entry("point")
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry.source_type, "point")

    def test_compile_point_from_slot_frame(self) -> None:
        frame = SlotFrame(
            confidence=0.91,
            source=SourceSlots(
                kind="point",
                particle="gamma",
                energy_mev=1.0,
                position_mm=[0.0, 0.0, -20.0],
                direction_vec=[0.0, 0.0, 1.0],
            ),
        )
        result = compile_source_spec_from_slot_frame(frame)
        self.assertTrue(result.ok)
        assert result.spec is not None
        self.assertEqual(result.spec.source_type, "point")
        self.assertEqual(result.spec.fields["energy_mev"], 1.0)
        self.assertEqual(result.spec.fields["position_mm"], [0.0, 0.0, -20.0])
        self.assertEqual(result.spec.field_resolutions["particle"].status, "user_explicit")

    def test_compile_beam_requires_direction(self) -> None:
        frame = SlotFrame(
            confidence=0.88,
            source=SourceSlots(kind="beam", particle="gamma", energy_mev=5.0, position_mm=[0.0, 0.0, -50.0]),
        )
        result = compile_source_spec_from_slot_frame(frame)
        self.assertFalse(result.ok)
        self.assertEqual(result.missing_fields, ("direction_vec",))

    def test_compile_isotropic_from_semantic_frame(self) -> None:
        frame = SemanticFrame(
            source=SourceFrame(
                type="isotropic",
                particle="gamma",
                energy={"value": 0.8},
                position={"x": 0.0, "y": 0.0, "z": 0.0},
            )
        )
        result = compile_source_spec_from_semantic_frame(frame)
        self.assertTrue(result.ok)
        assert result.spec is not None
        self.assertEqual(result.spec.source_type, "isotropic")
        self.assertEqual(result.spec.fields["energy_mev"], 0.8)

    def test_compile_point_from_config(self) -> None:
        config = {
            "source": {
                "type": "point",
                "particle": "gamma",
                "energy": 1.25,
                "position": {"type": "vector", "value": [0.0, 0.0, -100.0]},
                "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            }
        }
        result = compile_source_spec_from_config(config)
        self.assertTrue(result.ok)
        assert result.spec is not None
        self.assertEqual(result.spec.fields["direction_vec"], [0.0, 0.0, 1.0])

    def test_source_spec_to_runtime_payload(self) -> None:
        frame = SlotFrame(
            confidence=0.92,
            source=SourceSlots(
                kind="beam",
                particle="proton",
                energy_mev=250.0,
                position_mm=[0.0, 0.0, -120.0],
                direction_vec=[0.0, 0.0, 1.0],
            ),
        )
        result = compile_source_spec_from_slot_frame(frame)
        assert result.spec is not None
        payload = source_spec_to_runtime_payload(result.spec)
        self.assertEqual(payload["source_type"], "beam")
        self.assertEqual(payload["particle"], "proton")
        self.assertEqual(payload["energy"], 250.0)
        self.assertEqual(payload["position"]["z"], -120.0)

    def test_source_spec_to_config_fragment(self) -> None:
        frame = SlotFrame(
            confidence=0.92,
            source=SourceSlots(
                kind="point",
                particle="gamma",
                energy_mev=1.0,
                position_mm=[0.0, 0.0, -20.0],
                direction_vec=[0.0, 0.0, 1.0],
            ),
        )
        result = compile_source_spec_from_slot_frame(frame)
        assert result.spec is not None
        fragment = source_spec_to_config_fragment(result.spec)
        self.assertEqual(fragment["source"]["type"], "point")
        self.assertEqual(fragment["source"]["position"]["value"], [0.0, 0.0, -20.0])

    def test_diff_source_config_fragment_reports_match(self) -> None:
        frame = SlotFrame(
            confidence=0.92,
            source=SourceSlots(
                kind="point",
                particle="gamma",
                energy_mev=1.0,
                position_mm=[0.0, 0.0, -20.0],
                direction_vec=[0.0, 0.0, 1.0],
            ),
        )
        result = compile_source_spec_from_slot_frame(frame)
        assert result.spec is not None
        legacy_source = {
            "type": "point",
            "particle": "gamma",
            "energy": 1.0,
            "position": {"type": "vector", "value": [0.0, 0.0, -20.0]},
            "direction": {"type": "vector", "value": [0.0, 0.0, 1.0]},
        }
        diff = diff_source_config_fragment(result.spec, legacy_source)
        self.assertTrue(diff["matches"])

    def test_compare_slot_frame_source_reports_match(self) -> None:
        frame = SlotFrame(
            confidence=0.92,
            source=SourceSlots(
                kind="point",
                particle="gamma",
                energy_mev=1.0,
                position_mm=[0.0, 0.0, -20.0],
                direction_vec=[0.0, 0.0, 1.0],
            ),
        )
        comparison = compare_slot_frame_source(frame, turn_id=1)
        self.assertIsNotNone(comparison)
        assert comparison is not None
        self.assertTrue(comparison["compile_ok"])
        self.assertTrue(comparison["matches"])
        self.assertEqual(comparison["spec_source_type"], "point")


if __name__ == "__main__":
    unittest.main()
