# Geometry Upgrade Roadmap (2026-03-06)

## Goal

Upgrade geometry handling from a small set of hand-wired solids into a staged, extensible geometry pipeline:

1. `LLM-first` slot extraction for common single-solid families.
2. `Operator-graph` routing for composite geometry families.
3. `Validator-first` feasibility checks as the final write gate.

The project should stop treating `geometry.structure` as a fragile three-class decision. Instead:

- single-solid families should be mapped by a shared registry;
- composite families should be routed into candidate graph synthesis;
- final config writes should remain controlled by arbiter + validator.

## Current State

### Stable today

- `single_box`
- `single_tubs`
- `single_sphere`
- single-solid ingress + validation for:
  - `single_cons`
  - `single_trd`
  - `single_polycone`
  - `single_cuttubs`
  - `single_trap`
  - `single_para`
- `single_torus`
- `single_ellipsoid`
- `single_elltube`
- `single_polyhedra`
- `single_orb`
- operator-graph routing + strict config landing for:
  - `ring`
  - `grid`
  - `nest`
  - `stack`
  - `shell`
- stack-specific natural-language ingress is now wired through:
  - raw parameter recovery for `stack_x/stack_y/t1/t2/t3`
  - `autofix` propagation into runtime graph synthesis
  - graph-root normalization so strict config stores `root=stack`
- boolean ingress now accepts natural phrases:
  - `union`
  - `subtraction`
  - `intersection`
  and routes them into canonical `bool_a_* / bool_b_*` params and `geometry.graph_program`

### Main gap

The lower layers are stronger than the user-facing geometry ingress:

- slot schema now understands a wider family set, but text normalization and target inference are still uneven across families
- BERT/rule fallback is still biased toward older common families and does not yet provide broad geometry priors
- operator families now land in strict config, but missing-parameter dialogue is still more mature for simple families than for complex assemblies

So the geometry problem is not only "missing operators". It is also "ingress and canonicalization are narrower than the underlying library".

## Design Policy

### P0

#### P0.1 Single-solid family registry

Create one shared geometry family catalog and reuse it in:

- slot validation
- slot-to-config mapping
- prompt schema
- future extractor fallback

Target families:

- `single_box`
- `single_tubs`
- `single_sphere`
- `single_cons`
- `single_trd`
- `single_polycone`
- `single_cuttubs`

#### P0.2 Operator families must not be forced into `geometry.kind`

Do not encode the following as if they were just another scalar solid kind:

- `ring`
- `grid`
- `nest`
- `stack`
- `shell`
- `boolean` as a fully general family

These should be expressed through `graph_program` / candidate-graph routing, because they are assembly operators, not single solids.

#### P0.3 Validator stays authoritative

LLM and BERT may propose geometry families and parameters.
Only validator + arbiter may commit them.

This means:

- no direct config write from raw LLM output
- all geometry params must land in canonical config paths
- scope pruning and required-path validation remain mandatory

### P1

#### P1.1 Extend LLM-first geometry ingress

After registry unification, extend slot parsing and prompt schema so the LLM can directly emit:

- `cons`
- `trd`
- `polycone`
- `cuttubs`

This is the fastest way to increase coverage without retraining BERT.

#### P1.2 Bridge operator families into main orchestration

Promote these from "candidate search only" to "mainline geometry mode":

- `ring`
- `grid`
- `nest`
- `stack`
- `shell`

Required changes:

- graph candidate chosen by runtime search must be storable as `geometry.graph_program`
- config layer must distinguish `single-solid mode` vs `operator-graph mode`
- dialogue should ask missing operator parameters directly, not collapse them back to a fake single-solid structure

### P2

#### P2.1 Add more Geant4 common solids

Recommended priority:

- `Trap`
- `Para`
- `Torus`
- `Orb`
- `Ellipsoid`
- `EllipticalTube`
- `Polyhedra`

#### P2.2 Reduce structure-centralization

Longer term, geometry should move from:

- `structure + params`

toward:

- `geometry_mode = single_solid | operator_graph`
- `graph_program` as the authoritative representation for composite cases

## Implementation Sequence

1. Introduce a shared geometry family catalog.
2. Expand slot schema and slot mapper for additional single-solid families.
3. Expand prompt schema so LLM can emit those families explicitly.
4. Add regression tests for each newly supported family.
5. Promote operator-graph cases into orchestration state and config output.
6. Revisit BERT only after LLM-first + registry unification saturates.

## Current Next Steps

### Next P1

- add operator-aware target inference for more composite phrasings beyond `stack`
- make graph-mode missing-parameter prompts family-aware instead of generic `geometry.params.*`
- run casebank regression again and inspect whether remaining geometry misses are now concentrated in unsupported solids

### Next P2

- add better `boolean` ingress than the current two-box prototype
- evaluate whether `Polyhedra` and `EllipticalTube` need synthetic training samples in the structure router, or whether LLM-first ingress is already sufficient
- extend coverage toward `polyhedra`-adjacent and transform-heavy solids rather than adding more scalar aliases

## Acceptance Criteria

### Short term

- `single_cons`, `single_trd`, `single_polycone`, `single_cuttubs` are accepted by slot parser and mapped into canonical config paths.
- no duplicated geometry family hardcoding across prompt / mapper / validator.
- regression tests cover new single-solid families.

### Mid term

- `ring/grid/nest/stack/shell` can complete end-to-end through dialogue and config output.
- geometry coverage failures in the casebank are no longer dominated by `geometry.structure` mismatch.

## Notes

- This roadmap intentionally prioritizes LLM-first ingress before BERT retraining.
- BERT still matters for extraction robustness, but geometry coverage is currently limited more by orchestration design than by model capacity.
