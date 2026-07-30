from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

from app.agent import ToolFirstAgent
from app.models import AskRequest, AskResponse
from app.repository import PostgresEnergyRepository
from app.tools import EnergyAnalysisTools


def create_app(database_url: str | None = None) -> FastAPI:
    app = FastAPI(title="Building Energy AI MVP", version="0.1.0")
    configured_database_url = database_url or os.getenv("DATABASE_URL")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "database_configured": bool(configured_database_url)}

    @app.post("/v1/ask", response_model=AskResponse)
    def ask(request: AskRequest) -> AskResponse:
        if not configured_database_url:
            raise HTTPException(status_code=503, detail="DATABASE_URL is not configured")
        try:
            tools = EnergyAnalysisTools(PostgresEnergyRepository(configured_database_url).load_rows())
            return ToolFirstAgent(tools).ask(request.question, request.building_id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    return app


app = create_app()

