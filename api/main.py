from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
import os
import json

from .log_service import save_log, get_logs
from .ai_service import get_ai_code, get_ai_insight, AIGenerateRequest
from .execution_service import execute_code_safely

app = FastAPI()

# Đường dẫn tới file csv hiện tại
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "vn_fuel_price_2018_present.csv"

class ExecuteRequest(BaseModel):
    code: str
    user_prompt: str
    ai_code: str

@app.post("/api/ai/generate")
async def generate_code(request: AIGenerateRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Chưa cài đặt biến môi trường API key.")
    try:
        result = get_ai_code(request, api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/insight")
async def generate_insight(request: AIGenerateRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Chưa cài đặt biến môi trường API key.")
    try:
        result = get_ai_insight(request, api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
async def execute_code(request: ExecuteRequest):
    try:
        df = pd.read_csv(DATA_PATH)
        df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
        
        result = execute_code_safely(request.code, df)
        
        # Save log
        save_log(
            user_prompt=request.user_prompt,
            ai_code=request.ai_code,
            final_code=request.code,
            status=result["status"],
            result=json.dumps(result.get("fig_json") or result.get("df_json") or result.get("error_msg", ""))[:1000] # Luu 1 phan ket qua de log bot nang
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def fetch_logs():
    return get_logs()
