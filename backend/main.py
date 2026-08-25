from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from ai_engine import AnalysisPipeline, CandleData

app = FastAPI(title="Young Star ITC — Rule Book Analysis Engine")
pipeline = AnalysisPipeline()


class CandleInput(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


class AnalysisRequest(BaseModel):
    candles: List[CandleInput]
    timeframe: str
    current_index: Optional[int] = None


@app.get("/")
def read_root():
    return {"status": "active", "engine": "rule_book_analysis", "parts": "1-7"}


@app.post("/api/analyze")
def analyze(request: AnalysisRequest):
    candles = [CandleData(**c.model_dump()) for c in request.candles]
    return pipeline.analyze(candles, request.timeframe, request.current_index)
