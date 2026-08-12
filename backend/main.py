import sys
import os
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
    return engine.analyze_volume_and_pattern(symbol, timeframe)

# Real-time WebSocket Stream Endpoint for Live Candles & Signals
@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            live_data = {
                "event": "TICK_UPDATE",
                "symbol": "Gold",
                "price": 2409.20,
                "volume": 1920,
                "status": "LIVE"
            }
            await websocket.send_text(json.dumps(live_data))
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        print("WebSocket Client Disconnected")
