# Assembly DSL Feasibility Prototype

This project is a theory-level feasibility checker for cross-scenario Geant4-like assemblies. It is **not** a Geant4 geometry builder, and it does not run boolean overlap checks. Instead, it provides conservative analytical checks (AABB containment and spacing inequalities) so that an upstream LLM can avoid hallucinating impossible nested structures.

## Design Principles
- No per-scenario template classes. Scenarios are expressed as data using the assembly DSL.
- A finite operator set + constraints paradigm. New scenarios should be expressed by composing existing operators first.
- Add new operators only when you encounter a truly new geometric pattern that cannot be expressed by composition.
- This is a **conservative** validator. A future step can integrate Geant4 `checkOverlaps` as a final judge.

## Structure
- `dsl.py`: DSL nodes and JSON parsing/serialization.
- `geom.py`: AABB helpers and derived spans.
- `feasibility.py`: Analytical feasibility checks and error codes.
- `library.py`: Operator-graph skeletons and sampling spaces.
- `experiments.py`: Coverage, feasibility rate, ambiguity experiments.
- `cli.py`: Command-line interface.
- `examples/`: Small CSV coverage dataset and JSON DSL examples.
- `tests/`: Smoke tests.
- `synthesize.py`: Build DSL from structure + params and run feasibility.

## Structure Diagram
```
          +------------------+
          |  DSL JSON Input  |
          +---------+--------+
                    |
                    v
            +-------+-------+
            |   dsl.py      |
            | parse/validate|
            +-------+-------+
                    |
         +----------+----------+
         |                     |
         v                     v
    +----+----+           +----+----+
    | geom.py |           | library |
    | AABB    |           | skeleton|
    +----+----+           +----+----+
         |                     |
         +----------+----------+
                    v
            +-------+-------+
            | feasibility   |
            | checks + codes|
            +-------+-------+
                    |
                    v
            +-------+-------+
            | experiments   |
            | + cli.py      |
            +---------------+
```

## Minimal Example
Run all experiments and produce outputs in `out/`:

```powershell
python -m geometry.cli run_all --outdir geometry/out --n_samples 200 --n_param_sets 100 --seed 7 --dataset geometry/examples/coverage.csv
```

Expected output files:
- `geometry/out/coverage_summary.json`
- `geometry/out/coverage_checked.jsonl`
- `geometry/out/feasibility_summary.json`
- `geometry/out/ambiguity_summary.json`

Synthesize DSL from a structure + params JSON:

```powershell
python -m geometry.cli synthesize --input geometry/examples/synth_input.json --outdir geometry/out --seed 7
```

Expected output file:
- `geometry/out/synthesis_result.json`

## Extending
- Prefer adding new DSL data instances and operator compositions.
- Only add a new operator when existing ones cannot express the structural pattern.
- Keep analytical checks conservative; do not attempt exact boolean intersections here.

---

# Assembly DSL Feasibility Prototype（中文）

该模块是跨场景 Geant4 风格装配的理论可行性检查器。**它不是** Geant4 几何构建器，也不会做精确布尔相交。它提供保守的解析检查（AABB 包含与间距不等式），以降低上游 LLM 在复杂嵌套结构上的幻觉风险。

## 设计原则
- 不提供每个场景的模板类。场景通过 DSL 数据表达。
- 采用有限算子集合 + 约束的范式，优先通过组合表达新场景。
- 只有当结构无法由现有算子组合表达时，才新增算子。
- 这是**保守**验证器；未来可接 Geant4 `checkOverlaps` 作为最终裁判。

## 结构
- `dsl.py`：DSL 节点与 JSON 解析/序列化。
- `geom.py`：AABB 与包络推导。
- `feasibility.py`：解析可行性检查与错误码。
- `library.py`：装配骨架与采样空间。
- `experiments.py`：覆盖率/可行率/歧义性实验。
- `cli.py`：命令行入口。
- `examples/`：覆盖数据集与 DSL JSON 示例。
- `tests/`：烟雾测试。
- `synthesize.py`：由结构+参数合成 DSL 并检查可行性。

## 结构流程图
```
          +------------------+
          |  DSL JSON Input  |
          +---------+--------+
                    |
                    v
            +-------+-------+
            |   dsl.py      |
            | parse/validate|
            +-------+-------+
                    |
         +----------+----------+
         |                     |
         v                     v
    +----+----+           +----+----+
    | geom.py |           | library |
    | AABB    |           | skeleton|
    +----+----+           +----+----+
         |                     |
         +----------+----------+
                    v
            +-------+-------+
            | feasibility   |
            | checks + codes|
            +-------+-------+
                    |
                    v
            +-------+-------+
            | experiments   |
            | + cli.py      |
            +---------------+
```

## 最小示例

运行全部实验并输出到 `out/`：

```powershell
python -m geometry.cli run_all --outdir geometry/out --n_samples 200 --n_param_sets 100 --seed 7 --dataset geometry/examples/coverage.csv
```

预期输出：
- `geometry/out/coverage_summary.json`
- `geometry/out/coverage_checked.jsonl`
- `geometry/out/feasibility_summary.json`
- `geometry/out/ambiguity_summary.json`

由结构+参数合成 DSL：

```powershell
python -m geometry.cli synthesize --input geometry/examples/synth_input.json --outdir geometry/out --seed 7
```

预期输出：
- `geometry/out/synthesis_result.json`

## 扩展建议
- 优先添加 DSL 数据实例与算子组合。
- 只有在现有算子无法表达新结构时才新增算子。
- 保持解析检查的保守性，不做精确布尔相交。
