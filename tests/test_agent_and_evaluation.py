import json
from pathlib import Path

from app.agent import ToolFirstAgent
from app.evaluator import evaluate_questions
from app.tools import EnergyAnalysisTools


SAMPLE_ROWS = [
    {"timestamp": "2024-07-01T08:00:00", "building_id": "B-01", "energy_kwh": 42.0, "temperature_c": 28.0, "hvac_energy_kwh": 16.0, "supply_temp_c": 8.0, "return_temp_c": 12.0},
    {"timestamp": "2024-07-01T09:00:00", "building_id": "B-01", "energy_kwh": 44.0, "temperature_c": 29.0, "hvac_energy_kwh": 17.0, "supply_temp_c": 8.0, "return_temp_c": 12.5},
    {"timestamp": "2024-07-01T10:00:00", "building_id": "B-01", "energy_kwh": 43.0, "temperature_c": 30.0, "hvac_energy_kwh": 17.0, "supply_temp_c": 8.0, "return_temp_c": 12.5},
    {"timestamp": "2024-07-02T08:00:00", "building_id": "B-01", "energy_kwh": 45.0, "temperature_c": 29.0, "hvac_energy_kwh": 18.0, "supply_temp_c": 8.0, "return_temp_c": 12.0},
    {"timestamp": "2024-07-02T09:00:00", "building_id": "B-01", "energy_kwh": 46.0, "temperature_c": 30.0, "hvac_energy_kwh": 18.0, "supply_temp_c": 8.0, "return_temp_c": 12.0},
    {"timestamp": "2024-07-02T10:00:00", "building_id": "B-01", "energy_kwh": 80.0, "temperature_c": 31.0, "hvac_energy_kwh": 28.0, "supply_temp_c": 8.0, "return_temp_c": 13.0},
]


def test_agent_calls_expected_tool_and_returns_evidence():
    agent = ToolFirstAgent(EnergyAnalysisTools(SAMPLE_ROWS))

    for question, expected_tool in [
        ("查看 B-01 的能耗趋势", "energy_trend"),
        ("定位 B-01 的能耗异常", "locate_anomalies"),
        ("分析天气和能耗关联", "weather_energy_correlation"),
    ]:
        answer = agent.ask(question, building_id="B-01")
        assert answer.tool_calls[0].tool_name == expected_tool
        assert answer.evidence
        assert answer.answer


def test_evaluation_set_has_twenty_questions_with_real_tool_expectations():
    dataset = Path("evaluation/questions_v1.jsonl")
    rows = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines() if line]

    assert len(rows) == 20
    assert {row["expected_tool"] for row in rows} == {
        "energy_trend", "locate_anomalies", "weather_energy_correlation"
    }


def test_evaluation_executes_all_questions_with_tool_calls_and_evidence():
    results = evaluate_questions(
        ToolFirstAgent(EnergyAnalysisTools(SAMPLE_ROWS)),
        Path("evaluation/questions_v1.jsonl"),
    )

    assert len(results) == 20
    assert all(result["tool_called"] for result in results)
    assert all(result["has_evidence"] for result in results)
    assert all(result["failure_reason"] is None for result in results)
