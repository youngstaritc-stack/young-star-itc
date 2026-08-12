import sys
import os
import asyncio
import json
import websockets
import pandas as pd
from sqlite3 import connect
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.indicators import TechnicalAnalysis
from database.models import init_db

app = FastAPI(title="Young Star ITC Binance Live Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# Global candle price memory for BTC/USDT
btc_prices = []

def save_signal_to_db(data: dict):
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
    return {"status": "Active", "message": "Binance Live Stream Engine Running"}

@app.websocket("/ws/signals")
async def websocket_signals(websocket: WebSocket):
    await websocket.accept()
    
    # Connect directly to Binance Public WebSocket Stream for BTC/USDT 1m kline
    binance_ws_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
    
    try:
        async with websockets.connect(binance_ws_url) as b_ws:
            while True:
                response = await b_ws.recv()
                data = json.loads(response)
                kline = data.get('k', {})
                close_price = float(kline.get('c', 0))

                if close_price > 0:
                    btc_prices.append(close_price)
                    if len(btc_prices) > 100:
                        btc_prices.pop(0)

                    # Minimum 50 price points required for EMA50 calculation
                    if len(btc_prices) >= 50:
                        df = pd.DataFrame({"close": btc_prices})
                        analysis_result = TechnicalAnalysis.generate_signal(df)
                        save_signal_to_db(analysis_result)

                        await websocket.send_json({
                            "type": "SIGNAL_UPDATE",
                            "symbol": "BTCUSDT",
                            "data": analysis_result
                        })
                    else:
                        await websocket.send_json({
                            "type": "BUFFERING",
                            "message": f"Collecting market data... ({len(btc_prices)}/50)"
                        })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Binance Stream Error: {e}")
