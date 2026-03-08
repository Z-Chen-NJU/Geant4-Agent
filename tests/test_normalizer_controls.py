from __future__ import annotations

import unittest

from core.orchestrator.types import Intent
from nlu.llm.normalizer import infer_user_turn_controls


class NormalizerControlsTest(unittest.TestCase):
    def test_chinese_confirm_maps_to_confirm_intent(self) -> None:
        controls = infer_user_turn_controls("\u786e\u8ba4")
        self.assertEqual(controls["intent"], Intent.CONFIRM)
        self.assertEqual(controls["target_paths"], [])

    def test_chinese_modify_maps_to_modify_intent_and_material_target(self) -> None:
        controls = infer_user_turn_controls("\u628a\u6750\u6599\u6539\u6210 G4_Al\u3002")
        self.assertEqual(controls["intent"], Intent.MODIFY)
        self.assertIn("materials.selected_materials", controls["target_paths"])

    def test_keep_existing_maps_to_reject_intent(self) -> None:
        controls = infer_user_turn_controls("keep existing")
        self.assertEqual(controls["intent"], Intent.REJECT)
        self.assertEqual(controls["target_paths"], [])

    def test_narrow_output_turn_targets_output_only(self) -> None:
        controls = infer_user_turn_controls("Output json.")
        self.assertEqual(controls["intent"], Intent.SET)
        self.assertIn("output.format", controls["target_paths"])
        self.assertNotIn("output.path", controls["target_paths"])
        self.assertNotIn("source.position", controls["target_paths"])

    def test_narrow_hdf5_output_turn_targets_output_only(self) -> None:
        controls = infer_user_turn_controls("Output hdf5.")
        self.assertEqual(controls["intent"], Intent.SET)
        self.assertIn("output.format", controls["target_paths"])
        self.assertNotIn("source.position", controls["target_paths"])

    def test_explicit_source_vectors_target_position_and_direction(self) -> None:
        controls = infer_user_turn_controls(
            "Please set up a copper box with a gamma point source at (0,0,-100) mm pointing (0,0,1)."
        )
        self.assertEqual(controls["intent"], Intent.SET)
        self.assertIn("source.position", controls["target_paths"])
        self.assertIn("source.direction", controls["target_paths"])

    def test_cylindrical_prompt_targets_geometry_structure_and_tubs_params(self) -> None:
        controls = infer_user_turn_controls("Create a cylindrical copper target with radius 30 mm and half-length 50 mm.")
        self.assertEqual(controls["intent"], Intent.SET)
        self.assertIn("geometry.structure", controls["target_paths"])
        self.assertIn("geometry.params.child_rmax", controls["target_paths"])
        self.assertIn("geometry.params.child_hz", controls["target_paths"])

    def test_uncertain_turn_maps_to_question_intent(self) -> None:
        controls = infer_user_turn_controls(
            "Need a quick cargo-screening toy setup with forward photons, but I have not fixed the target shape, material, source energy, or output format yet."
        )
        self.assertEqual(controls["intent"], Intent.QUESTION)
        self.assertIn("geometry.structure", controls["target_paths"])
        self.assertIn("materials.selected_materials", controls["target_paths"])
        self.assertIn("source.energy", controls["target_paths"])
        self.assertIn("output.format", controls["target_paths"])

    def test_chinese_missing_start_maps_to_question_intent(self) -> None:
        controls = infer_user_turn_controls("我想做一个中子屏蔽的概念验证，现在先给一个缺参开头。")
        self.assertEqual(controls["intent"], Intent.QUESTION)
        self.assertIn("geometry.structure", controls["target_paths"])
        self.assertIn("materials.selected_materials", controls["target_paths"])
        self.assertIn("source.energy", controls["target_paths"])
        self.assertIn("output.format", controls["target_paths"])


if __name__ == "__main__":
    unittest.main()
