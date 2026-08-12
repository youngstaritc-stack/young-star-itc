from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.mt5_bridge import process_incoming_mt5_data
from ai_engine.master_engine import CoreBrain

app = FastAPI(title="Young Star ITC - MT5 Pro Engine")
brain = CoreBrain()

class MT5Data(BaseModel):
    symbol: str
    price: float
    timeframe: str

@app.get("/")
def read_root():
    return {"status": "Forex Engine Active", "mode": "MT5 Ready"}

@app.post("/api/mt5-data")
def receive_data(data: MT5Data):
    result = process_incoming_mt5_data(data.dict())
    return {"message": "Data received", "engine_output": brain.run_analysis(data)}
