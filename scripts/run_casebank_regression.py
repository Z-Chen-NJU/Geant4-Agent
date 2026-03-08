from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from core.orchestrator.session_manager import process_turn, reset_session


@dataclass
class TurnResult:
    turn: int
    user: str
    assistant: str
    is_complete: bool
    missing_fields: list[str]
    dialogue_action: str
    phase: str
    llm_used: bool
    fallback_reason: str | None
    inference_backend: str
    accepted_update_count: int
    rejected_update_count: int
    pending_overwrite_required: bool
    internal_trace: dict[str, Any]


@dataclass
class CaseResult:
    case_id: str
    domain: str
    style: str
    completeness: str
    lang: str
    pass_case: bool
    fail_reasons: list[str]
    expected_initial_complete: bool
    actual_initial_complete: bool
    expected_final_complete: bool
    actual_final_complete: bool
    initial_missing_count: int
    final_missing_count: int
    expected_paths_ok: bool
    final_pending_overwrite_required: bool
    turns: list[TurnResult]
    raw_dialogue: list[dict[str, str]]
    config_snapshot: dict[str, Any]


def _latex_escape(text: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = text
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def _bool_label(v: bool, lang: str) -> str:
    if lang == "zh":
        return "通过" if v else "失败"
    return "PASS" if v else "FAIL"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _deep_get(data: Any, path: str) -> Any:
    cur = data
    for seg in path.split("."):
        if isinstance(cur, list):
            try:
                idx = int(seg)
            except ValueError:
                return None
            if idx < 0 or idx >= len(cur):
                return None
            cur = cur[idx]
            continue
        if not isinstance(cur, dict):
            return None
        if seg not in cur:
            return None
        cur = cur[seg]
    return cur


def _expected_flow(case: dict[str, Any], has_followups: bool) -> tuple[bool, bool, bool]:
    completeness = str(case.get("completeness", "")).strip().lower()
    flow = case.get("expected_flow", {}) if isinstance(case.get("expected_flow", {}), dict) else {}

    if "initial_complete" in flow:
        initial_complete = bool(flow["initial_complete"])
    else:
        initial_complete = completeness == "full"

    if "final_complete" in flow:
        final_complete = bool(flow["final_complete"])
    else:
        if completeness == "full":
            final_complete = True
        else:
            final_complete = has_followups

    if "require_missing_reduction" in flow:
        require_missing_reduction = bool(flow["require_missing_reduction"])
    else:
        require_missing_reduction = has_followups and completeness == "missing"

    return initial_complete, final_complete, require_missing_reduction


def _build_turn_payload(session_id: str, text: str, min_confidence: float) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "text": text,
        "llm_router": True,
        "llm_question": True,
        "normalize_input": True,
        "autofix": True,
        "strict_mode": True,
        "min_confidence": min_confidence,
    }


def _evaluate_case(case: dict[str, Any], turn_outputs: list[dict[str, Any]]) -> tuple[bool, list[str], bool, bool, bool]:
    fail_reasons: list[str] = []
    has_followups = len(turn_outputs) > 1
    expected_initial_complete, expected_final_complete, require_missing_reduction = _expected_flow(case, has_followups)

    first = turn_outputs[0]
    final = turn_outputs[-1]
    actual_initial_complete = bool(first.get("is_complete", False))
    actual_final_complete = bool(final.get("is_complete", False))

    if actual_initial_complete != expected_initial_complete:
        fail_reasons.append("initial_complete_mismatch")
    if actual_final_complete != expected_final_complete:
        fail_reasons.append("final_complete_mismatch")

    first_missing = list(first.get("missing_fields", []))
    final_missing = list(final.get("missing_fields", []))
    if require_missing_reduction and len(final_missing) >= len(first_missing):
        fail_reasons.append("missing_not_reduced_after_followups")

    if bool(final.get("pending_overwrite_required", False)):
        fail_reasons.append("pending_overwrite_not_confirmed")

    expected_final = case.get("expected_final", {})
    if isinstance(expected_final, dict):
        cfg = final.get("config", {})
        for path, expected in expected_final.items():
            actual = _deep_get(cfg, str(path))
            if actual != expected:
                fail_reasons.append(f"expected_final_mismatch:{path}")

    for out in turn_outputs:
        if out.get("error"):
            fail_reasons.append("runtime_error")
            break

    return (
        len(fail_reasons) == 0,
        fail_reasons,
        expected_initial_complete,
        expected_final_complete,
        bool(expected_final) and not any(x.startswith("expected_final_mismatch:") for x in fail_reasons),
    )


def _run_case(case: dict[str, Any], *, config_path: str, min_confidence: float) -> CaseResult:
    case_id = str(case.get("id", "unknown"))
    session_id = f"casebank-{case_id}"
    reset_session(session_id)

    lang = str(case.get("lang", "en")).lower()
    initial_prompt = str(case.get("prompt", "")).strip()
    followups = [str(x).strip() for x in case.get("followup_turns", []) if str(x).strip()]
    turns_text = [initial_prompt, *followups]
    _, expected_final_complete, _ = _expected_flow(case, bool(followups))

    turn_outputs: list[dict[str, Any]] = []
    turn_results: list[TurnResult] = []
    for idx, text in enumerate(turns_text, start=1):
        out = process_turn(
            payload=_build_turn_payload(session_id, text, min_confidence),
            ollama_config_path=config_path,
            min_confidence=min_confidence,
            lang=lang,
        )
        turn_outputs.append(out)
        turn_results.append(
            TurnResult(
                turn=idx,
                user=text,
                assistant=str(out.get("assistant_message", "")),
                is_complete=bool(out.get("is_complete", False)),
                missing_fields=list(out.get("missing_fields", [])),
                dialogue_action=str(out.get("dialogue_action", "")),
                phase=str(out.get("phase", "")),
                llm_used=bool(out.get("llm_used", False)),
                fallback_reason=out.get("fallback_reason"),
                inference_backend=str(out.get("inference_backend", "")),
                accepted_update_count=int(out.get("internal_trace", {}).get("arbitration", {}).get("accepted_update_count", 0)),
                rejected_update_count=int(out.get("internal_trace", {}).get("arbitration", {}).get("rejected_update_count", 0)),
                pending_overwrite_required=bool(out.get("pending_overwrite_required", False)),
                internal_trace=dict(out.get("internal_trace", {})),
            )
        )

    auto_confirm_turns = 0
    while (
        expected_final_complete
        and turn_outputs
        and bool(turn_outputs[-1].get("pending_overwrite_required", False))
        and auto_confirm_turns < 2
    ):
        auto_confirm_turns += 1
        confirm_text = "确认" if lang == "zh" else "confirm"
        idx = len(turn_outputs) + 1
        out = process_turn(
            payload=_build_turn_payload(session_id, confirm_text, min_confidence),
            ollama_config_path=config_path,
            min_confidence=min_confidence,
            lang=lang,
        )
        turn_outputs.append(out)
        turn_results.append(
            TurnResult(
                turn=idx,
                user=confirm_text,
                assistant=str(out.get("assistant_message", "")),
                is_complete=bool(out.get("is_complete", False)),
                missing_fields=list(out.get("missing_fields", [])),
                dialogue_action=str(out.get("dialogue_action", "")),
                phase=str(out.get("phase", "")),
                llm_used=bool(out.get("llm_used", False)),
                fallback_reason=out.get("fallback_reason"),
                inference_backend=str(out.get("inference_backend", "")),
                accepted_update_count=int(out.get("internal_trace", {}).get("arbitration", {}).get("accepted_update_count", 0)),
                rejected_update_count=int(out.get("internal_trace", {}).get("arbitration", {}).get("rejected_update_count", 0)),
                pending_overwrite_required=bool(out.get("pending_overwrite_required", False)),
                internal_trace=dict(out.get("internal_trace", {})),
            )
        )

    final = turn_outputs[-1]
    pass_case, fail_reasons, expected_initial_complete, expected_final_complete, expected_paths_ok = _evaluate_case(
        case, turn_outputs
    )

    reset_session(session_id)
    return CaseResult(
        case_id=case_id,
        domain=str(case.get("domain", "")),
        style=str(case.get("style", "")),
        completeness=str(case.get("completeness", "")),
        lang=lang,
        pass_case=pass_case,
        fail_reasons=fail_reasons,
        expected_initial_complete=expected_initial_complete,
        actual_initial_complete=turn_results[0].is_complete,
        expected_final_complete=expected_final_complete,
        actual_final_complete=bool(final.get("is_complete", False)),
        initial_missing_count=len(turn_results[0].missing_fields),
        final_missing_count=len(list(final.get("missing_fields", []))),
        expected_paths_ok=expected_paths_ok,
        final_pending_overwrite_required=bool(final.get("pending_overwrite_required", False)),
        turns=turn_results,
        raw_dialogue=list(final.get("raw_dialogue", [])),
        config_snapshot=dict(final.get("config", {})),
    )


def _aggregate(results: list[CaseResult]) -> dict[str, Any]:
    internal_term_pattern = re.compile(
        r"\b[a-z]+(?:\.[a-z_]+)+\b|\b(single_[a-z_]+|module_[xyz]|child_[a-z0-9_]+|pitch_[xy]|tilt_[xy])\b",
        flags=re.IGNORECASE,
    )
    total = len(results)
    pass_count = sum(1 for r in results if r.pass_case)
    initial_alignment = sum(1 for r in results if r.expected_initial_complete == r.actual_initial_complete)
    final_alignment = sum(1 for r in results if r.expected_final_complete == r.actual_final_complete)
    llm_used_turns = sum(1 for r in results for t in r.turns if t.llm_used)
    total_turns = sum(len(r.turns) for r in results)
    internal_leak_turns = sum(1 for r in results for t in r.turns if internal_term_pattern.search(str(t.assistant)))
    repeated_assistant_cases = sum(
        1
        for r in results
        if any(
            a.get("content", "") == b.get("content", "")
            for a, b in zip(r.raw_dialogue, r.raw_dialogue[1:])
            if a.get("role") == "assistant" and b.get("role") == "assistant"
        )
    )
    stale_confirm_cases = sum(
        1
        for r in results
        if any(t.dialogue_action == "confirm_overwrite" and t.is_complete for t in r.turns)
    )
    reduction_applicable = [r for r in results if len(r.turns) > 1 and r.initial_missing_count > 0]
    reduction_success = sum(1 for r in reduction_applicable if r.final_missing_count < r.initial_missing_count)
    confirm_cases = [r for r in results if any(t.dialogue_action == "confirm_overwrite" for t in r.turns)]
    confirm_success = sum(1 for r in confirm_cases if not r.final_pending_overwrite_required)
    confirm_turns = [
        t
        for r in results
        for t in r.turns
        if str(t.user).strip().lower() in {"confirm", "\u786e\u8ba4"}
    ]
    confirm_rollback = sum(1 for t in confirm_turns if t.accepted_update_count == 0 and t.rejected_update_count > 0)
    return {
        "total_cases": total,
        "pass_count": pass_count,
        "fail_count": total - pass_count,
        "pass_rate": (pass_count / total) if total else 0.0,
        "initial_alignment_rate": (initial_alignment / total) if total else 0.0,
        "final_alignment_rate": (final_alignment / total) if total else 0.0,
        "llm_used_rate": (llm_used_turns / total_turns) if total_turns else 0.0,
        "total_turns": total_turns,
        "avg_turns_per_case": (total_turns / total) if total else 0.0,
        "missing_reduction_rate": (reduction_success / len(reduction_applicable)) if reduction_applicable else 0.0,
        "confirm_apply_success_rate": (confirm_success / len(confirm_cases)) if confirm_cases else 1.0,
        "rollback_after_confirm_rate": (confirm_rollback / len(confirm_turns)) if confirm_turns else 0.0,
        "internal_leak_turn_count": internal_leak_turns,
        "internal_leak_turn_rate": (internal_leak_turns / total_turns) if total_turns else 0.0,
        "repeated_assistant_case_count": repeated_assistant_cases,
        "repeated_assistant_case_rate": (repeated_assistant_cases / total) if total else 0.0,
        "stale_confirm_case_count": stale_confirm_cases,
        "stale_confirm_case_rate": (stale_confirm_cases / total) if total else 0.0,
    }


def _build_baseline_diff(summary: dict[str, Any], results: list[CaseResult], baseline: dict[str, Any] | None) -> dict[str, Any]:
    if not baseline:
        return {
            "has_baseline": False,
            "message": "baseline_not_found",
            "delta_pass_rate": None,
            "regressions": [],
            "improvements": [],
        }

    baseline_summary = dict(baseline.get("summary", {}))
    baseline_case_map = {str(item.get("case_id")): bool(item.get("pass_case", False)) for item in baseline.get("results", [])}
    current_case_map = {r.case_id: r.pass_case for r in results}

    regressions: list[str] = []
    improvements: list[str] = []
    for cid, current_pass in current_case_map.items():
        prev = baseline_case_map.get(cid)
        if prev is None:
            continue
        if prev and not current_pass:
            regressions.append(cid)
        if (not prev) and current_pass:
            improvements.append(cid)

    return {
        "has_baseline": True,
        "baseline_generated_at": baseline.get("generated_at"),
        "delta_pass_rate": summary["pass_rate"] - float(baseline_summary.get("pass_rate", 0.0)),
        "regressions": sorted(regressions),
        "improvements": sorted(improvements),
    }


def _to_json_payload(run_meta: dict[str, Any], summary: dict[str, Any], baseline_diff: dict[str, Any], results: list[CaseResult]) -> dict[str, Any]:
    return {
        "run_meta": run_meta,
        "summary": summary,
        "baseline_diff": baseline_diff,
        "results": [
            {
                "case_id": r.case_id,
                "domain": r.domain,
                "style": r.style,
                "completeness": r.completeness,
                "lang": r.lang,
                "pass_case": r.pass_case,
                "fail_reasons": r.fail_reasons,
                "expected_initial_complete": r.expected_initial_complete,
                "actual_initial_complete": r.actual_initial_complete,
                "expected_final_complete": r.expected_final_complete,
                "actual_final_complete": r.actual_final_complete,
                "initial_missing_count": r.initial_missing_count,
                "final_missing_count": r.final_missing_count,
                "expected_paths_ok": r.expected_paths_ok,
                "turns": [
                    {
                        "turn": t.turn,
                        "user": t.user,
                        "assistant": t.assistant,
                        "is_complete": t.is_complete,
                        "missing_fields": t.missing_fields,
                        "dialogue_action": t.dialogue_action,
                        "phase": t.phase,
                        "llm_used": t.llm_used,
                        "fallback_reason": t.fallback_reason,
                        "inference_backend": t.inference_backend,
                        "accepted_update_count": t.accepted_update_count,
                        "rejected_update_count": t.rejected_update_count,
                        "pending_overwrite_required": t.pending_overwrite_required,
                        "internal_trace": t.internal_trace,
                    }
                    for t in r.turns
                ],
                "final_pending_overwrite_required": r.final_pending_overwrite_required,
                "raw_dialogue": r.raw_dialogue,
                "config_snapshot": r.config_snapshot,
            }
            for r in results
        ],
    }


def _render_turn_narrative_en(turn: TurnResult) -> list[str]:
    lines = [
        f"Turn {turn.turn}: action={turn.dialogue_action}, phase={turn.phase}, complete={turn.is_complete}.",
        f"Missing fields: {', '.join(turn.missing_fields) if turn.missing_fields else 'none'}.",
        f"LLM used={turn.llm_used}; fallback={turn.fallback_reason or 'none'}; backend={turn.inference_backend}.",
    ]
    return lines


def _render_turn_narrative_zh(turn: TurnResult) -> list[str]:
    lines = [
        f"第 {turn.turn} 轮：动作={turn.dialogue_action}，阶段={turn.phase}，闭环状态={turn.is_complete}。",
        f"缺失字段：{('、'.join(turn.missing_fields)) if turn.missing_fields else '无'}。",
        f"LLM 使用={turn.llm_used}；回退={turn.fallback_reason or '无'}；后端={turn.inference_backend}。",
    ]
    return lines


def _render_table_rows(results: list[CaseResult], *, lang: str) -> list[str]:
    rows: list[str] = []
    for r in results:
        reason = ", ".join(r.fail_reasons) if r.fail_reasons else "-"
        rows.append(
            " & ".join(
                [
                    _latex_escape(r.case_id),
                    _latex_escape(r.domain),
                    _latex_escape(r.style),
                    _latex_escape(r.completeness),
                    _bool_label(r.expected_initial_complete, lang),
                    _bool_label(r.actual_initial_complete, lang),
                    _bool_label(r.expected_final_complete, lang),
                    _bool_label(r.actual_final_complete, lang),
                    f"{r.initial_missing_count}->{r.final_missing_count}",
                    _bool_label(r.pass_case, lang),
                    _latex_escape(reason),
                ]
            )
            + r" \\"
        )
    return rows


def _build_tex_en(run_meta: dict[str, Any], summary: dict[str, Any], baseline_diff: dict[str, Any], results: list[CaseResult]) -> str:
    lines: list[str] = []
    lines.append(r"\documentclass[11pt]{ctexart}")
    lines.append(r"\usepackage[a4paper,margin=1in]{geometry}")
    lines.append(r"\usepackage{longtable,booktabs}")
    lines.append(r"\title{Geant4-Agent Casebank Regression Report (EN)}")
    lines.append(r"\author{Automated Pipeline}")
    lines.append(rf"\date{{{_latex_escape(run_meta['timestamp'])}}}")
    lines.append(r"\begin{document}")
    lines.append(r"\maketitle")
    lines.append(r"\section{Unified Pass/Fail Table}")
    lines.append(r"\begin{longtable}{p{0.06\linewidth}p{0.08\linewidth}p{0.07\linewidth}p{0.08\linewidth}p{0.07\linewidth}p{0.07\linewidth}p{0.07\linewidth}p{0.07\linewidth}p{0.09\linewidth}p{0.06\linewidth}p{0.21\linewidth}}")
    lines.append(r"\toprule")
    lines.append(r"ID & Domain & Style & Completeness & ExpInit & ActInit & ExpFinal & ActFinal & Missing(I->F) & Result & Fail Reason \\")
    lines.append(r"\midrule")
    lines.extend(_render_table_rows(results, lang="en"))
    lines.append(r"\bottomrule")
    lines.append(r"\end{longtable}")
    lines.append(r"\section{Baseline Comparison}")
    lines.append(r"\begin{itemize}")
    lines.append(rf"\item pass\_rate={summary['pass_rate']:.3f}")
    lines.append(rf"\item initial\_alignment\_rate={summary['initial_alignment_rate']:.3f}")
    lines.append(rf"\item final\_alignment\_rate={summary['final_alignment_rate']:.3f}")
    lines.append(rf"\item avg\_turns\_per\_case={summary.get('avg_turns_per_case', 0.0):.3f}")
    lines.append(rf"\item missing\_reduction\_rate={summary.get('missing_reduction_rate', 0.0):.3f}")
    lines.append(rf"\item confirm\_apply\_success\_rate={summary.get('confirm_apply_success_rate', 0.0):.3f}")
    lines.append(rf"\item rollback\_after\_confirm\_rate={summary.get('rollback_after_confirm_rate', 0.0):.3f}")
    lines.append(rf"\item internal\_leak\_turn\_rate={summary.get('internal_leak_turn_rate', 0.0):.3f}")
    lines.append(rf"\item repeated\_assistant\_case\_rate={summary.get('repeated_assistant_case_rate', 0.0):.3f}")
    lines.append(rf"\item stale\_confirm\_case\_rate={summary.get('stale_confirm_case_rate', 0.0):.3f}")
    if baseline_diff.get("has_baseline"):
        lines.append(rf"\item delta\_pass\_rate={float(baseline_diff.get('delta_pass_rate') or 0.0):+.3f}")
        lines.append(
            rf"\item regressions={_latex_escape(', '.join(baseline_diff.get('regressions', [])) or 'none')}"
        )
        lines.append(
            rf"\item improvements={_latex_escape(', '.join(baseline_diff.get('improvements', [])) or 'none')}"
        )
    else:
        lines.append(r"\item baseline not found")
    lines.append(r"\end{itemize}")
    lines.append(r"\appendix")
    lines.append(r"\section{Appendix: Full Dialogues and Naturalized Internal Chains}")
    for r in results:
        lines.append(rf"\subsection{{Case {_latex_escape(r.case_id)} ({_latex_escape(r.domain)})}}")
        lines.append(r"\textbf{Dialogue:}")
        lines.append(r"\begin{itemize}")
        for item in r.raw_dialogue:
            role = str(item.get("role", "")).strip().lower()
            text = _latex_escape(str(item.get("content", "")))
            label = "User" if role == "user" else "Assistant"
            lines.append(rf"\item {label}: {text}")
        lines.append(r"\end{itemize}")
        lines.append(r"\textbf{Internal Chain (Natural Language):}")
        lines.append(r"\begin{itemize}")
        for t in r.turns:
            for line in _render_turn_narrative_en(t):
                lines.append(rf"\item {_latex_escape(line)}")
        lines.append(r"\end{itemize}")
    lines.append(r"\end{document}")
    return "\n".join(lines)


def _build_tex_zh(run_meta: dict[str, Any], summary: dict[str, Any], baseline_diff: dict[str, Any], results: list[CaseResult]) -> str:
    lines: list[str] = []
    lines.append(r"\documentclass[11pt]{ctexart}")
    lines.append(r"\usepackage[a4paper,margin=1in]{geometry}")
    lines.append(r"\usepackage{longtable,booktabs}")
    lines.append(r"\title{Geant4-Agent 回归测试报告（中文）}")
    lines.append(r"\author{自动化评测流程}")
    lines.append(rf"\date{{{_latex_escape(run_meta['timestamp'])}}}")
    lines.append(r"\begin{document}")
    lines.append(r"\maketitle")
    lines.append(r"\section{统一 Pass/Fail 总表}")
    lines.append(r"\begin{longtable}{p{0.06\linewidth}p{0.08\linewidth}p{0.07\linewidth}p{0.08\linewidth}p{0.07\linewidth}p{0.07\linewidth}p{0.07\linewidth}p{0.07\linewidth}p{0.09\linewidth}p{0.06\linewidth}p{0.21\linewidth}}")
    lines.append(r"\toprule")
    lines.append(r"ID & 领域 & 风格 & 参数完整性 & 期望初始 & 实际初始 & 期望最终 & 实际最终 & 缺参(初->终) & 结果 & 失败原因 \\")
    lines.append(r"\midrule")
    lines.extend(_render_table_rows(results, lang="zh"))
    lines.append(r"\bottomrule")
    lines.append(r"\end{longtable}")
    lines.append(r"\section{基准对比}")
    lines.append(r"\begin{itemize}")
    lines.append(rf"\item pass\_rate={summary['pass_rate']:.3f}")
    lines.append(rf"\item initial\_alignment\_rate={summary['initial_alignment_rate']:.3f}")
    lines.append(rf"\item final\_alignment\_rate={summary['final_alignment_rate']:.3f}")
    lines.append(rf"\item avg\_turns\_per\_case={summary.get('avg_turns_per_case', 0.0):.3f}")
    lines.append(rf"\item missing\_reduction\_rate={summary.get('missing_reduction_rate', 0.0):.3f}")
    lines.append(rf"\item confirm\_apply\_success\_rate={summary.get('confirm_apply_success_rate', 0.0):.3f}")
    lines.append(rf"\item rollback\_after\_confirm\_rate={summary.get('rollback_after_confirm_rate', 0.0):.3f}")
    lines.append(rf"\item internal\_leak\_turn\_rate={summary.get('internal_leak_turn_rate', 0.0):.3f}")
    lines.append(rf"\item repeated\_assistant\_case\_rate={summary.get('repeated_assistant_case_rate', 0.0):.3f}")
    lines.append(rf"\item stale\_confirm\_case\_rate={summary.get('stale_confirm_case_rate', 0.0):.3f}")
    if baseline_diff.get("has_baseline"):
        lines.append(rf"\item delta\_pass\_rate={float(baseline_diff.get('delta_pass_rate') or 0.0):+.3f}")
        lines.append(
            rf"\item regressions={_latex_escape('、'.join(baseline_diff.get('regressions', [])) or '无')}"
        )
        lines.append(
            rf"\item improvements={_latex_escape('、'.join(baseline_diff.get('improvements', [])) or '无')}"
        )
    else:
        lines.append(r"\item 未发现历史基准")
    lines.append(r"\end{itemize}")
    lines.append(r"\appendix")
    lines.append(r"\section{附录：完整对话与内部处理链（自然语言）}")
    for r in results:
        lines.append(rf"\subsection{{案例 {_latex_escape(r.case_id)}（{_latex_escape(r.domain)}）}}")
        lines.append(r"\textbf{对话：}")
        lines.append(r"\begin{itemize}")
        for item in r.raw_dialogue:
            role = str(item.get("role", "")).strip().lower()
            text = _latex_escape(str(item.get("content", "")))
            label = "用户" if role == "user" else "系统"
            lines.append(rf"\item {label}：{text}")
        lines.append(r"\end{itemize}")
        lines.append(r"\textbf{内部链路（自然语言）：}")
        lines.append(r"\begin{itemize}")
        for t in r.turns:
            for line in _render_turn_narrative_zh(t):
                lines.append(rf"\item {_latex_escape(line)}")
        lines.append(r"\end{itemize}")
    lines.append(r"\end{document}")
    return "\n".join(lines)


def _compile_tex_xelatex(tex_path: Path) -> tuple[bool, str]:
    cmd = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    try:
        for _ in range(2):
            proc = subprocess.run(
                cmd,
                cwd=str(tex_path.parent),
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
            )
            if proc.returncode != 0:
                return False, (proc.stdout + "\n" + proc.stderr)[-4000:]
    except FileNotFoundError:
        return False, "xelatex_not_found"
    return True, "ok"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run casebank regression and emit EN/ZH LaTeX+PDF reports.")
    parser.add_argument("--dataset", default="docs/eval_casebank_v1_20.json")
    parser.add_argument("--config", required=True, help="LLM config path")
    parser.add_argument("--outdir", default="docs")
    parser.add_argument("--baseline", default="docs/casebank_baseline.json")
    parser.add_argument("--min_confidence", type=float, default=0.6)
    parser.add_argument("--set_baseline", action="store_true")
    parser.add_argument("--max_cases", type=int, default=0)
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    baseline_path = Path(args.baseline)

    dataset = _load_json(dataset_path)
    cases = list(dataset.get("cases", []))
    if args.max_cases > 0:
        cases = cases[: args.max_cases]

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_meta = {
        "timestamp": ts,
        "dataset": str(dataset_path).replace("\\", "/"),
        "config": str(args.config).replace("\\", "/"),
        "min_confidence": args.min_confidence,
        "total_cases": len(cases),
    }

    results = [_run_case(case, config_path=args.config, min_confidence=args.min_confidence) for case in cases]
    summary = _aggregate(results)

    baseline = _load_json(baseline_path) if baseline_path.exists() else None
    baseline_diff = _build_baseline_diff(summary, results, baseline)

    payload = _to_json_payload(run_meta, summary, baseline_diff, results)
    json_out = outdir / f"casebank_regression_{ts}.json"
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    tex_en = outdir / f"casebank_regression_report_en_{ts}.tex"
    tex_zh = outdir / f"casebank_regression_report_zh_{ts}.tex"
    tex_en.write_text(_build_tex_en(run_meta, summary, baseline_diff, results), encoding="utf-8")
    tex_zh.write_text(_build_tex_zh(run_meta, summary, baseline_diff, results), encoding="utf-8")

    ok_en, msg_en = _compile_tex_xelatex(tex_en)
    ok_zh, msg_zh = _compile_tex_xelatex(tex_zh)

    if args.set_baseline:
        baseline_payload = {
            "generated_at": ts,
            "summary": summary,
            "results": [{"case_id": r.case_id, "pass_case": r.pass_case} for r in results],
        }
        baseline_path.write_text(json.dumps(baseline_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "json_report": str(json_out).replace("\\", "/"),
                "tex_en": str(tex_en).replace("\\", "/"),
                "pdf_en": str(tex_en.with_suffix('.pdf')).replace("\\", "/"),
                "tex_zh": str(tex_zh).replace("\\", "/"),
                "pdf_zh": str(tex_zh.with_suffix('.pdf')).replace("\\", "/"),
                "compile_en_ok": ok_en,
                "compile_zh_ok": ok_zh,
                "compile_en_msg": msg_en if not ok_en else "ok",
                "compile_zh_msg": msg_zh if not ok_zh else "ok",
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
