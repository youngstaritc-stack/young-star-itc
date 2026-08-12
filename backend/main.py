from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            body { background-color: #0b0e14; color: #fff; font-family: sans-serif; margin: 0; padding: 20px; }
            .card { background: #131b26; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #1e293b; }
            input { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #1e293b; background: #1e293b; color: #fff; box-sizing: border-box; }
            button { width: 100%; padding: 12px; border-radius: 8px; border: none; background: #0284c7; color: #fff; font-weight: bold; cursor: pointer; margin-top: 10px; }
            .badge { background: #1e293b; padding: 4px 8px; border-radius: 6px; font-size: 12px; color: #38bdf8; }
        </style>
    </head>
    <body>
        <div id="login-view" class="card">
            <h2 style="color: #38bdf8; margin-top:0;">Young Star ITC Login</h2>
            <input type="email" id="email" placeholder="Email" value="admin@youngstar.itc">
            <input type="password" id="password" placeholder="Password" value="123456">
            <button onclick="login()">Login to Dashboard</button>
        </div>

        <div id="chart-view" class="card" style="display:none;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="color:#38bdf8; margin:0;">XAU/USD Live Chart</h3>
                <span class="badge">WebSocket Connected</span>
            </div>
            <h1 id="price" style="color:#34d399; font-size: 36px; margin: 15px 0;">$0.00</h1>
            <p id="volume" style="color:#cbd5e1; margin:0;">Volume: 0</p>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #1e293b;">
                <span style="color:#94a3b8;">AI Signal: </span>
                <strong id="signal" style="color:#38bdf8;">WAITing...</strong>
            </div>
        </div>

        <script>
            function login() {
                document.getElementById('login-view').style.display = 'none';
                document.getElementById('chart-view').style.display = 'block';
                connectWS();
            }

            function connectWS() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const ws = new WebSocket(`${protocol}//${window.location.host}/ws/stream`);
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if(data.price) document.getElementById('price').innerText = `$${data.price.toFixed(2)}`;
                    if(data.volume) document.getElementById('volume').innerText = `Volume: ${data.volume}`;
                    if(data.ai_signal) document.getElementById('signal').innerText = data.ai_signal;
                };
            }
        </script>
    </body>
    </html>
    """

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    import asyncio, random
    price = 2350.00
    while True:
        price += random.uniform(-0.5, 0.5)
        await websocket.send_json({
            "symbol": "XAU/USD",
            "price": price,
            "volume": random.randint(100, 500),
            "ai_signal": random.choice(["BUY CONFIRMED", "SELL CONFIRMED", "WAIT"])
        })
        await asyncio.sleep(1)
