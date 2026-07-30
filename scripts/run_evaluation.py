import json
import os
import sys
from pathlib import Path

root = Path(__file__).parents[1]
sys.path.insert(0, str(root))

from app.agent import ToolFirstAgent
from app.evaluator import evaluate_questions
from app.repository import PostgresEnergyRepository
from app.tools import EnergyAnalysisTools


rows = PostgresEnergyRepository(os.environ["DATABASE_URL"]).load_rows()
results = evaluate_questions(ToolFirstAgent(EnergyAnalysisTools(rows)), root / "evaluation" / "questions_v1.jsonl")
print(json.dumps(results, ensure_ascii=False, indent=2))
if any(result["failure_reason"] for result in results):
    raise SystemExit(1)
