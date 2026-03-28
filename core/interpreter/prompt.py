from __future__ import annotations


def build_interpreter_prompt(user_text: str, context_summary: str) -> str:
    return (
        "Interpret the user request for a Geant4 configuration session.\n"
        "Your job is to explain what the user appears to mean, not to write final config paths.\n"
        "Return JSON only with this schema:\n"
        "{\n"
        '  "turn_summary": {\n'
        '    "intent": "set|modify|confirm|reject|question|other",\n'
        '    "focus": "geometry|source|physics|output|mixed",\n'
        '    "scope": "full_request|partial_update|clarification",\n'
        '    "user_goal": "brief summary of the user goal",\n'
        '    "explicit_domains": ["geometry"],\n'
        '    "uncertain_domains": ["source"]\n'
        "  },\n"
        '  "geometry_candidate": {\n'
        '    "kind_candidate": "box|cylinder|sphere|orb|cons|trd|slab|plate|null",\n'
        '    "material_candidate": "G4_Cu|null",\n'
        '    "dimension_hints": {\n'
        '      "size_triplet_mm": [null,null,null],\n'
        '      "side_length_mm": null,\n'
        '      "radius_mm": null,\n'
        '      "diameter_mm": null,\n'
        '      "half_length_mm": null,\n'
        '      "full_length_mm": null,\n'
        '      "thickness_mm": null\n'
        "    },\n"
        '    "placement_relation": null,\n'
        '    "confidence": 0.0,\n'
        '    "ambiguities": ["what is unclear"],\n'
        '    "evidence_spans": [{"text":"10 mm x 20 mm x 30 mm","role":"dimensions"}]\n'
        "  },\n"
        '  "source_candidate": {\n'
        '    "source_type_candidate": "point|beam|plane|isotropic|null",\n'
        '    "particle_candidate": "gamma|e-|proton|neutron|null",\n'
        '    "energy_candidate_mev": null,\n'
        '    "position_mode": "absolute|relative_to_target_center|relative_to_target_face|null",\n'
        '    "position_hint": {\n'
        '      "position_mm": [null,null,null],\n'
        '      "offset_mm": null,\n'
        '      "axis": "+x|-x|+y|-y|+z|-z|null"\n'
        "    },\n"
        '    "direction_mode": "explicit_vector|toward_target_center|toward_target_face|toward_target_face_normal|normal_to_target_face|unknown|null",\n'
        '    "direction_hint": {\n'
        '      "direction_vec": [null,null,null],\n'
        '      "axis": "+x|-x|+y|-y|+z|-z|null"\n'
        "    },\n"
        '    "confidence": 0.0,\n'
        '    "ambiguities": ["what is unclear"],\n'
        '    "evidence_spans": [{"text":"at (0,0,-20) mm","role":"position"}]\n'
        "  }\n"
        "}\n"
        "Hard rules:\n"
        "- Do not output final config paths.\n"
        "- Do not invent missing values.\n"
        "- If the user is unclear, keep the corresponding field null and explain the ambiguity.\n"
        "- Stay inside the schema. Do not add new keys.\n"
        "- Prefer a short, faithful interpretation over a clever one.\n"
        "- Use evidence_spans to point to the exact wording that supports your interpretation.\n"
        "- If the request only changes one area, keep unrelated domains out of focus.\n"
        "- Geometry and source are interpreted candidates only; final execution decisions happen later.\n"
        "Examples:\n"
        '- User: "10 mm x 20 mm x 30 mm copper box target"\n'
        '  geometry_candidate.kind_candidate = "box"\n'
        '  geometry_candidate.dimension_hints.size_triplet_mm = [10,20,30]\n'
        '  geometry_candidate.material_candidate = "G4_Cu"\n'
        '- User: "gamma point source 1 MeV at (0,0,-20) mm along +z"\n'
        '  source_candidate.source_type_candidate = "point"\n'
        '  source_candidate.particle_candidate = "gamma"\n'
        '  source_candidate.energy_candidate_mev = 1.0\n'
        '  source_candidate.position_mode = "absolute"\n'
        '  source_candidate.direction_mode = "explicit_vector"\n'
        f"Context: {context_summary}\n"
        f"User: {user_text}\n"
        "JSON:"
    )
