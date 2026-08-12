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
            * { box-sizing: border-box; }
            body { 
                background-color: #0b0e14; 
                color: #e2e8f0; 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                margin: 0; 
                padding: 0; 
                padding-bottom: 70px;
            }
            .header {
                padding: 16px;
                background: #131b26;
                border-bottom: 1px solid #1e293b;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .header h2 { margin: 0; color: #38bdf8; font-size: 18px; }
            .container { padding: 16px; }
            .card { 
                background: #131b26; 
                border-radius: 12px; 
                padding: 16px; 
                margin-bottom: 16px; 
                border: 1px solid #1e293b; 
            }
            input { 
                width: 100%; 
                padding: 12px; 
                margin: 8px 0; 
                border-radius: 8px; 
                border: 1px solid #1e293b; 
                background: #0b0e14; 
                color: #fff; 
            }
            button { 
                width: 100%; 
                padding: 12px; 
                border-radius: 8px; 
                border: none; 
                background: #0284c7; 
                color: #fff; 
                font-weight: bold; 
                cursor: pointer; 
                margin-top: 10px; 
            }
            .badge { background: #1e293b; padding: 4px 10px; border-radius: 20px; font-size: 12px; color: #38bdf8; }
            
            /* Bottom Navigation Bar */
            .navbar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                height: 60px;
                background: #131b26;
                border-top: 1px solid #1e293b;
                display: flex;
                justify-content: space-around;
                align-items: center;
            }
            .nav-item {
                color: #64748b;
                text-decoration: none;
                font-size: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
            }
            .nav-item.active { color: #38bdf8; font-weight: bold; }
            .nav-icon { font-size: 18px; margin-bottom: 2px; }
        </style>
    </head>
    <body>

        <!-- Login Screen -->
        <div id="login-view" class="container" style="margin-top: 40px;">
            <div class="card">
                <h2 style="color: #38bdf8; margin-top:0; text-align:center;">Young Star ITC</h2>
                <p style="color: #94a3b8; font-size: 13px; text-align:center;">Sign in to access live trading signals</p>
                <input type="email" id="email" placeholder="Email" value="admin@youngstar.itc">
                <input type="password" id="password" placeholder="Password" value="123456">
                <button onclick="login()">Login to Dashboard</button>
            </div>
        </div>

        <!-- Main Dashboard View -->
        <div id="dashboard-view" style="display:none;">
            <div class="header">
                <h2>Young Star ITC</h2>
                <span class="badge" id="ws-status">Connecting...</span>
            </div>

            <div class="container">
                <!-- Tab: Chart -->
                <div id="tab-chart">
                    <div class="card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="color:#94a3b8;">Symbol</span>
                            <span style="font-weight:bold; color:#fff;">XAU/USD (Gold)</span>
                        </div>
                        <h1 id="price" style="color:#34d399; font-size: 38px; margin: 12px 0;">$0.00</h1>
                        <p id="volume" style="color:#cbd5e1; margin:0; font-size: 13px;">Volume: 0</p>
                    </div>

                    <div class="card" style="border-left: 4px solid #0284c7;">
                        <div style="color:#94a3b8; font-size: 12px;">AI Engine Analysis</div>
                        <h3 id="signal" style="color:#38bdf8; margin: 8px 0;">WAITING FOR SIGNAL...</h3>
                        <p style="color:#64748b; font-size: 11px; margin:0;">Updated real-time via WebSocket</p>
                    </div>
                </div>

                <!-- Tab: Signals -->
                <div id="tab-signals" style="display:none;">
                    <div class="card">
                        <h3>AI Signal History</h3>
                        <ul id="signal-list" style="padding-left:20px; color:#cbd5e1; font-size:13px; margin:0;">
                            <li>Live AI signals stream starts on login...</li>
                        </ul>
                    </div>
                </div>

                <!-- Tab: Settings -->
                <div id="tab-settings" style="display:none;">
                    <div class="card">
                        <h3>App Settings</h3>
                        <p style="color:#94a3b8; font-size:13px;">Account: admin@youngstar.itc</p>
                        <p style="color:#94a3b8; font-size:13px;">Theme: Figma Dark Modern</p>
                        <button onclick="logout()" style="background:#ef4444;">Logout</button>
                    </div>
                </div>
            </div>

            <!-- Bottom Navigation -->
            <div class="navbar">
                <div class="nav-item active" id="nav-chart" onclick="switchTab('chart')">
                    <span class="nav-icon">📊</span>
                    <span>Chart</span>
                </div>
                <div class="nav-item" id="nav-signals" onclick="switchTab('signals')">
                    <span class="nav-icon">🤖</span>
                    <span>AI Signals</span>
                </div>
                <div class="nav-item" id="nav-settings" onclick="switchTab('settings')">
                    <span class="nav-icon">⚙️</span>
                    <span>Settings</span>
                </div>
            </div>
        </div>

        <script>
            let ws;

            function login() {
                document.getElementById('login-view').style.display = 'none';
                document.getElementById('dashboard-view').style.display = 'block';
                connectWS();
            }

            function logout() {
                if (ws) ws.close();
                document.getElementById('dashboard-view').style.display = 'none';
                document.getElementById('login-view').style.display = 'block';
            }

            function switchTab(tabName) {
                ['chart', 'signals', 'settings'].forEach(t => {
                    document.getElementById('tab-' + t).style.display = (t === tabName) ? 'block' : 'none';
                    document.getElementById('nav-' + t).classList.toggle('active', t === tabName);
                });
            }

            function connectWS() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws/stream`);
                
                ws.onopen = () => {
                    document.getElementById('ws-status').innerText = 'LIVE';
                    document.getElementById('ws-status').style.color = '#34d399';
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if(data.price) document.getElementById('price').innerText = `$${data.price.toFixed(2)}`;
                    if(data.volume) document.getElementById('volume').innerText = `Volume: ${data.volume}`;
                    if(data.ai_signal) {
                        document.getElementById('signal').innerText = data.ai_signal;
                        
                        // Add to Signal History Tab
                        const list = document.getElementById('signal-list');
                        const li = document.createElement('li');
                        li.style.marginBottom = '6px';
                        li.innerText = `[${new Date().toLocaleTimeString()}] ${data.ai_signal} @ $${data.price.toFixed(2)}`;
                        list.prepend(li);
                        if (list.children.length > 10) list.removeChild(list.lastChild);
                    }
                };

                ws.onclose = () => {
                    document.getElementById('ws-status').innerText = 'Disconnected';
                    document.getElementById('ws-status').style.color = '#ef4444';
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
