from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="YOUNG STAR ITC Engine", version="1.0.0")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "YOUNG STAR ITC",
        "engine": "Young Star Volume Engine",
        "message": "Backend is running smoothly"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# Dedicated Chart Data Contract Endpoint
@app.get("/api/chart/data")
def get_chart_data(
    symbol: str = Query("Gold", description="Market symbol: Gold, Silver, AUD/USD"),
    timeframe: str = Query("15M", description="Timeframe: 1D, 4H, 2H, 1H, 45M, 30M, 15M, 5M, 1M")
):
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "engine": "Young Star Volume Engine",
        "candles": [
            {"timestamp": "2026-08-12T10:00:00Z", "open": 2400.0, "high": 2405.5, "low": 2398.2, "close": 2403.1, "volume": 1250},
            {"timestamp": "2026-08-12T10:15:00Z", "open": 2403.1, "high": 2410.0, "low": 2401.0, "close": 2408.4, "volume": 1820}
        ]
    }

# Analysis Data Contract Endpoint (Section 20)
@app.get("/api/analysis/state")
def get_analysis_state(
    symbol: str = Query("Gold"),
    timeframe: str = Query("15M")
):
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "timestamp": "2026-08-12T10:15:00Z",
        "trend_state": {"status": "COMPLETED", "code": "TR-003", "reason": "100% Trend Confirmation"},
        "fib_state": {"status": "IN_DEVELOPMENT", "code": "FIB-004", "reason": "Priority zone 38/50/61 pullback retest"},
        "ob_state": {"status": "DEFINED", "code": "OB-001", "reason": "High quality OB detected"},
        "pc_state": {"status": "IN_DEVELOPMENT", "code": "PC-001", "reason": "Candle Open-to-Close PC zone active"},
        "volume_state": {"status": "ACTIVE", "reason": "High volume confirmation"},
        "liquidity_state": {"status": "WARNING", "reason": "LQ Ahead notification"},
        "fvg_state": {"status": "WARNING", "reason": "FVG Ahead notification"},
        "historical_match": {"score": 94, "evidence": "Live/historical pattern match card"},
        "signal_state": "READY", # Options: INFORMATION, READY, CONFIRMED, ENTERED, MANAGING, CLOSED
        "ai_boundary": "BEFORE_ENTRY_INFORMATIONAL_ONLY"
    }
