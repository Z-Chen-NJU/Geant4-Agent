# Multi-turn Dialogue Evaluation (2026-03-03)

- Runtime: strict slot-first + dialogue agent v2
- Ollama: http://114.212.130.6:11434 / qwen3:14b
- Cases: 4 scenarios x 2 languages

## MT1 Progressive fill without overwrite

### EN | FAIL

- Metrics: `{"turn_count": 3, "confirm_overwrite_count": 1, "summarize_progress_count": 0, "explain_choice_count": 0, "final_action": "confirm_overwrite", "final_complete": true, "final_missing": []}`
- Checks: 4/5
- Final config snapshot:
```json
{
  "geometry": {
    "structure": "single_box",
    "params": {
      "module_x": 50.0,
      "module_y": 50.0,
      "module_z": 50.0
    },
    "root_name": "box"
  },
  "materials": {
    "selected_materials": [
      "G4_Si"
    ],
    "volume_material_map": {
      "box": "G4_Si"
    }
  },
  "source": {
    "type": "point",
    "particle": "gamma",
    "energy": 0.5,
    "position": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        -20.0
      ]
    },
    "direction": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        1.0
      ]
    }
  },
  "physics": {
    "physics_list": "FTFP_BERT",
    "selection_source": "explicit_request"
  },
  "output": {
    "format": "json",
    "path": "output/result.json"
  }
}
```
- Final dialogue trace:
```json
{
  "action": "confirm_overwrite",
  "user_intent": "SET",
  "asked_fields": [],
  "updated_paths": [],
  "missing_fields": [],
  "answered_this_turn": [],
  "overwrite_preview": [
    {
      "path": "source.position",
      "field": "source position",
      "old": {
        "type": "vector",
        "value": [
          0.0,
          0.0,
          -20.0
        ]
      },
      "new": {
        "type": "vector",
        "value": [
          0.0,
          0.0,
          -100.0
        ]
      },
      "producer": "slot_mapper"
    }
  ],
  "explanation": {}
}
```
- Raw dialogue:
```json
[
  {
    "role": "user",
    "content": "Create a 50 mm silicon box detector."
  },
  {
    "role": "assistant",
    "content": "Please provide: source type, particle type"
  },
  {
    "role": "user",
    "content": "Use a gamma point source, energy 0.5 MeV, at (0,0,-20) mm, direction +z."
  },
  {
    "role": "assistant",
    "content": "Please provide: physics list, output format"
  },
  {
    "role": "user",
    "content": "Use FTFP_BERT and output json."
  },
  {
    "role": "assistant",
    "content": "An existing confirmed value would be overwritten. Please confirm whether to apply this change: source position: {'type': 'vector', 'value': [0.0, 0.0, -20.0]} -> {'type': 'vector', 'value': [0.0, 0.0, -100.0]}."
  }
]
```

### ZH | FAIL

- Metrics: `{"turn_count": 3, "confirm_overwrite_count": 2, "summarize_progress_count": 0, "explain_choice_count": 0, "final_action": "confirm_overwrite", "final_complete": true, "final_missing": []}`
- Checks: 3/5
- Final config snapshot:
```json
{
  "geometry": {
    "structure": "single_box",
    "params": {
      "module_x": 1000.0,
      "module_y": 1000.0,
      "module_z": 1000.0
    },
    "root_name": "box"
  },
  "materials": {
    "selected_materials": [
      "G4_Cu"
    ],
    "volume_material_map": {
      "box": "G4_Cu"
    }
  },
  "source": {
    "type": "point",
    "particle": "gamma",
    "energy": 1.0,
    "position": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        -100.0
      ]
    },
    "direction": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        1.0
      ]
    }
  },
  "physics": {
    "physics_list": "FTFP_BERT",
    "selection_source": "explicit_request"
  },
  "output": {
    "format": "root",
    "path": "output/result.root"
  }
}
```
- Final dialogue trace:
```json
{
  "action": "confirm_overwrite",
  "user_intent": "QUESTION",
  "asked_fields": [],
  "updated_paths": [],
  "missing_fields": [],
  "answered_this_turn": [],
  "overwrite_preview": [
    {
      "path": "source.energy",
      "field": "源能量",
      "old": 1.0,
      "new": 0.5,
      "producer": "slot_mapper"
    },
    {
      "path": "source.position",
      "field": "源位置",
      "old": {
        "type": "vector",
        "value": [
          0.0,
          0.0,
          -100.0
        ]
      },
      "new": {
        "type": "vector",
        "value": [
          0.0,
          0.0,
          -20.0
        ]
      },
      "producer": "slot_mapper"
    }
  ],
  "explanation": {}
}
```
- Raw dialogue:
```json
[
  {
    "role": "user",
    "content": "????50???????????"
  },
  {
    "role": "assistant",
    "content": "请补充：几何结构类型, 几何参数 module_x"
  },
  {
    "role": "user",
    "content": "??gamma?????0.5 MeV????(0,0,-20)?????+z?"
  },
  {
    "role": "assistant",
    "content": "检测到将覆盖已确认的内容。请确认是否应用以下修改：源能量: 1.0 -> 0.5；源位置: {'type': 'vector', 'value': [0.0, 0.0, -100.0]} -> {'type': 'vector', 'value': [0.0, 0.0, -20.0]}。"
  },
  {
    "role": "user",
    "content": "?????FTFP_BERT???json?"
  },
  {
    "role": "assistant",
    "content": "检测到将覆盖已确认的内容。请确认是否应用以下修改：源能量: 1.0 -> 0.5；源位置: {'type': 'vector', 'value': [0.0, 0.0, -100.0]} -> {'type': 'vector', 'value': [0.0, 0.0, -20.0]}。"
  }
]
```

## MT2 Overwrite plus unrelated completion while pending confirmation

### EN | PASS

- Metrics: `{"turn_count": 4, "confirm_overwrite_count": 1, "summarize_progress_count": 0, "explain_choice_count": 0, "final_action": "finalize", "final_complete": true, "final_missing": []}`
- Checks: 4/4
- Final config snapshot:
```json
{
  "geometry": {
    "structure": "single_box",
    "params": {
      "module_x": 1000.0,
      "module_y": 1000.0,
      "module_z": 1000.0
    },
    "root_name": "box"
  },
  "materials": {
    "selected_materials": [
      "G4_Cu"
    ],
    "volume_material_map": {
      "box": "G4_Cu"
    }
  },
  "source": {
    "type": "point",
    "particle": "gamma",
    "energy": 0.5,
    "position": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        -100.0
      ]
    },
    "direction": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        1.0
      ]
    }
  },
  "physics": {
    "physics_list": "FTFP_BERT",
    "selection_source": "explicit_request"
  },
  "output": {
    "format": "json",
    "path": "output/result.root"
  }
}
```
- Final dialogue trace:
```json
{
  "action": "finalize",
  "user_intent": "CONFIRM",
  "asked_fields": [],
  "updated_paths": [],
  "missing_fields": [],
  "answered_this_turn": [],
  "overwrite_preview": [],
  "explanation": {}
}
```
- Raw dialogue:
```json
[
  {
    "role": "user",
    "content": "Set up a 1 m copper box target with gamma source, energy 1 MeV, source at (0,0,-100) mm, direction +z, physics FTFP_BERT, output root."
  },
  {
    "role": "assistant",
    "content": "Configuration complete."
  },
  {
    "role": "user",
    "content": "Change source energy to 0.5 MeV and also change output format to json."
  },
  {
    "role": "assistant",
    "content": "An existing confirmed value would be overwritten. Please confirm whether to apply this change: source energy: 1.0 -> 0.5; output format: root -> json."
  },
  {
    "role": "user",
    "content": "Output json."
  },
  {
    "role": "assistant",
    "content": "Configuration complete."
  },
  {
    "role": "user",
    "content": "confirm"
  },
  {
    "role": "assistant",
    "content": "Configuration complete."
  }
]
```

### ZH | FAIL

- Metrics: `{"turn_count": 4, "confirm_overwrite_count": 3, "summarize_progress_count": 0, "explain_choice_count": 0, "final_action": "confirm_overwrite", "final_complete": false, "final_missing": ["materials.volume_material_map"]}`
- Checks: 1/4
- Final config snapshot:
```json
{
  "geometry": {
    "structure": "single_box",
    "params": {
      "module_x": 1000.0,
      "module_y": 1000.0,
      "module_z": 1000.0
    },
    "root_name": "box"
  },
  "materials": {
    "selected_materials": [],
    "volume_material_map": {}
  },
  "source": {
    "type": "beam",
    "particle": "gamma",
    "energy": 1.0,
    "position": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        -100.0
      ]
    },
    "direction": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        1.0
      ]
    }
  },
  "physics": {
    "physics_list": "FTFP_BERT",
    "selection_source": "explicit_request"
  },
  "output": {
    "format": "root",
    "path": "output/result.root"
  }
}
```
- Final dialogue trace:
```json
{
  "action": "confirm_overwrite",
  "user_intent": "QUESTION",
  "asked_fields": [],
  "updated_paths": [],
  "missing_fields": [
    "materials.volume_material_map"
  ],
  "answered_this_turn": [],
  "overwrite_preview": [
    {
      "path": "source.energy",
      "field": "源能量",
      "old": 1.0,
      "new": 0.5,
      "producer": "slot_mapper"
    },
    {
      "path": "output.format",
      "field": "输出格式",
      "old": "root",
      "new": "json",
      "producer": "slot_mapper"
    }
  ],
  "explanation": {}
}
```
- Raw dialogue:
```json
[
  {
    "role": "user",
    "content": "????1?????????gamma????1 MeV???(0,0,-100)?????+z??????FTFP_BERT???ROOT?"
  },
  {
    "role": "assistant",
    "content": "请补充：几何结构类型, 几何参数 module_x"
  },
  {
    "role": "user",
    "content": "??????0.5 MeV??????????json?"
  },
  {
    "role": "assistant",
    "content": "检测到将覆盖已确认的内容。请确认是否应用以下修改：源能量: 1.0 -> 0.5；输出格式: root -> json。"
  },
  {
    "role": "user",
    "content": "??json?"
  },
  {
    "role": "assistant",
    "content": "检测到将覆盖已确认的内容。请确认是否应用以下修改：源能量: 1.0 -> 0.5；输出格式: root -> json。"
  },
  {
    "role": "user",
    "content": "??"
  },
  {
    "role": "assistant",
    "content": "检测到将覆盖已确认的内容。请确认是否应用以下修改：源能量: 1.0 -> 0.5；输出格式: root -> json。"
  }
]
```

## MT3 Recommendation then explanation follow-up

### EN | PASS

- Metrics: `{"turn_count": 2, "confirm_overwrite_count": 0, "summarize_progress_count": 0, "explain_choice_count": 2, "final_action": "explain_choice", "final_complete": true, "final_missing": []}`
- Checks: 4/4
- Final config snapshot:
```json
{
  "geometry": {
    "structure": "single_box",
    "params": {
      "module_x": 20.0,
      "module_y": 20.0,
      "module_z": 20.0
    },
    "root_name": "box"
  },
  "materials": {
    "selected_materials": [
      "G4_Cu"
    ],
    "volume_material_map": {
      "box": "G4_Cu"
    }
  },
  "source": {
    "type": "point",
    "particle": "gamma",
    "energy": 1.0,
    "position": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        -50.0
      ]
    },
    "direction": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        1.0
      ]
    }
  },
  "physics": {
    "physics_list": "QGSP_BERT",
    "selection_source": "llm_recommender"
  },
  "output": {
    "format": "root",
    "path": "output/result.root"
  }
}
```
- Final dialogue trace:
```json
{
  "action": "explain_choice",
  "user_intent": "QUESTION",
  "asked_fields": [],
  "updated_paths": [],
  "missing_fields": [],
  "answered_this_turn": [],
  "overwrite_preview": [],
  "explanation": {
    "materials": {
      "label": "Materials",
      "field": "materials.selected_materials",
      "source": "explicit_request",
      "reasons": [
        "Material provided explicitly by user or extracted semantics."
      ]
    },
    "source": {
      "label": "Source",
      "field": "source type",
      "source": "explicit_request",
      "reasons": [
        "Source parameters provided explicitly by user or extracted semantics."
      ]
    },
    "physics": {
      "label": "Physics",
      "field": "physics list",
      "source": "llm_recommender",
      "reasons": [
        "Selected by rule-backed fallback recommender for current request semantics."
      ]
    }
  }
}
```
- Raw dialogue:
```json
[
  {
    "role": "user",
    "content": "Set up a 20 mm copper box target with a 1 MeV gamma point source at (0,0,-50) mm along +z. Choose the most suitable Geant4 reference physics list for gamma attenuation and output root."
  },
  {
    "role": "assistant",
    "content": "Physics: physics list. Source: llm_recommender. Reason: Selected by rule-backed fallback recommender for current request semantics.. Materials: materials.selected_materials. Source: explicit_request. Reason: Material provided explicitly by user or extracted semantics.. Source: source type. Source: explicit_request. Reason: Source parameters provided explicitly by user or extracted semantics.."
  },
  {
    "role": "user",
    "content": "Why did you choose that physics list?"
  },
  {
    "role": "assistant",
    "content": "Physics: physics list. Source: llm_recommender. Reason: Selected by rule-backed fallback recommender for current request semantics.. Materials: materials.selected_materials. Source: explicit_request. Reason: Material provided explicitly by user or extracted semantics.. Source: source type. Source: explicit_request. Reason: Source parameters provided explicitly by user or extracted semantics.."
  }
]
```

### ZH | FAIL

- Metrics: `{"turn_count": 2, "confirm_overwrite_count": 0, "summarize_progress_count": 0, "explain_choice_count": 0, "final_action": "ask_clarification", "final_complete": false, "final_missing": ["geometry.structure", "geometry.params.module_x", "geometry.params.module_y", "geometry.params.module_z", "materials.volume_material_map", "physics.physics_list"]}`
- Checks: 1/4
- Final config snapshot:
```json
{
  "geometry": {
    "structure": null,
    "params": {},
    "root_name": null
  },
  "materials": {
    "selected_materials": [],
    "volume_material_map": {}
  },
  "source": {
    "type": "point",
    "particle": "gamma",
    "energy": 1.0,
    "position": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        -100.0
      ]
    },
    "direction": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        1.0
      ]
    }
  },
  "physics": {
    "physics_list": null,
    "selection_source": null
  },
  "output": {
    "format": "root",
    "path": "output/result.root"
  }
}
```
- Final dialogue trace:
```json
{
  "action": "ask_clarification",
  "user_intent": "OTHER",
  "asked_fields": [
    "geometry.params.module_y",
    "geometry.params.module_z"
  ],
  "updated_paths": [
    "geometry.params.module_x",
    "geometry.params.module_y",
    "geometry.params.module_z",
    "source.type",
    "source.particle",
    "source.energy",
    "source.position",
    "source.direction",
    "output.format"
  ],
  "missing_fields": [
    "geometry.structure",
    "geometry.params.module_x",
    "geometry.params.module_y",
    "geometry.params.module_z",
    "materials.volume_material_map",
    "physics.physics_list"
  ],
  "answered_this_turn": [
    "source.position"
  ],
  "overwrite_preview": [],
  "explanation": {}
}
```
- Raw dialogue:
```json
[
  {
    "role": "user",
    "content": "????20??????????1 MeV?gamma?????(0,0,-50)????+z??????gamma????????Geant4??????????ROOT?"
  },
  {
    "role": "assistant",
    "content": "请补充：几何结构类型, 几何参数 module_x"
  },
  {
    "role": "user",
    "content": "????????????"
  },
  {
    "role": "assistant",
    "content": "请补充：几何参数 module_y, 几何参数 module_z"
  }
]
```

## MT4 Repeated confirmation cycles

### EN | PASS

- Metrics: `{"turn_count": 5, "confirm_overwrite_count": 2, "summarize_progress_count": 0, "explain_choice_count": 0, "final_action": "finalize", "final_complete": true, "final_missing": []}`
- Checks: 4/4
- Final config snapshot:
```json
{
  "geometry": {
    "structure": "single_box",
    "params": {
      "module_x": 1000.0,
      "module_y": 1000.0,
      "module_z": 1000.0
    },
    "root_name": "box"
  },
  "materials": {
    "selected_materials": [
      "G4_Al"
    ],
    "volume_material_map": {
      "box": "G4_Al"
    }
  },
  "source": {
    "type": "point",
    "particle": "gamma",
    "energy": 1.0,
    "position": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        -100.0
      ]
    },
    "direction": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        1.0
      ]
    }
  },
  "physics": {
    "physics_list": "FTFP_BERT",
    "selection_source": "explicit_request"
  },
  "output": {
    "format": "json",
    "path": "output/result.root"
  }
}
```
- Final dialogue trace:
```json
{
  "action": "finalize",
  "user_intent": "CONFIRM",
  "asked_fields": [],
  "updated_paths": [
    "output.format"
  ],
  "missing_fields": [],
  "answered_this_turn": [],
  "overwrite_preview": [],
  "explanation": {}
}
```
- Raw dialogue:
```json
[
  {
    "role": "user",
    "content": "Set up a 1 m copper box target with gamma source, energy 1 MeV, source at (0,0,-100) mm, direction +z, physics FTFP_BERT, output root."
  },
  {
    "role": "assistant",
    "content": "Configuration complete."
  },
  {
    "role": "user",
    "content": "Change material to G4_Al."
  },
  {
    "role": "assistant",
    "content": "An existing confirmed value would be overwritten. Please confirm whether to apply this change: materials.selected_materials: ['G4_Cu'] -> ['G4_Al']."
  },
  {
    "role": "user",
    "content": "confirm"
  },
  {
    "role": "assistant",
    "content": "Configuration complete."
  },
  {
    "role": "user",
    "content": "Change output format to json."
  },
  {
    "role": "assistant",
    "content": "An existing confirmed value would be overwritten. Please confirm whether to apply this change: output format: root -> json."
  },
  {
    "role": "user",
    "content": "confirm"
  },
  {
    "role": "assistant",
    "content": "Configuration complete."
  }
]
```

### ZH | FAIL

- Metrics: `{"turn_count": 5, "confirm_overwrite_count": 0, "summarize_progress_count": 0, "explain_choice_count": 3, "final_action": "explain_choice", "final_complete": true, "final_missing": []}`
- Checks: 1/4
- Final config snapshot:
```json
{
  "geometry": {
    "structure": "single_box",
    "params": {
      "module_x": 1000.0,
      "module_y": 1000.0,
      "module_z": 1000.0
    },
    "root_name": "box"
  },
  "materials": {
    "selected_materials": [
      "G4_Cu"
    ],
    "volume_material_map": {
      "box": "G4_Cu"
    }
  },
  "source": {
    "type": "beam",
    "particle": "gamma",
    "energy": 1.0,
    "position": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        -100.0
      ]
    },
    "direction": {
      "type": "vector",
      "value": [
        0.0,
        0.0,
        1.0
      ]
    }
  },
  "physics": {
    "physics_list": "FTFP_BERT",
    "selection_source": "explicit_request"
  },
  "output": {
    "format": "root",
    "path": "output/result.root"
  }
}
```
- Final dialogue trace:
```json
{
  "action": "explain_choice",
  "user_intent": "QUESTION",
  "asked_fields": [],
  "updated_paths": [],
  "missing_fields": [],
  "answered_this_turn": [],
  "overwrite_preview": [],
  "explanation": {
    "materials": {
      "label": "材料",
      "field": "materials.selected_materials",
      "source": "explicit_request",
      "reasons": [
        "Material provided explicitly by user or extracted semantics."
      ]
    },
    "source": {
      "label": "源",
      "field": "源类型",
      "source": "explicit_request",
      "reasons": [
        "Source parameters provided explicitly by user or extracted semantics."
      ]
    },
    "physics": {
      "label": "物理",
      "field": "物理列表",
      "source": "explicit_request",
      "reasons": [
        "Physics list provided explicitly by user or extracted semantics."
      ]
    }
  }
}
```
- Raw dialogue:
```json
[
  {
    "role": "user",
    "content": "????1?????????gamma????1 MeV???(0,0,-100)?????+z??????FTFP_BERT???ROOT?"
  },
  {
    "role": "assistant",
    "content": "配置已完成。"
  },
  {
    "role": "user",
    "content": "?????G4_Al?"
  },
  {
    "role": "assistant",
    "content": "物理：物理列表。来源：explicit_request。原因：Physics list provided explicitly by user or extracted semantics.。材料：materials.selected_materials。来源：explicit_request。原因：Material provided explicitly by user or extracted semantics.。源：源类型。来源：explicit_request。原因：Source parameters provided explicitly by user or extracted semantics.。"
  },
  {
    "role": "user",
    "content": "??"
  },
  {
    "role": "assistant",
    "content": "物理：物理列表。来源：explicit_request。原因：Physics list provided explicitly by user or extracted semantics.。材料：materials.selected_materials。来源：explicit_request。原因：Material provided explicitly by user or extracted semantics.。源：源类型。来源：explicit_request。原因：Source parameters provided explicitly by user or extracted semantics.。"
  },
  {
    "role": "user",
    "content": "???????json?"
  },
  {
    "role": "assistant",
    "content": "配置已完成。"
  },
  {
    "role": "user",
    "content": "??"
  },
  {
    "role": "assistant",
    "content": "物理：物理列表。来源：explicit_request。原因：Physics list provided explicitly by user or extracted semantics.。材料：materials.selected_materials。来源：explicit_request。原因：Material provided explicitly by user or extracted semantics.。源：源类型。来源：explicit_request。原因：Source parameters provided explicitly by user or extracted semantics.。"
  }
]
```
