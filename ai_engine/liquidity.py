from typing import Any, Dict, List

from .candle import CandleData
from .trend_engine import TrendEngine


class LiquidityEngine:
    """Part 7: informational liquidity and completed sweep tracking."""

    LOOKBACK = 10  # implementation default, not a trading threshold

    def detect(self, candles: List[CandleData], current_index: int, trend_context: Dict[str, Any], timeframe: str) -> List[Dict[str, Any]]:
        visible = candles[: min(current_index, len(candles) - 1) + 1] if candles and current_index >= 0 else []
        highs, lows = TrendEngine()._detect_swings(visible)
        levels = [{"price": x["price"], "index": x["index"], "type": "HIGH", "volume": visible[x["index"]].volume} for x in highs]
        levels += [{"price": x["price"], "index": x["index"], "type": "LOW", "volume": visible[x["index"]].volume} for x in lows]
        levels.sort(key=lambda x: x["volume"], reverse=True)  # LQ-002
        results = []
        for level in levels:
            state, sweep_index = self._state(visible, level)
            results.append({"level": level["price"], "level_type": level["type"], "formation_index": level["index"], "volume": level["volume"], "sweep_index": sweep_index, "state": state, "trend_alignment": self._alignment(level["type"], trend_context.get("direction")), "confluence": {"trend_alignment": self._alignment(level["type"], trend_context.get("direction"))}})
        return results

    @staticmethod
    def _state(candles: List[CandleData], level: Dict[str, Any]):
        price = level["price"]
        start = level["index"] + 1
        for i in range(start, len(candles)):
            c = candles[i]
            if level["type"] == "HIGH" and c.high > price and c.close <= price:
                return "SWEPT", i
            if level["type"] == "LOW" and c.low < price and c.close >= price:
                return "SWEPT", i
        return "VIRGIN", None

    @staticmethod
    def _alignment(level_type: str, trend: str) -> bool:
        return (level_type == "LOW" and trend == "BULLISH") or (level_type == "HIGH" and trend == "BEARISH")
