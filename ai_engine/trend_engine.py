from typing import Any

from .candle import CandleData


class TrendEngine:
    """Rule-bound market structure engine. Never generates BUY/SELL signals."""

    @staticmethod
    def _detect_swings(candles: list[CandleData]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        highs: list[dict[str, Any]] = []
        lows: list[dict[str, Any]] = []
        for i in range(2, len(candles) - 2):
            c = candles[i]
            if all(c.high > candles[j].high for j in (i - 2, i - 1, i + 1, i + 2)):
                highs.append({"index": i, "price": c.high})
            if all(c.low < candles[j].low for j in (i - 2, i - 1, i + 1, i + 2)):
                lows.append({"index": i, "price": c.low})
        return highs, lows

    @staticmethod
    def _analyze_structure(highs: list[dict[str, Any]], lows: list[dict[str, Any]]) -> tuple[str, str]:
        if len(highs) >= 2 and len(lows) >= 2:
            hh = highs[-1]["price"] > highs[-2]["price"]
            hl = lows[-1]["price"] > lows[-2]["price"]
            lh = highs[-1]["price"] < highs[-2]["price"]
            ll = lows[-1]["price"] < lows[-2]["price"]
            if hh and hl:
                return "BULLISH", "HH+HL"
            if lh and ll:
                return "BEARISH", "LH+LL"
        return "SIDEWAYS", "UNCONFIRMED"

    def detect_market_structure(self, candles: list[CandleData], current_index: int) -> dict[str, Any]:
        if not candles:
            return {"direction": "SIDEWAYS", "confidence": 0, "structure": "UNCONFIRMED", "swing_highs": [], "swing_lows": [], "trend_change_detected": False, "trend_start_confirmed": False, "is_sideways": True}
        end = min(current_index, len(candles) - 1)
        visible = candles[: end + 1]
        highs, lows = self._detect_swings(visible)
        direction, structure = self._analyze_structure(highs, lows)
        confidence = 90 if direction in {"BULLISH", "BEARISH"} else 50
        return {
            "direction": direction,
            "confidence": confidence,
            "structure": structure,
            "swing_highs": highs,
            "swing_lows": lows,
            "trend_change_detected": len(highs) >= 2 or len(lows) >= 2,
            "trend_start_confirmed": direction in {"BULLISH", "BEARISH"},
            "is_sideways": direction == "SIDEWAYS",
        }


def detect_market_structure(candles: list[CandleData], current_index: int) -> dict[str, Any]:
    return TrendEngine().detect_market_structure(candles, current_index)
