from typing import Any, Dict, List

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
            levels = {
                "38.2": hi - diff * 0.382,
                "50.0": hi - diff * 0.50,
                "61.8": hi - diff * 0.618,
            }
        else:
            levels = {
                "38.2": lo + diff * 0.382,
                "50.0": lo + diff * 0.50,
                "61.8": lo + diff * 0.618,
            }

        states = {name: self._state_for_level(visible, price, direction) for name, price in levels.items()}
        virgin_levels = [name for name, state in states.items() if state == "VIRGIN"]
        priority = next((name for name in ("38.2", "50.0", "61.8") if name in virgin_levels), None)

        return {
            "timeframe": timeframe,
            "direction": direction,
            "swing_high": high,
            "swing_low": low,
            "levels": levels,
            "states": states,
            "virgin_levels": virgin_levels,
            "priority_level": {"name": priority, "price": levels[priority]} if priority else None,
        }

    def analyze_extension(self, candles: List[CandleData], timeframe: str, retracement_data: Dict[str, Any]) -> Dict[str, Any]:
        priority = retracement_data.get("priority_level")
        high = retracement_data.get("swing_high")
        low = retracement_data.get("swing_low")
        direction = retracement_data.get("direction")
        if not priority or not high or not low:
            return {
                "timeframe": timeframe,
                "direction": direction,
                "extension_1_618": None,
                "extension_2_618": None,
                "extension_3_618": None,
                "extension_4_618": None,
                "tp_always": None,
                "final_target": None,
            }

        a, b = low["price"], high["price"]
        c = priority["price"]
        span = abs(b - a)
        sign = 1 if direction == "BULLISH" else -1
        ext_1 = c + sign * span * 1.618
        ext_2 = c + sign * span * 2.618
        ext_3 = c + sign * span * 3.618
        ext_4 = c + sign * span * 4.618
        return {
            "timeframe": timeframe,
            "direction": direction,
            "point_c": c,
            "extension_1_618": ext_1,
            "extension_2_618": ext_2,
            "extension_3_618": ext_3,
            "extension_4_618": ext_4,
            "tp_always": ext_3,
            "final_target": ext_4,
        }

    @staticmethod
    def _state_for_level(candles: List[CandleData], price: float, direction: str) -> str:
        touched = [i for i, c in enumerate(candles) if c.low <= price <= c.high]
        if not touched:
            return "VIRGIN"

        # A level is invalidated only by a decisive close beyond it in the
        # direction of the retracement break. Wick contact alone is a touch.
        if direction == "BULLISH":
            invalidated = any(candles[i].close < price for i in touched)
        else:
            invalidated = any(candles[i].close > price for i in touched)
        if invalidated:
            return "INVALIDATED"
        return "RETESTED" if len(touched) > 1 else "TOUCHED"

    @staticmethod
    def _empty_retracement(timeframe: str) -> Dict[str, Any]:
        return {
            "timeframe": timeframe,
            "direction": "SIDEWAYS",
            "swing_high": None,
            "swing_low": None,
            "levels": {},
            "states": {},
            "virgin_levels": [],
            "priority_level": None,
        }
