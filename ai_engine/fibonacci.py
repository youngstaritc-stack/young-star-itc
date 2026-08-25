from typing import Any, Dict, List, Optional

from .candle import CandleData
from .trend_engine import TrendEngine


class FibonacciEngine:
    """Parts 2-3: approved Fibonacci retracement and extension logic."""

    def analyze(self, candles: List[CandleData], timeframe: str) -> Dict[str, Any]:
        visible = list(candles)
        if len(visible) < 5:
            return self._empty_retracement(timeframe)
        highs, lows = TrendEngine()._detect_swings(visible)
        if not highs or not lows:
            return self._empty_retracement(timeframe)

        high = highs[-1]
        low = lows[-1]
        direction = "BULLISH" if high["index"] > low["index"] else "BEARISH"
        hi, lo = high["price"], low["price"]
        diff = hi - lo
        if diff <= 0:
            return self._empty_retracement(timeframe)

        if direction == "BULLISH":
            levels = {"38.2": hi - diff * 0.382, "50.0": hi - diff * 0.50, "61.8": hi - diff * 0.618}
        else:
            levels = {"38.2": lo + diff * 0.382, "50.0": lo + diff * 0.50, "61.8": lo + diff * 0.618}

        virgin_levels = self._virgin_levels(visible, levels)
        priority = next((k for k in ("38.2", "50.0", "61.8") if k in virgin_levels), None)
        states = {k: ("VIRGIN" if k in virgin_levels else self._state_for_level(visible, v)) for k, v in levels.items()}
        return {"timeframe": timeframe, "direction": direction, "swing_high": high, "swing_low": low, "levels": levels, "states": states, "virgin_levels": virgin_levels, "priority_level": {"name": priority, "price": levels[priority]} if priority else None}

    def analyze_extension(self, candles: List[CandleData], timeframe: str, retracement_data: Dict[str, Any]) -> Dict[str, Any]:
        priority = retracement_data.get("priority_level")
        high = retracement_data.get("swing_high")
        low = retracement_data.get("swing_low")
        direction = retracement_data.get("direction")
        if not priority or not high or not low:
            return {"timeframe": timeframe, "direction": direction, "extension_1_618": None, "extension_2_618": None, "extension_3_618": None, "extension_4_618": None, "tp_always": None, "final_target": None}

        a, b = low["price"], high["price"]
        c = priority["price"]
        span = abs(b - a)
        sign = 1 if direction == "BULLISH" else -1
        return {
            "timeframe": timeframe,
            "direction": direction,
            "point_c": c,
            "extension_1_618": c + sign * span * 1.618,
            "extension_2_618": c + sign * span * 2.618,
            "extension_3_618": c + sign * span * 3.618,
            "extension_4_618": c + sign * span * 4.618,
            "tp_always": c + sign * span * 3.618,
            "final_target": c + sign * span * 4.618,
        }

    def _virgin_levels(self, candles: List[CandleData], levels: Dict[str, float]) -> List[str]:
        result = []
        for name, price in levels.items():
            touched = any(c.low <= price <= c.high for c in candles[-1:])
            if not touched:
                result.append(name)
        return result

    @staticmethod
    def _state_for_level(candles: List[CandleData], price: float) -> str:
        hits = sum(c.low <= price <= c.high for c in candles)
        return "RETESTED" if hits > 1 else "TOUCHED"

    @staticmethod
    def _empty_retracement(timeframe: str) -> Dict[str, Any]:
        return {"timeframe": timeframe, "direction": "SIDEWAYS", "swing_high": None, "swing_low": None, "levels": {}, "states": {}, "virgin_levels": [], "priority_level": None}
