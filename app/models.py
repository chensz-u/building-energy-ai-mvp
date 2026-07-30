from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=300)
    building_id: str = Field(default="B-01", min_length=1, max_length=40)


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


class AskResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCall]
    evidence: list[dict[str, Any]]

