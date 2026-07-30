from __future__ import annotations

from app.models import AskResponse, ToolCall
from app.tools import EnergyAnalysisTools


class ToolFirstAgent:
    """Routes a question to one analysis tool before producing a cited answer."""

    def __init__(self, tools: EnergyAnalysisTools):
        self.tools = tools

    def ask(self, question: str, building_id: str) -> AskResponse:
        tool_name = self._choose_tool(question)
        result = getattr(self.tools, tool_name)(building_id)
        evidence = [result["evidence"]]
        return AskResponse(
            answer=self._answer_for(tool_name, building_id, result),
            tool_calls=[ToolCall(tool_name=tool_name, arguments={"building_id": building_id}, result=result)],
            evidence=evidence,
        )

    @staticmethod
    def _choose_tool(question: str) -> str:
        if any(token in question for token in ("异常", "突增", "定位", "告警")):
            return "locate_anomalies"
        if any(token in question.lower() for token in ("天气", "温度", "关联", "相关", "关系")):
            return "weather_energy_correlation"
        return "energy_trend"

    @staticmethod
    def _answer_for(tool_name: str, building_id: str, result: dict) -> str:
        if tool_name == "locate_anomalies":
            return f"{building_id} 检出 {len(result['anomalies'])} 条超过统计阈值的读数；请结合工具证据复核。"
        if tool_name == "weather_energy_correlation":
            return f"{building_id} 的温度与能耗 Pearson 相关系数为 {result['pearson_correlation']}；样本范围见工具证据。"
        return f"{building_id} 已按日聚合 {len(result['points'])} 个能耗点；总量和样本数见工具证据。"
