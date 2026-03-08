from __future__ import annotations

import unittest

from core.orchestrator.session_manager import process_turn, reset_session


def _turn(session_id: str, text: str) -> dict:
    return process_turn(
        {
            "session_id": session_id,
            "text": text,
            "llm_router": False,
            "llm_question": False,
            "normalize_input": False,
            "autofix": True,
        },
        ollama_config_path="",
        lang="en",
    )


class MaterialAliasTest(unittest.TestCase):
    def test_steel_maps_to_g4_stainless_steel(self) -> None:
        sid = "material-alias-steel"
        reset_session(sid)
        out = _turn(
            sid,
            "steel box 100 mm x 100 mm x 100 mm, gamma point source 1 MeV at (0,0,-50) to +z, physics QBBC, output json",
        )
        self.assertEqual(out.get("config", {}).get("materials", {}).get("selected_materials"), ["G4_STAINLESS-STEEL"])

    def test_lead_alias_maps_to_g4_pb(self) -> None:
        sid = "material-alias-lead"
        reset_session(sid)
        out = _turn(
            sid,
            "lead sphere radius 50 mm, gamma point source 1 MeV at origin to +z, physics FTFP_BERT, output root",
        )
        self.assertEqual(out.get("config", {}).get("materials", {}).get("selected_materials"), ["G4_Pb"])

    def test_csi_alias_maps_to_g4_cesium_iodide(self) -> None:
        sid = "material-alias-csi"
        reset_session(sid)
        out = _turn(
            sid,
            "material G4_CsI; box 100 mm x 100 mm x 10 mm, gamma point source, energy 0.662 MeV, position (0,0,-50), direction +z, physics QBBC, output root path output/result.root",
        )
        self.assertEqual(out.get("config", {}).get("materials", {}).get("selected_materials"), ["G4_CESIUM_IODIDE"])

    def test_chinese_cesium_iodide_alias_maps_to_g4_cesium_iodide(self) -> None:
        sid = "material-alias-csi-zh"
        reset_session(sid)
        out = _turn(
            sid,
            "材料 碘化铯；3 x 3 盒体阵列，每个模块 12 mm x 12 mm x 3 mm，pitch_x 15 mm，pitch_y 15 mm，间隙 1 mm；点源 gamma 0.662 MeV，位置 (0,0,-90) mm，方向 +z；物理列表 QBBC；输出 root。",
        )
        self.assertEqual(out.get("config", {}).get("materials", {}).get("selected_materials"), ["G4_CESIUM_IODIDE"])

    def test_change_to_lead_without_material_keyword_still_requests_overwrite(self) -> None:
        sid = "material-target-hint-lead"
        reset_session(sid)
        first = _turn(
            sid,
            "copper box 200 mm x 200 mm x 200 mm, gamma point source 1 MeV at origin to +z, physics QBBC, output json",
        )
        self.assertEqual(first.get("config", {}).get("materials", {}).get("selected_materials"), ["G4_Cu"])

        second = _turn(sid, "change target to lead")
        self.assertEqual(second.get("dialogue_action"), "confirm_overwrite")
        self.assertTrue(second.get("pending_overwrite_required"))


if __name__ == "__main__":
    unittest.main()
