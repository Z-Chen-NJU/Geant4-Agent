# Ollama 开启回归报告（多轮）

## 运行配置
- config_path: nlu/bert_lab/configs/deepseek_api.local.json
- provider: deepseek
- base_url: https://api.deepseek.com
- model: deepseek-chat
- min_confidence: 0.6

## 连接探针
- connectivity_ok: True
- model_count: 2
- models(sample): ['deepseek-chat', 'deepseek-reasoner']
- error: none

## 总体指标
- 用例数: 5
- 语言自然化平均分: 0.933
- 准确性平均分: 0.920
- 严格通过率: 60.00%
- LLM 使用回合占比: 100.00%
- 未通过用例: ['ollama_case02_box_two_turns', 'ollama_case03_tubs_two_turns']

## 逐例（含 raw dialogue）
### ollama_case01_box_full
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 1.0, 'naturalness_score': 0.8}
- accuracy: 1.000 (6/6)
- strict_pass: True
- llm_used_turn_ratio: 1.00
- turns:
  - turn 1 user: 我要一个铜立方体，尺寸 1m x 1m x 1m。Gamma 点源，能量 1 MeV，位置在中心，方向 +z，物理列表 FTFP_BERT，输出 json。
    assistant: 配置已完成。
    action=finalize, llm_used=True, fallback=None, missing=[]
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
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 0.0, 'naturalness_score': 1.0}
- accuracy: 0.800 (4/5)
- strict_pass: False
- llm_used_turn_ratio: 1.00
- turns:
  - turn 1 user: 铜立方体 1m x 1m x 1m，gamma 点源，1 MeV，位置原点，方向 +z。
    assistant: 好的，当前配置进度如下：

**几何**：已设置立方体结构，尺寸为 1m x 1m x 1m。
**材料**：已选定为铜，并绑定到几何体。
**源**：已设置为位于原点的伽马点源，能量 1 MeV，方向沿 +z 轴。

**待补充项**：
*   物理列表
*   输出格式
*   输出路径

请继续提供这些信息以完成配置。
    action=summarize_progress, llm_used=True, fallback=None, missing=['physics.physics_list', 'output.format', 'output.path']
  - turn 2 user: 物理列表 QBBC，输出 root。
    assistant: 好的，配置已完成！

根据您的设置，物理列表已选定为 **QBBC**，输出格式为 **ROOT**，输出路径将使用默认位置。物理列表的选择依据和来源也已根据您的明确要求记录在案。

所有必要信息已确认，可以生成最终的配置文件了。
    action=finalize, llm_used=True, fallback=None, missing=[]
- raw_dialogue:
```json
[
  {
    "role": "user",
    "content": "铜立方体 1m x 1m x 1m，gamma 点源，1 MeV，位置原点，方向 +z。"
  },
  {
    "role": "assistant",
    "content": "好的，当前配置进度如下：\n\n**几何**：已设置立方体结构，尺寸为 1m x 1m x 1m。\n**材料**：已选定为铜，并绑定到几何体。\n**源**：已设置为位于原点的伽马点源，能量 1 MeV，方向沿 +z 轴。\n\n**待补充项**：\n*   物理列表\n*   输出格式\n*   输出路径\n\n请继续提供这些信息以完成配置。"
  },
  {
    "role": "user",
    "content": "物理列表 QBBC，输出 root。"
  },
  {
    "role": "assistant",
    "content": "好的，配置已完成！\n\n根据您的设置，物理列表已选定为 **QBBC**，输出格式为 **ROOT**，输出路径将使用默认位置。物理列表的选择依据和来源也已根据您的明确要求记录在案。\n\n所有必要信息已确认，可以生成最终的配置文件了。"
  }
]
```

### ollama_case03_tubs_two_turns
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 0.0, 'naturalness_score': 1.0}
- accuracy: 0.800 (4/5)
- strict_pass: False
- llm_used_turn_ratio: 1.00
- turns:
  - turn 1 user: 我要圆柱铜靶，半径 30 mm，半长 50 mm，gamma 点源 2 MeV，位置(0,0,-100)，方向(0,0,1)。
    assistant: 当前配置进度如下：

**几何**：已根据你的输入，更新了圆柱靶的半径（30 mm）和半长（50 mm）。  
**材料**：已选定铜作为靶材料，并完成了体积与材料的绑定。  
**源**：已设置为 2 MeV 的伽马点源，位置和方向也已同步。  

接下来还需要确认以下设置：  
- 物理列表  
- 输出格式（如 ROOT、ASCII 等）  
- 输出文件路径  

请补充这三项信息，我们就可以继续生成完整的模拟配置了。
    action=summarize_progress, llm_used=True, fallback=None, missing=['physics.physics_list', 'output.format', 'output.path']
  - turn 2 user: 物理列表 QBBC，输出 json。
    assistant: 好的，配置已完成。

根据你的设定，物理列表已确定为 **QBBC**，输出格式为 **JSON**，输出路径将使用默认值。

所有必要信息都已确认，可以开始生成完整的模拟配置文件了。
    action=finalize, llm_used=True, fallback=None, missing=[]
- raw_dialogue:
```json
[
  {
    "role": "user",
    "content": "我要圆柱铜靶，半径 30 mm，半长 50 mm，gamma 点源 2 MeV，位置(0,0,-100)，方向(0,0,1)。"
  },
  {
    "role": "assistant",
    "content": "当前配置进度如下：\n\n**几何**：已根据你的输入，更新了圆柱靶的半径（30 mm）和半长（50 mm）。  \n**材料**：已选定铜作为靶材料，并完成了体积与材料的绑定。  \n**源**：已设置为 2 MeV 的伽马点源，位置和方向也已同步。  \n\n接下来还需要确认以下设置：  \n- 物理列表  \n- 输出格式（如 ROOT、ASCII 等）  \n- 输出文件路径  \n\n请补充这三项信息，我们就可以继续生成完整的模拟配置了。"
  },
  {
    "role": "user",
    "content": "物理列表 QBBC，输出 json。"
  },
  {
    "role": "assistant",
    "content": "好的，配置已完成。\n\n根据你的设定，物理列表已确定为 **QBBC**，输出格式为 **JSON**，输出路径将使用默认值。\n\n所有必要信息都已确认，可以开始生成完整的模拟配置文件了。"
  }
]
```

### ollama_case04_overwrite_confirm
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 0.3333333333333333, 'naturalness_score': 0.9333333333333333}
- accuracy: 1.000 (3/3)
- strict_pass: True
- llm_used_turn_ratio: 1.00
- turns:
  - turn 1 user: 铜立方体 1m x 1m x 1m，gamma 点源 1 MeV，位置中心，方向 +z，物理 FTFP_BERT，输出 json。
    assistant: 配置已完成。
    action=finalize, llm_used=True, fallback=None, missing=[]
  - turn 2 user: 把材料改成 G4_Al。
    assistant: 检测到需要覆盖已确认的材料设置，请确认是否应用以下修改：将材料从 G4_Cu 改为 G4_Al。
    action=confirm_overwrite, llm_used=True, fallback=None, missing=[]
  - turn 3 user: 确认。
    assistant: 好的，配置已更新完成。材料已从 G4_Cu 成功更改为 G4_Al。
    action=finalize, llm_used=True, fallback=None, missing=[]
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
    "content": "检测到需要覆盖已确认的材料设置，请确认是否应用以下修改：将材料从 G4_Cu 改为 G4_Al。"
  },
  {
    "role": "user",
    "content": "确认。"
  },
  {
    "role": "assistant",
    "content": "好的，配置已更新完成。材料已从 G4_Cu 成功更改为 G4_Al。"
  }
]
```

### ollama_case05_source_split
- naturalness: {'internal_field_leak_rate': 0.0, 'template_rate': 0.0, 'short_reply_rate': 0.3333333333333333, 'naturalness_score': 0.9333333333333333}
- accuracy: 1.000 (5/5)
- strict_pass: True
- llm_used_turn_ratio: 1.00
- turns:
  - turn 1 user: 铜立方体 1m x 1m x 1m，gamma 点源。
    assistant: 当前配置进度如下：

- **几何**：已设定为立方体，尺寸为 1m x 1m x 1m。
- **材料**：已选择铜，并绑定至几何体。
- **源**：已设定为 gamma 点源，还需补充能量和位置。
- **物理**：待选择物理列表。
- **输出**：待指定输出格式和保存路径。

请继续提供剩余参数。
    action=summarize_progress, llm_used=True, fallback=None, missing=['source.energy', 'source.position', 'source.direction', 'physics.physics_list', 'output.format', 'output.path']
  - turn 2 user: 能量 1 MeV，位置 (0,0,0)，方向 +z。
    assistant: 当前配置进度如下：

- **几何**：已确认根体积名称。
- **材料**：已确认材料选择依据和来源。
- **源**：已同步能量、位置和方向。
- **物理**：待补充物理列表。
- **输出**：待补充输出格式和保存路径。
    action=summarize_progress, llm_used=True, fallback=None, missing=['physics.physics_list', 'output.format', 'output.path']
  - turn 3 user: 物理 FTFP_BERT，输出 json。
    assistant: 配置已完成。
    action=finalize, llm_used=True, fallback=None, missing=[]
- raw_dialogue:
```json
[
  {
    "role": "user",
    "content": "铜立方体 1m x 1m x 1m，gamma 点源。"
  },
  {
    "role": "assistant",
    "content": "当前配置进度如下：\n\n- **几何**：已设定为立方体，尺寸为 1m x 1m x 1m。\n- **材料**：已选择铜，并绑定至几何体。\n- **源**：已设定为 gamma 点源，还需补充能量和位置。\n- **物理**：待选择物理列表。\n- **输出**：待指定输出格式和保存路径。\n\n请继续提供剩余参数。"
  },
  {
    "role": "user",
    "content": "能量 1 MeV，位置 (0,0,0)，方向 +z。"
  },
  {
    "role": "assistant",
    "content": "当前配置进度如下：\n\n- **几何**：已确认根体积名称。\n- **材料**：已确认材料选择依据和来源。\n- **源**：已同步能量、位置和方向。\n- **物理**：待补充物理列表。\n- **输出**：待补充输出格式和保存路径。"
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
