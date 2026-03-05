# Ollama 开启回归报告（多轮）

## 运行配置
- config_path: nlu/bert_lab/configs/ollama_config.json
- provider: ollama
- base_url: http://localhost:11434
- model: qwen3:14b
- min_confidence: 0.6

## 连接探针
- connectivity_ok: False
- model_count: 0
- models(sample): []
- error: <urlopen error [WinError 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。>

## 总体指标
- 用例数: 5
- 语言自然化平均分: 0.847
- 准确性平均分: 1.000
- 严格通过率: 100.00%
- LLM 使用回合占比: 0.00%
- 未通过用例: []

## 逐例（含 raw dialogue）
### ollama_case01_box_full
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 1.0, 'naturalness_score': 0.8}
- accuracy: 1.000 (6/6)
- strict_pass: True
- llm_used_turn_ratio: 0.00
- turns:
  - turn 1 user: 我要一个铜立方体，尺寸 1m x 1m x 1m。Gamma 点源，能量 1 MeV，位置在中心，方向 +z，物理列表 FTFP_BERT，输出 json。
    assistant: 配置已完成。
    action=finalize, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=[]
- raw_dialogue:
```json
[
  {
    "role": "user",
    "content": "我要一个铜立方体，尺寸 1m x 1m x 1m。Gamma 点源，能量 1 MeV，位置在中心，方向 +z，物理列表 FTFP_BERT，输出 json。"
  },
  {
    "role": "assistant",
    "content": "配置已完成。"
  }
]
```

### ollama_case02_box_two_turns
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 0.5, 'naturalness_score': 0.9}
- accuracy: 1.000 (5/5)
- strict_pass: True
- llm_used_turn_ratio: 0.00
- turns:
  - turn 1 user: 铜立方体 1m x 1m x 1m，gamma 点源，1 MeV，位置原点，方向 +z。
    assistant: 几何：已同步几何结构类型, 几何参数 module_x, 几何参数 module_y。材料：已同步materials.selected_materials, 体积与材料绑定, 材料选择来源。源：已同步粒子类型, 源类型, 源能量。物理：待补充物理列表。输出：待补充输出格式, 输出路径。
    action=summarize_progress, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=['physics.physics_list', 'output.format', 'output.path']
  - turn 2 user: 物理列表 QBBC，输出 root。
    assistant: 配置已完成。
    action=finalize, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=[]
- raw_dialogue:
```json
[
  {
    "role": "user",
    "content": "铜立方体 1m x 1m x 1m，gamma 点源，1 MeV，位置原点，方向 +z。"
  },
  {
    "role": "assistant",
    "content": "几何：已同步几何结构类型, 几何参数 module_x, 几何参数 module_y。材料：已同步materials.selected_materials, 体积与材料绑定, 材料选择来源。源：已同步粒子类型, 源类型, 源能量。物理：待补充物理列表。输出：待补充输出格式, 输出路径。"
  },
  {
    "role": "user",
    "content": "物理列表 QBBC，输出 root。"
  },
  {
    "role": "assistant",
    "content": "配置已完成。"
  }
]
```

### ollama_case03_tubs_two_turns
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 0.5, 'naturalness_score': 0.9}
- accuracy: 1.000 (5/5)
- strict_pass: True
- llm_used_turn_ratio: 0.00
- turns:
  - turn 1 user: 我要圆柱铜靶，半径 30 mm，半长 50 mm，gamma 点源 2 MeV，位置(0,0,-100)，方向(0,0,1)。
    assistant: 几何：已同步几何结构类型, 几何参数 child_rmax, 几何参数 child_hz。材料：已同步materials.selected_materials, 体积与材料绑定, 材料选择来源。源：已同步粒子类型, 源类型, 源能量。物理：待补充物理列表。输出：待补充输出格式, 输出路径。
    action=summarize_progress, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=['physics.physics_list', 'output.format', 'output.path']
  - turn 2 user: 物理列表 QBBC，输出 json。
    assistant: 配置已完成。
    action=finalize, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=[]
- raw_dialogue:
```json
[
  {
    "role": "user",
    "content": "我要圆柱铜靶，半径 30 mm，半长 50 mm，gamma 点源 2 MeV，位置(0,0,-100)，方向(0,0,1)。"
  },
  {
    "role": "assistant",
    "content": "几何：已同步几何结构类型, 几何参数 child_rmax, 几何参数 child_hz。材料：已同步materials.selected_materials, 体积与材料绑定, 材料选择来源。源：已同步粒子类型, 源类型, 源能量。物理：待补充物理列表。输出：待补充输出格式, 输出路径。"
  },
  {
    "role": "user",
    "content": "物理列表 QBBC，输出 json。"
  },
  {
    "role": "assistant",
    "content": "配置已完成。"
  }
]
```

### ollama_case04_overwrite_confirm
- naturalness: {'internal_field_leak_rate': 0.3333333333333333, 'template_rate': 0.0, 'short_reply_rate': 0.6666666666666666, 'naturalness_score': 0.7}
- accuracy: 1.000 (3/3)
- strict_pass: True
- llm_used_turn_ratio: 0.00
- turns:
  - turn 1 user: 铜立方体 1m x 1m x 1m，gamma 点源 1 MeV，位置中心，方向 +z，物理 FTFP_BERT，输出 json。
    assistant: 配置已完成。
    action=finalize, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=[]
  - turn 2 user: 把材料改成 G4_Al。
    assistant: 检测到将覆盖已确认的内容。请确认是否应用以下修改：materials.selected_materials: ['G4_Cu'] -> ['G4_Al']。
    action=confirm_overwrite, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=[]
  - turn 3 user: 确认。
    assistant: 配置已完成。
    action=finalize, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=[]
- raw_dialogue:
```json
[
  {
    "role": "user",
    "content": "铜立方体 1m x 1m x 1m，gamma 点源 1 MeV，位置中心，方向 +z，物理 FTFP_BERT，输出 json。"
  },
  {
    "role": "assistant",
    "content": "配置已完成。"
  },
  {
    "role": "user",
    "content": "把材料改成 G4_Al。"
  },
  {
    "role": "assistant",
    "content": "检测到将覆盖已确认的内容。请确认是否应用以下修改：materials.selected_materials: ['G4_Cu'] -> ['G4_Al']。"
  },
  {
    "role": "user",
    "content": "确认。"
  },
  {
    "role": "assistant",
    "content": "配置已完成。"
  }
]
```

### ollama_case05_source_split
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 0.3333333333333333, 'naturalness_score': 0.9333333333333333}
- accuracy: 1.000 (5/5)
- strict_pass: True
- llm_used_turn_ratio: 0.00
- turns:
  - turn 1 user: 铜立方体 1m x 1m x 1m，gamma 点源。
    assistant: 几何：已同步几何结构类型, 几何参数 module_x, 几何参数 module_y。材料：已同步materials.selected_materials, 体积与材料绑定, 材料选择来源。源：已同步粒子类型, 源类型, 源选择来源；待补充源能量, 源位置。物理：待补充物理列表。输出：待补充输出格式, 输出路径。
    action=summarize_progress, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=['source.energy', 'source.position', 'source.direction', 'physics.physics_list', 'output.format', 'output.path']
  - turn 2 user: 能量 1 MeV，位置 (0,0,0)，方向 +z。
    assistant: 几何：已确认几何根体积名。材料：已确认材料选择依据, 材料选择来源。源：已同步源能量, 源位置, 源方向。物理：待补充物理列表。输出：待补充输出格式, 输出路径。
    action=summarize_progress, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=['physics.physics_list', 'output.format', 'output.path']
  - turn 3 user: 物理 FTFP_BERT，输出 json。
    assistant: 配置已完成。
    action=finalize, llm_used=False, fallback=E_LLM_FRAME_CALL_FAILED, missing=[]
- raw_dialogue:
```json
[
  {
    "role": "user",
    "content": "铜立方体 1m x 1m x 1m，gamma 点源。"
  },
  {
    "role": "assistant",
    "content": "几何：已同步几何结构类型, 几何参数 module_x, 几何参数 module_y。材料：已同步materials.selected_materials, 体积与材料绑定, 材料选择来源。源：已同步粒子类型, 源类型, 源选择来源；待补充源能量, 源位置。物理：待补充物理列表。输出：待补充输出格式, 输出路径。"
  },
  {
    "role": "user",
    "content": "能量 1 MeV，位置 (0,0,0)，方向 +z。"
  },
  {
    "role": "assistant",
    "content": "几何：已确认几何根体积名。材料：已确认材料选择依据, 材料选择来源。源：已同步源能量, 源位置, 源方向。物理：待补充物理列表。输出：待补充输出格式, 输出路径。"
  },
  {
    "role": "user",
    "content": "物理 FTFP_BERT，输出 json。"
  },
  {
    "role": "assistant",
    "content": "配置已完成。"
  }
]
```
