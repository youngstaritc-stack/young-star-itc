from typing import Any

from .candle import CandleData


class TrendEngine:
    """Part 1: five-candle pivot and market-structure analysis only."""

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
        if len(highs) < 2 or len(lows) < 2:
            return "SIDEWAYS", "UNCONFIRMED"
        hh = highs[-1]["price"] > highs[-2]["price"]
        hl = lows[-1]["price"] > lows[-2]["price"]
        lh = highs[-1]["price"] < highs[-2]["price"]
        ll = lows[-1]["price"] < lows[-2]["price"]
        if hh and hl:
            return "BULLISH", "HH+HL"
        if lh and ll:
            return "BEARISH", "LH+LL"
        return "SIDEWAYS", "MIXED_STRUCTURE"

    def detect_market_structure(self, candles: list[CandleData], current_index: int) -> dict[str, Any]:
        if not candles or current_index < 0:
            return {
                "direction": "SIDEWAYS", "confidence": 0, "structure": "UNCONFIRMED",
                "swing_highs": [], "swing_lows": [], "trend_change_detected": False,
                "trend_start_confirmed": False, "is_sideways": True,
            }

        end = min(current_index, len(candles) - 1)
        visible = candles[: end + 1]
        highs, lows = self._detect_swings(visible)
        direction, structure = self._analyze_structure(highs, lows)

        previous_direction = "SIDEWAYS"
        if len(highs) >= 3 and len(lows) >= 3:
            previous_direction, _ = self._analyze_structure(highs[:-1], lows[:-1])
        trend_change = direction in {"BULLISH", "BEARISH"} and previous_direction not in {"SIDEWAYS", direction}
        confirmed = direction in {"BULLISH", "BEARISH"}

        return {
            "direction": direction,
            "confidence": 90 if confirmed else 50,
            "structure": structure,
            "swing_highs": highs,
            "swing_lows": lows,
            "trend_change_detected": trend_change,
            "trend_start_confirmed": confirmed,
            "is_sideways": direction == "SIDEWAYS",
        }


def detect_market_structure(candles: list[CandleData], current_index: int) -> dict[str, Any]:
    return TrendEngine().detect_market_structure(candles, current_index)
