from __future__ import annotations

import json
from pathlib import Path

from app.agent import ToolFirstAgent


def evaluate_questions(agent: ToolFirstAgent, dataset_path: Path) -> list[dict[str, object]]:
    """Run the fixed question set and record tool/evidence checks without scoring model quality."""
    results: list[dict[str, object]] = []
    for line in dataset_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        case = json.loads(line)
        failure_reason = None
        tool_called = False
        has_evidence = False
        try:
            response = agent.ask(case["question"], building_id=case.get("building_id", "B-01"))
            tool_called = bool(response.tool_calls) and response.tool_calls[0].tool_name == case["expected_tool"]
            has_evidence = bool(response.evidence)
            if not tool_called:
                failure_reason = "unexpected_tool"
            elif not has_evidence:
                failure_reason = "missing_evidence"
        except Exception as error:  # Evaluation records execution failure instead of hiding it.
            failure_reason = f"execution_error:{type(error).__name__}"
        results.append({
            "id": case["id"],
            "expected_tool": case["expected_tool"],
            "tool_called": tool_called,
            "has_evidence": has_evidence,
            "failure_reason": failure_reason,
        })
    return results

