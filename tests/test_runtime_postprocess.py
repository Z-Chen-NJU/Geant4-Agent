from __future__ import annotations

import unittest

from nlu.runtime_components.postprocess import merge_params


class RuntimePostprocessTest(unittest.TestCase):
    def test_merge_params_backfills_stack_fields_from_natural_language(self) -> None:
        params, notes = merge_params(
            "stack of layers along z, x 20 mm, y 20 mm, thicknesses 2 3 4 mm, clearance 0.5 mm",
            {},
        )
        self.assertEqual(params.get("stack_x"), 20.0)
        self.assertEqual(params.get("stack_y"), 20.0)
        self.assertEqual(params.get("t1"), 2.0)
        self.assertEqual(params.get("t2"), 3.0)
        self.assertEqual(params.get("t3"), 4.0)
        self.assertEqual(params.get("stack_clearance"), 0.5)
        self.assertEqual(params.get("nest_clearance"), 0.5)
        self.assertTrue(any("stack thicknesses" in note for note in notes))

    def test_merge_params_backfills_stack_footprint_and_outer_box(self) -> None:
        params, notes = merge_params(
            "Use stack footprint 25 mm x 25 mm, thicknesses 1 mm, 2 mm, 1 mm, "
            "layer clearance 0.2 mm, outer box 30 mm x 30 mm x 12 mm, container clearance 0.5 mm",
            {},
        )
        self.assertEqual(params.get("stack_x"), 25.0)
        self.assertEqual(params.get("stack_y"), 25.0)
        self.assertEqual(params.get("parent_x"), 30.0)
        self.assertEqual(params.get("parent_y"), 30.0)
        self.assertEqual(params.get("parent_z"), 12.0)
        self.assertEqual(params.get("nest_clearance"), 0.5)
        self.assertTrue(any("stack footprint" in note for note in notes))
        self.assertTrue(any("outer box" in note for note in notes))

    def test_merge_params_backfills_stack_thicknesses_when_each_value_has_unit(self) -> None:
        params, _ = merge_params(
            "stack footprint 20 mm x 20 mm, thicknesses 2 mm, 4 mm, 6 mm, outer box 30 mm x 30 mm x 20 mm",
            {},
        )
        self.assertEqual(params.get("t1"), 2.0)
        self.assertEqual(params.get("t2"), 4.0)
        self.assertEqual(params.get("t3"), 6.0)

    def test_merge_params_backfills_boolean_box_triplets_from_union_phrase(self) -> None:
        params, notes = merge_params(
            "union of two boxes, 10x20x30 mm and 5x6x7 mm",
            {},
        )
        self.assertEqual(params.get("bool_a_x"), 10.0)
        self.assertEqual(params.get("bool_a_y"), 20.0)
        self.assertEqual(params.get("bool_a_z"), 30.0)
        self.assertEqual(params.get("bool_b_x"), 5.0)
        self.assertEqual(params.get("bool_b_y"), 6.0)
        self.assertEqual(params.get("bool_b_z"), 7.0)
        self.assertNotIn("module_x", params)
        self.assertTrue(any("bool_a_*" in note for note in notes))

    def test_merge_params_backfills_boolean_box_triplets_from_by_phrase(self) -> None:
        params, _ = merge_params(
            "subtract a 5 by 6 by 7 mm box from a 10 by 20 by 30 mm box",
            {},
        )
        self.assertEqual(params.get("bool_a_x"), 10.0)
        self.assertEqual(params.get("bool_a_y"), 20.0)
        self.assertEqual(params.get("bool_a_z"), 30.0)
        self.assertEqual(params.get("bool_b_x"), 5.0)
        self.assertEqual(params.get("bool_b_y"), 6.0)
        self.assertEqual(params.get("bool_b_z"), 7.0)

    def test_merge_params_backfills_boolean_box_triplets_from_hole_phrase(self) -> None:
        params, _ = merge_params(
            "10x20x30 mm box with a 5x6x7 mm hole",
            {},
        )
        self.assertEqual(params.get("bool_a_x"), 10.0)
        self.assertEqual(params.get("bool_a_y"), 20.0)
        self.assertEqual(params.get("bool_a_z"), 30.0)
        self.assertEqual(params.get("bool_b_x"), 5.0)
        self.assertEqual(params.get("bool_b_y"), 6.0)
        self.assertEqual(params.get("bool_b_z"), 7.0)

    def test_merge_params_backfills_grid_counts_from_array_phrase(self) -> None:
        params, _ = merge_params(
            "3 x 3 module array, module 12 mm x 12 mm x 3 mm, pitch_x 15 mm, pitch_y 15 mm, clearance 1 mm",
            {},
        )
        self.assertEqual(params.get("nx"), 3)
        self.assertEqual(params.get("ny"), 3)
        self.assertEqual(params.get("module_x"), 12.0)
        self.assertEqual(params.get("pitch_x"), 15.0)
        self.assertEqual(params.get("clearance"), 1.0)

    def test_merge_params_promotes_outer_box_into_parent_for_nest_context(self) -> None:
        params, _ = merge_params(
            "nested setup: outer box 80 mm x 80 mm x 80 mm, inner cylinder radius 15 mm, half length 25 mm, clearance 1 mm",
            {},
        )
        self.assertEqual(params.get("parent_x"), 80.0)
        self.assertEqual(params.get("parent_y"), 80.0)
        self.assertEqual(params.get("parent_z"), 80.0)
        self.assertEqual(params.get("child_rmax"), 15.0)
        self.assertEqual(params.get("child_hz"), 25.0)


if __name__ == "__main__":
    unittest.main()
