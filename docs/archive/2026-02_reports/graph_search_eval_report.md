# 候选图搜索几何求解评测报告

- 样本数: 15
- Top-1 准确率: 0.800
- Top-3 召回率: 1.000
- unknown 精确率: 0.500

## 失败样例
- `shell_en_1`: expected=shell, predicted=unknown, ranked=[('single_tubs', 0.24363827845238262), ('single_sphere', 0.24363827845238262), ('shell', 0.22887698137955523)]
- `grid_zh_1`: expected=grid, predicted=single_box, ranked=[('single_box', 0.4442831304576876), ('grid', 0.11838736952032386), ('ring', 0.10846874211962663)]
- `nest_zh_1`: expected=nest, predicted=unknown, ranked=[('nest', 0.24734243168007863), ('single_tubs', 0.24734243168007863), ('single_sphere', 0.24734243168007863)]
