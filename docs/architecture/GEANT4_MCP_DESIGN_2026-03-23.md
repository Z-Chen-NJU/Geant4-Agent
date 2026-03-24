# Geant4 MCP Design (2026-03-23)

## Goal

Move the project from a web-form-style config assistant toward an agent that can:

- accept user intent
- plan the next operation
- call tools against a live Geant4-side runtime
- inspect execution state and logs
- continue iterating from observations

## Why Web UI Stops Being The Main Architecture

The current `ui/web/` path is good for local dialogue demos, but it is not the right long-term control surface for an interactive Geant4 agent.

The next system needs:

- tool-call semantics instead of only HTTP form submission
- explicit runtime phases and action guards
- structured observations from Geant4
- the ability to re-plan after execution, not only after user turns

## Proposed Layers

### 1. Agent Layer

Existing modules that still matter:

- `core/contracts/`
- `core/orchestrator/`
- `nlu/`
- `planner/`

These remain responsible for:

- interpreting user intent
- updating semantic/config state
- deciding whether the next step is clarification or execution

### 2. Runtime Boundary

New shared runtime contract:

- `core/runtime/types.py`

This layer defines:

- `RuntimeStateSnapshot`
- `ExecutionObservation`
- `ToolSpec`
- runtime phase/status enums

This keeps the agent independent from Geant4 implementation details.

### 3. MCP Geant4 Layer

New MCP-facing package:

- `mcp/geant4/tools.py`
- `mcp/geant4/adapter.py`
- `mcp/geant4/server.py`

Current minimal tool set:

- `get_runtime_state`
- `apply_config_patch`
- `initialize_run`
- `run_beam`
- `get_last_log`

This is the smallest useful closed loop for a live demo.

### 4. Geant4 Adapter Implementation

The real adapter should eventually translate tool calls into one of:

- direct Geant4 C++ API calls
- a Python binding layer if available
- controlled macro/command execution

The agent should never emit raw shell or macro strings as its primary interface.

Instead:

- agent outputs structured action
- MCP server validates it
- adapter converts it to Geant4-side operations
- adapter returns structured observation

## Recommended Runtime State Model

Suggested phases:

- `detached`
- `idle`
- `configured`
- `initialized`
- `running`
- `failed`

This matters because not every action is legal in every phase.

Examples:

- `run_beam` is invalid before `initialize_run`
- `initialize_run` should fail if source/physics/geometry are incomplete
- geometry mutation during a run may require explicit reset/reinitialize semantics

## What The Real Geant4 Side Should Expose

For the first practical integration, the Geant4 runtime side should provide:

1. current state snapshot
2. ability to apply structured config patches
3. initialize action
4. run action
5. log/error fetch

If those five are reliable, the agent loop is already demo-worthy.

## What The User Needs To Provide

To move from this design skeleton to real integration, the local environment should provide:

### Required

- a local Geant4 runtime that can be driven programmatically
- a stable way to launch or attach to that runtime
- a reproducible sample application or detector setup for demos
- clear runtime outputs/log locations

### Strongly Recommended

- a narrow adapter surface for geometry/source/physics updates
- a predictable reset/reinitialize flow
- one canonical demo scenario for early iteration

### Important Decisions You Need To Make

Please clarify these before the real adapter implementation:

1. Will Geant4 be controlled via Python bindings, C++ service wrapper, or macro execution?
2. Do you want one long-lived Geant4 process, or spawn-per-session?
3. What is the minimum interactive demo:
   - geometry change only
   - geometry + source + run
   - geometry + source + physics + run + result inspection
4. What outputs should the agent read back:
   - logs only
   - scalar summaries
   - ROOT/CSV paths
   - geometry tree/volume inspection

## Recommended Next Implementation Step

Do not expand the tool set yet.

Instead, build one real adapter that makes these work end-to-end:

- `get_runtime_state`
- `apply_config_patch`
- `initialize_run`
- `run_beam`
- `get_last_log`

Once that loop is stable, the orchestrator can decide whether a user turn should:

- ask for clarification
- patch the runtime config
- initialize
- execute
- explain errors/results
