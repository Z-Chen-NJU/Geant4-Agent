from __future__ import annotations

from core.orchestrator.types import Phase, ValidationReport
from core.validation.minimal_schema import get_local_required_paths


PHASE_TRANSITION_TABLE: dict[Phase, dict] = {
    Phase.GEOMETRY: {"accept_intents": {"SET", "MODIFY", "CONFIRM", "QUESTION"}, "next_if_local_ok": Phase.MATERIALS},
    Phase.MATERIALS: {"accept_intents": {"SET", "MODIFY", "CONFIRM", "QUESTION"}, "next_if_local_ok": Phase.SOURCE},
    Phase.SOURCE: {"accept_intents": {"SET", "MODIFY", "CONFIRM", "QUESTION"}, "next_if_local_ok": Phase.PHYSICS},
    Phase.PHYSICS: {"accept_intents": {"SET", "MODIFY", "CONFIRM", "QUESTION"}, "next_if_local_ok": Phase.OUTPUT},
    Phase.OUTPUT: {"accept_intents": {"SET", "MODIFY", "CONFIRM", "QUESTION"}, "next_if_local_ok": Phase.FINALIZE},
    Phase.FINALIZE: {"accept_intents": {"SET", "MODIFY", "CONFIRM", "QUESTION"}, "next_if_local_ok": Phase.FINALIZE},
}


def _local_phase_ok(phase: Phase, global_report: ValidationReport, *, config: dict | None = None) -> bool:
    local_required = set(get_local_required_paths(phase, config=config))
    if not local_required:
        return True
    for path in global_report.missing_required_paths:
        if path in local_required:
            return False
    return True


def decide_phase_transition(
    current_phase: Phase,
    local_report: ValidationReport,
    global_report: ValidationReport,
    *,
    config: dict | None = None,
) -> Phase:
    # local_report is accepted for interface stability; decision relies on required-path completeness.
    _ = local_report
    if current_phase == Phase.FINALIZE:
        return Phase.FINALIZE if global_report.ok else current_phase
    if _local_phase_ok(current_phase, global_report, config=config):
        return PHASE_TRANSITION_TABLE[current_phase]["next_if_local_ok"]
    return current_phase
