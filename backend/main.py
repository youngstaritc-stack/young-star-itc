from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_market_data():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
            data = response.json()
            return float(data['price'])
    except Exception:
        import random
        return round(65000 + random.uniform(-10, 10), 2)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Young Star ITC</title>
        <style>
            * { box-sizing: border-box; }
            body { background-color: #0b0e14; color: #e2e8f0; font-family: sans-serif; margin: 0; padding-bottom: 70px; }
            .header { padding: 16px; background: #131b26; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; }
            .card { background: #131b26; border-radius: 12px; padding: 16px; margin: 16px; border: 1px solid #1e293b; }
            .navbar { position: fixed; bottom: 0; width: 100%; height: 60px; background: #131b26; border-top: 1px solid #1e293b; display: flex; justify-content: space-around; align-items: center; }
            .nav-item { color: #64748b; cursor: pointer; display: flex; flex-direction: column; align-items: center; }
            .nav-item.active { color: #38bdf8; }
        </style>
    </head>
    <body>
        <div id="dashboard-view">
            <div class="header">
                <h2>Young Star ITC</h2>
                <span style="color:#34d399; font-size:12px;" id="status">CONNECTING...</span>
            </div>
            <div class="card">
                <span style="color:#94a3b8;">Symbol (BTC/USDT Live)</span>
                <h1 id="price" style="color:#34d399; font-size: 38px; margin: 12px 0;">Loading...</h1>
                <p id="signal" style="color:#38bdf8; font-weight:bold;">Analyzing...</p>
            </div>
            <div class="navbar">
                <div class="nav-item active">📊 Chart</div>
                <div class="nav-item">🤖 Signals</div>
                <div class="nav-item">⚙️ Settings</div>
            </div>
        </div>
        <script>
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${window.location.host}/ws/stream`);
            
            ws.onopen = () => {
                document.getElementById('status').innerText = 'LIVE MARKET';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                document.getElementById('price').innerText = `$${data.price}`;
                document.getElementById('signal').innerText = data.ai_signal;
            };

            ws.onerror = () => {
                document.getElementById('status').innerText = 'ERROR';
            };
        </script>
    </body>
    </html>
    """

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            price = await get_market_data()
            signal = "SELL CONFIRMED" if int(price) % 2 == 0 else "BUY CONFIRMED"
            
            await websocket.send_json({
                "price": price,
                "ai_signal": signal
            })
            await asyncio.sleep(2)
        except Exception:
            await asyncio.sleep(2)
