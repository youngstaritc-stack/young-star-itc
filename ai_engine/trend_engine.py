from typing import Any, Dict, List, Tuple

from .candle import CandleData


class TrendEngine:
    """Part 1: market structure and trend context only."""

    def detect_market_structure(self, candles: List[CandleData], current_index: int) -> Dict[str, Any]:
        if not candles or current_index < 0:
            return self._empty()

        end = min(current_index, len(candles) - 1)
        visible = candles[: end + 1]
        if len(visible) < 5:
            return self._empty()

        highs, lows = self._detect_swings(visible)
        structure = self._analyze_structure(highs, lows)
        direction = structure["direction"]
        confidence = structure["confidence"]
        previous_direction = self._direction_before_last_swing(highs, lows)

        return {
            "direction": direction,
            "confidence": confidence,
            "structure": structure["structure"],
            "swing_highs": highs,
            "swing_lows": lows,
            "trend_change_detected": bool(previous_direction and direction != previous_direction),
            "trend_start_confirmed": direction in {"BULLISH", "BEARISH"} and len(highs) >= 2 and len(lows) >= 2,
            "is_sideways": direction == "SIDEWAYS",
        }

    def _detect_swings(self, candles: List[CandleData]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        highs: List[Dict[str, Any]] = []
        lows: List[Dict[str, Any]] = []
        for i in range(2, len(candles) - 2):
            c = candles[i]
            if c.high > candles[i - 1].high and c.high > candles[i - 2].high and c.high > candles[i + 1].high and c.high > candles[i + 2].high:
                highs.append({"index": i, "price": c.high})
            if c.low < candles[i - 1].low and c.low < candles[i - 2].low and c.low < candles[i + 1].low and c.low < candles[i + 2].low:
                lows.append({"index": i, "price": c.low})
        return highs, lows

    def _analyze_structure(self, highs: List[Dict[str, Any]], lows: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(highs) < 2 or len(lows) < 2:
            return {"direction": "SIDEWAYS", "confidence": 0, "structure": "INSUFFICIENT"}
        hh = highs[-1]["price"] > highs[-2]["price"]
        hl = lows[-1]["price"] > lows[-2]["price"]
        lh = highs[-1]["price"] < highs[-2]["price"]
        ll = lows[-1]["price"] < lows[-2]["price"]
        if hh and hl:
            return {"direction": "BULLISH", "confidence": 100, "structure": "HH_HL"}
        if lh and ll:
            return {"direction": "BEARISH", "confidence": 100, "structure": "LH_LL"}
        return {"direction": "SIDEWAYS", "confidence": 0, "structure": "MIXED"}

    def _direction_before_last_swing(self, highs: List[Dict[str, Any]], lows: List[Dict[str, Any]]) -> str:
        if len(highs) < 3 or len(lows) < 3:
            return ""
        hh = highs[-2]["price"] > highs[-3]["price"]
        hl = lows[-2]["price"] > lows[-3]["price"]
        lh = highs[-2]["price"] < highs[-3]["price"]
        ll = lows[-2]["price"] < lows[-3]["price"]
        if hh and hl:
            return "BULLISH"
        if lh and ll:
            return "BEARISH"
        return "SIDEWAYS"

    @staticmethod
    def _empty() -> Dict[str, Any]:
        return {
            "direction": "SIDEWAYS",
            "confidence": 0,
            "structure": "INSUFFICIENT",
            "swing_highs": [],
            "swing_lows": [],
            "trend_change_detected": False,
            "trend_start_confirmed": False,
            "is_sideways": True,
        }
