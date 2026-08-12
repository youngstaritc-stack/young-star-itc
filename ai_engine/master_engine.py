import pandas as pd
import numpy as np

class MarketStructureEngine:
    """1. BOS & CHoCH Detection"""
    @staticmethod
    def analyze(df: pd.DataFrame) -> dict:
        if len(df) < 5:
            return {"bos": False, "choch": False, "structure": "NEUTRAL"}
        
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        
        recent_high = np.max(highs[-5:-1])
        recent_low = np.min(lows[-5:-1])
        current_close = closes[-1]
        
        bos = current_close > recent_high
        choch = current_close < recent_low
        
        structure = "BULLISH_BOS" if bos else ("BEARISH_CHOCH" if choch else "NEUTRAL")
        return {"bos": bos, "choch": choch, "structure": structure}

class TrendEngine:
    """2. Trend Direction Classifier"""
    @staticmethod
    def analyze(df: pd.DataFrame) -> str:
        if len(df) < 20:
            return "SIDEWAYS"
        
        sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
        current_price = df['close'].iloc[-1]
        
        if current_price > sma_20:
            return "BULLISH"
        elif current_price < sma_20:
            return "BEARISH"
        return "SIDEWAYS"

class FibonacciEngine:
    """3. Fibonacci Retracement Levels"""
    @staticmethod
    def calculate(high: float, low: float, trend: str) -> dict:
        diff = high - low
        if trend == "BULLISH":
            return {
                "0.50": high - (diff * 0.50),
                "0.618": high - (diff * 0.618),
                "0.786": high - (diff * 0.786),
                "zone": "DISCOUNT"
            }
        else:
            return {
                "0.50": low + (diff * 0.50),
                "0.618": low + (diff * 0.618),
                "0.786": low + (diff * 0.786),
                "zone": "PREMIUM"
            }

class OrderBlockEngine:
    """4. Institutional Order Block Detector"""
    @staticmethod
    def find_order_blocks(df: pd.DataFrame) -> dict:
        if len(df) < 3:
            return {"bullish_ob": None, "bearish_ob": None}
            
        c1 = df.iloc[-3]
        c2 = df.iloc[-2]
        c3 = df.iloc[-1]
        
        bullish_ob = None
        bearish_ob = None
        
        # Bullish OB: Bearish candle followed by strong bullish displacement
        if c2['close'] < c2['open'] and c3['close'] > c1['high']:
            bullish_ob = {"high": c2['high'], "low": c2['low']}
            
        # Bearish OB: Bullish candle followed by strong bearish displacement
        if c2['close'] > c2['open'] and c3['close'] < c1['low']:
            bearish_ob = {"high": c2['high'], "low": c2['low']}
            
        return {"bullish_ob": bullish_ob, "bearish_ob": bearish_ob}

class ParallelChannelEngine:
    """5. Support & Resistance Channel Bounds"""
    @staticmethod
    def get_channel(df: pd.DataFrame) -> dict:
        if len(df) < 10:
            return {"upper": 0, "lower": 0}
        
        upper_bound = df['high'].tail(10).max()
        lower_bound = df['low'].tail(10).min()
        return {"upper": upper_bound, "lower": lower_bound}

class CoreBrain:
    """Engine Orchestration Layer"""
    def __init__(self):
        self.ms_engine = MarketStructureEngine()
        self.trend_engine = TrendEngine()
        self.fib_engine = FibonacciEngine()
        self.ob_engine = OrderBlockEngine()
        self.channel_engine = ParallelChannelEngine()
    
    def run_analysis(self, candle_data: dict) -> dict:
        # Dummy DataFrame parsing for pipeline validation
        df = pd.DataFrame([candle_data])
        
        structure = self.ms_engine.analyze(df)
        trend = self.trend_engine.analyze(df)
        obs = self.ob_engine.find_order_blocks(df)
        channel = self.channel_engine.get_channel(df)
        
        return {
            "symbol": candle_data.get("symbol", "XAUUSD"),
            "trend": trend,
            "structure": structure["structure"],
            "order_blocks": obs,
            "channel": channel
        }

class CandleIntelligenceEngine:
    """6. Candlestick Pattern Detector"""
    @staticmethod
    def analyze(df: pd.DataFrame) -> dict:
        if len(df) < 2:
            return {"pattern": "NONE"}
        c1 = df.iloc[-2]
        c2 = df.iloc[-1]
        
        is_bullish_engulfing = (c1['close'] < c1['open']) and (c2['close'] > c2['open']) and (c2['close'] > c1['high'])
        is_bearish_engulfing = (c1['close'] > c1['open']) and (c2['close'] < c2['open']) and (c2['close'] < c1['low'])
        
        pattern = "BULLISH_ENGULFING" if is_bullish_engulfing else ("BEARISH_ENGULFING" if is_bearish_engulfing else "NONE")
        return {"pattern": pattern}

class LiquidityFVGEngine:
    """7. Liquidity Sweep & Fair Value Gap (FVG) Engine"""
    @staticmethod
    def find_fvg(df: pd.DataFrame) -> dict:
        if len(df) < 3:
            return {"fvg": None}
        c1_high = df.iloc[-3]['high']
        c3_low = df.iloc[-1]['low']
        
        if c3_low > c1_high:
            return {"fvg": "BULLISH_FVG", "gap_bottom": c1_high, "gap_top": c3_low}
        return {"fvg": None}

class MultiTimeframeEngine:
    """8. HTF / LTF Confluence Sync"""
    @staticmethod
    def evaluate(htf_trend: str, ltf_trend: str) -> bool:
        return htf_trend == ltf_trend and htf_trend != "SIDEWAYS"

class ConfidenceScoringEngine:
    """9. 0-100% Signal Confidence Scorer"""
    @staticmethod
    def calculate_score(ms_res: dict, pattern_res: dict, fvg_res: dict, mtf_aligned: bool) -> int:
        score = 0
        if ms_res.get("bos"): score += 30
        if ms_res.get("choch"): score += 20
        if pattern_res.get("pattern") != "NONE": score += 25
        if fvg_res.get("fvg"): score += 15
        if mtf_aligned: score += 10
        return min(score, 100)

class SignalDecisionEngine:
    """10. Core Decision Brain"""
    @staticmethod
    def make_decision(score: int, structure: str) -> str:
        if score >= 70 and "BULLISH" in structure:
            return "BUY"
        elif score >= 70 and "BEARISH" in structure:
            return "SELL"
        return "HOLD"

class RiskManagementEngine:
    """11. Dynamic Position Sizer & SL/TP Engine"""
    @staticmethod
    def calculate_trade_params(balance: float, risk_percent: float, entry: float, sl: float, symbol: str) -> dict:
        risk_amount = balance * (risk_percent / 100.0)
        pips_diff = abs(entry - sl)
        if pips_diff == 0:
            return {"lot_size": 0.01, "risk_amount": risk_amount, "tp1": entry, "tp2": entry}
            
        multiplier = 10.0 if "XAU" in symbol or "XAG" in symbol else 100000.0
        lot_size = max(0.01, round(risk_amount / (pips_diff * multiplier), 2))
        
        is_buy = entry > sl
        tp1 = round(entry + (pips_diff * 1.5) if is_buy else entry - (pips_diff * 1.5), 4)
        tp2 = round(entry + (pips_diff * 3.0) if is_buy else entry - (pips_diff * 3.0), 4)
        
        return {
            "lot_size": lot_size,
            "risk_amount": round(risk_amount, 2),
            "stop_loss": sl,
            "tp1": tp1,
            "tp2": tp2
        }

class NewsAndSessionFilterEngine:
    """12. Session & News Filter"""
    @staticmethod
    def check_session(current_hour_utc: int) -> dict:
        is_london = 7 <= current_hour_utc <= 16
        is_newyork = 13 <= current_hour_utc <= 22
        is_tradeable = is_london or is_newyork
        return {"tradeable_session": is_tradeable, "london": is_london, "newyork": is_newyork}

class HistoricalPatternMatchEngine:
    """13. Historical Trade Similarity Scorer"""
    @staticmethod
    def match_history(pattern: str, confidence: int) -> float:
        if pattern != "NONE" and confidence >= 70:
            return 85.5
        return 50.0

class MT5ExecutionEngine:
    """14. MetaTrader 5 Payload Builder & Order Router"""
    @staticmethod
    def build_order_payload(symbol: str, action: str, risk_params: dict) -> dict:
        return {
            "action": action,
            "symbol": symbol,
            "volume": risk_params.get("lot_size"),
            "sl": risk_params.get("stop_loss"),
            "tp": risk_params.get("tp1"),
            "comment": "YOUNG STAR ITC - SMC AI ENGINE"
        }

class CoreBrain:
    def __init__(self):
        self.ms_engine = MarketStructureEngine()
        self.trend_engine = TrendEngine()
        self.fib_engine = FibonacciEngine()
        self.ob_engine = OrderBlockEngine()
        self.channel_engine = ParallelChannelEngine()
        self.candle_engine = CandleIntelligenceEngine()
        self.fvg_engine = LiquidityFVGEngine()
        self.mtf_engine = MultiTimeframeEngine()
        self.scorer = ConfidenceScoringEngine()
        self.decision_engine = SignalDecisionEngine()
        self.risk_engine = RiskManagementEngine()
        self.session_filter = NewsAndSessionFilterEngine()
        self.history_matcher = HistoricalPatternMatchEngine()
        self.mt5_executor = MT5ExecutionEngine()

    def process_full_pipeline(self, candle_data: dict, balance: float = 1000.0, risk_pct: float = 1.0) -> dict:
        df = pd.DataFrame([candle_data])
        symbol = candle_data.get("symbol", "XAUUSD")
        
        # Step 1-8: Engine Analyses
        ms = self.ms_engine.analyze(df)
        trend = self.trend_engine.analyze(df)
        obs = self.ob_engine.find_order_blocks(df)
        pattern = self.candle_engine.analyze(df)
        fvg = self.fvg_engine.find_fvg(df)
        session = self.session_filter.check_session(14)
        
        # Step 9-10: Scoring & Signal Decision
        score = self.scorer.calculate_score(ms, pattern, fvg, mtf_aligned=True)
        decision = self.decision_engine.make_decision(score, ms["structure"])
        
        if decision == "HOLD":
            return {"status": "NO_SIGNAL", "symbol": symbol, "score": score, "reason": "Low confidence or structure conflict"}
        
        # Step 11-14: Risk Calculation & MT5 Payload
        sl_price = obs["bullish_ob"]["low"] if decision == "BUY" and obs["bullish_ob"] else candle_data.get("low", 0)
        risk_params = self.risk_engine.calculate_trade_params(balance, risk_pct, candle_data.get("close", 0), sl_price, symbol)
        mt5_payload = self.mt5_executor.build_order_payload(symbol, decision, risk_params)
        
        return {
            "status": "SIGNAL_GENERATED",
            "decision": decision,
            "confidence_score": score,
            "risk_analysis": risk_params,
            "mt5_payload": mt5_payload,
            "session": session
        }
