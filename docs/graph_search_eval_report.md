# 候选图搜索几何求解评测报告

- 样本数: 15
- Top-1 准确率: 0.800
- Top-3 召回率: 1.000
- unknown 精确率: 0.500

## 失败样例
- `shell_en_1`: expected=shell, predicted=unknown, ranked=[('single_tubs', 0.26301698021696984), ('single_sphere', 0.26301698021696984), ('shell', 0.24708158695757504)]
- `grid_zh_1`: expected=grid, predicted=single_box, ranked=[('single_box', 0.46375227522788315), ('grid', 0.17017894822957993), ('ring', 0.11322200304401175)]
- `nest_zh_1`: expected=nest, predicted=unknown, ranked=[('nest', 0.274085594182222), ('single_tubs', 0.274085594182222), ('single_sphere', 0.274085594182222)]
