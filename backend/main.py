import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_engine.volume_engine import VolumeEngine

app = FastAPI(title="Young Star ITC API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = VolumeEngine()

@app.get("/")
def read_root():
    return {"status": "ONLINE", "system": "YOUNG STAR ITC Core API"}

@app.get("/api/chart/data")
def get_chart_data(symbol: str = "Gold", timeframe: str = "15M"):
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": [
            {"time": "10:00", "open": 2400.0, "high": 2405.0, "low": 2398.0, "close": 2402.5, "volume": 1200},
            {"time": "10:15", "open": 2402.5, "high": 2410.0, "low": 2401.0, "close": 2408.4, "volume": 1850}
        ]
    }

@app.get("/api/analysis/state")
def get_analysis_state(symbol: str = "Gold", timeframe: str = "15M"):
    # Connect directly to AI Volume Engine Core
    analysis_result = engine.analyze_volume_and_pattern(symbol, timeframe)
    return analysis_result
