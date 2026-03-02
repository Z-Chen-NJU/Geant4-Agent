# Real-Language E2E Evaluation (2026-03-02)

## Environment
- Remote Ollama: `http://114.212.130.6:11434`
- Model: `qwen3:14b`
- Path: strict `slot-first` orchestration
- Key switches: `llm_router=true`, `normalize_input=true`, `llm_question=false`

## Cases

### 1. English full box, single turn
Input:
- `Please set up a 1 m x 1 m x 1 m copper box target with a gamma point source at (0,0,-100) mm pointing +z, energy 1 MeV, physics FTFP_BERT, output ROOT.`

Result:
- `llm_used=true`
- `inference_backend=llm_slot_frame+runtime_semantic`
- `is_complete=true`
- Geometry correct: `single_box`, `module_x/y/z=1000`
- Material correct: `G4_Cu`, `volume_material_map={"box":"G4_Cu"}`
- Source correct: point, gamma, 1 MeV, position/direction vectors
- Physics correct at schema level: `FTFP_BERT`
- Output correct: `root`, default path generated

Assessment:
- Pass

### 2. Chinese full box, single turn
Input:
- `我想做一个1米见方的铜立方体靶，用gamma点源照射，源放在(0,0,-100)毫米，沿+z方向，能量1MeV，物理列表用FTFP_BERT，输出ROOT。`

Result:
- `llm_used=true`
- `inference_backend=llm_slot_frame+runtime_semantic`
- `is_complete=false`
- Source / physics / output filled
- Geometry missing entirely
- Material degraded to `selected_materials=["null"]`
- Missing fields: geometry + volume material map

Assessment:
- Fail
- Root symptom: Chinese slot extraction is unstable; slot parser accepted a string-like `null` material and lost geometry slots.

### 3. English two-turn, explicit material modification
Turn 1:
- Same as case 1
- Complete and correct

Turn 2:
- `Actually change the target material to aluminum, keep everything else the same.`

Result after turn 2:
- `llm_used=true`
- `is_complete=true`
- `selected_materials=["G4_Al"]`
- `volume_material_map` remained `{"box":"G4_Cu"}`

Assessment:
- Partial pass
- User explicit overwrite works
- Derived field synchronization is still broken

### 4. Chinese implicit physics recommendation
Input:
- `这是纯gamma在铜中的衰减测试，不涉及强子。请帮我建立一个10厘米见方的铜立方体靶，源是1MeV点源，放在原点，沿+z发射。请你自行选择一个合适的Geant4预置物理列表，并输出ROOT。`

Result:
- `llm_used=true`
- `is_complete=true`
- Geometry, material, source, output all filled
- Physics list selected as `FTFP_BERT`
- `selection_reasons=[]`
- `selection_source=null`

Assessment:
- Schema pass, semantic pass is questionable
- The system completed the config, but the physics choice is not auditable and is not clearly justified for a pure gamma attenuation request.

### 5. English cylinder, single turn
Input:
- `Create a copper cylinder target with radius 30 mm and half-length 50 mm, using a gamma point source at (0,0,-100) mm toward +z, energy 2 MeV, physics FTFP_BERT, output json.`

Result:
- `llm_used=true`
- `is_complete=true`
- Geometry: `single_tubs`
- `child_rmax=30`
- `child_hz=100`
- Material / source / output all filled

Assessment:
- Partial pass
- Structure family mapping now works
- But `half-length 50 mm` was interpreted as `child_hz=100`, i.e. semantic scaling is wrong.

## Summary
- Strongly improved:
  - English explicit requests
  - Box and cylinder structure families
  - Strict path now genuinely runs through `slot-first`
- Still weak:
  - Chinese free-form geometry/material extraction
  - Derived-field synchronization (`selected_materials` vs `volume_material_map`)
  - Semantic normalization for domain-specific units (`half-length`)
  - Physics recommendation provenance and justification

## Next-round architecture tasks
1. Add a slot null-sanitizer before mapping
- Reject string values such as `"null"`, `"none"`, `"unknown"` as semantic content.
- This should be implemented in slot parsing/validation, not in per-field patches.

2. Split slot value semantics from config semantics for geometry dimensions
- Introduce explicit geometry slot semantics:
  - `cylinder.radius_mm`
  - `cylinder.half_length_mm`
- Do not use generic `height_mm` for `single_tubs`.
- Map these deterministically to `child_rmax` / `child_hz`.

3. Add derived-field synchronizer stage after accepted updates
- After commit-worthy updates are chosen, run a deterministic sync stage for dependent fields:
  - `materials.selected_materials -> materials.volume_material_map`
  - possibly `geometry.structure -> geometry.root_name`
- This should be a dedicated stage, not hidden in ad-hoc defaults.

4. Separate physics recommendation intent from explicit physics selection
- Keep two distinct slots:
  - `physics.explicit_list`
  - `physics.recommendation_intent`
- If the second is used, route through recommender and require provenance fields:
  - `selection_source`
  - `selection_reasons`
- Do not allow an implicit recommendation to look identical to an explicit user choice.

5. Add multilingual normalization contract inside slot prompting
- The slot prompt should explicitly require:
  - internal English canonicalization
  - never emit placeholder literals like `null` as strings
- Add Chinese few-shot examples focused on geometry + material.

## Current conclusion
- The `slot-first` architecture is materially better than the prior direct path-update strategy.
- It is now robust for explicit English first-pass requests.
- It is not yet robust enough for free-form Chinese input or auditable physics recommendation.
- The next round should continue at the slot/mapper/synchronizer layer, not by adding local regex patches to config-path updates.
