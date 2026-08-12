import sys
import os
import asyncio
import pandas as pd
from sqlite3 import connect
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path to import ai_engine and database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.indicators import TechnicalAnalysis
from database.models import init_db

app = FastAPI(title="Young Star ITC Trade Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on start
init_db()

def save_signal_to_db(data: dict):
    """Helper function to save signals into SQLite database"""
    conn = connect('trade_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO signals (price, rsi, ema_20, ema_50, signal, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['price'], data['rsi'], data['ema_20'], data['ema_50'], data['signal'], data['reason']))
    conn.commit()
    conn.close()

@app.get("/")
def read_root():
    return {"status": "Active", "message": "Young Star ITC Trading Backend Running"}

@app.get("/api/signals/history")
def get_signal_history(limit: int = 20):
    """REST API endpoint to fetch recent signals history from database"""
    conn = connect('trade_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, price, rsi, ema_20, ema_50, signal, reason 
        FROM signals 
        ORDER BY id DESC 
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "timestamp": row[0],
            "price": row[1],
            "rsi": row[2],
            "ema_20": row[3],
            "ema_50": row[4],
            "signal": row[5],
            "reason": row[6]
        })
    return {"status": "success", "data": history}

@app.websocket("/ws/signals")
async def websocket_signals(websocket: WebSocket):
    await websocket.accept()
    
    base_price = 100.0
    prices = [base_price + (i * 0.2 if i % 2 == 0 else -i * 0.1) for i in range(60)]
    
    try:
        while True:
            import random
            price_change = random.uniform(-0.8, 1.0)
            prices.append(prices[-1] + price_change)
            
            df = pd.DataFrame({"close": prices})
            analysis_result = TechnicalAnalysis.generate_signal(df)
            
            # Save generated signal to database
            save_signal_to_db(analysis_result)
            
            # Broadcast signal via websocket
            await websocket.send_json({
                "type": "SIGNAL_UPDATE",
                "data": analysis_result
            })
            
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        print("Client disconnected from websocket")
