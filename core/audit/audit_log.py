from __future__ import annotations

from datetime import datetime, timezone

from core.orchestrator.path_ops import diff_paths
from core.orchestrator.types import SessionState, UpdateOp, ValidationReport


def append_audit_entry(
    state: SessionState,
    before_config: dict,
    after_config: dict,
    accepted_updates: list[UpdateOp],
    rejected_updates: list[dict],
    validation_report: ValidationReport,
    applied_rules: list[dict],
) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "turn_id": state.turn_id,
        "phase": state.phase.value,
        "accepted_updates": [
            {
                "path": u.path,
                "op": u.op,
                "value": u.value,
                "producer": u.producer.value,
                "confidence": u.confidence,
            }
            for u in accepted_updates
        ],
        "rejected_updates": rejected_updates,
        "applied_rules": applied_rules,
        "violations": validation_report.errors,
        "warnings": validation_report.warnings,
        "missing_required_paths": validation_report.missing_required_paths,
        "config_diff": diff_paths(before_config, after_config),
    }
    state.audit_trail.append(entry)
