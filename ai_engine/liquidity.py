from typing import Any, Dict, List

from .candle import CandleData
from .trend_engine import TrendEngine


class LiquidityEngine:
    """Part 7: informational liquidity and completed sweep tracking."""

    LOOKBACK = 10  # implementation default, not a trading threshold

    def detect(self, candles: List[CandleData], current_index: int, trend_context: Dict[str, Any], timeframe: str) -> List[Dict[str, Any]]:
        visible = candles[: min(current_index, len(candles) - 1) + 1] if candles and current_index >= 0 else []
        highs, lows = TrendEngine()._detect_swings(visible)
        levels = [
            {"price": x["price"], "index": x["index"], "type": "HIGH", "volume": visible[x["index"]].volume}
            for x in highs
        ]
        levels += [
            {"price": x["price"], "index": x["index"], "type": "LOW", "volume": visible[x["index"]].volume}
            for x in lows
        ]

        # Volume priority is intentionally deferred by the Rule Book. Keep
        # deterministic chronological ordering instead of using volume as rank.
        levels.sort(key=lambda x: (x["index"], x["type"]))

        results = []
        trend = trend_context.get("direction", "SIDEWAYS")
        for level in levels:
            state, sweep_index = self._state(visible, level)
            alignment = self._alignment(level["type"], trend)
            if state in {"SWEPT", "RETESTED"} and not alignment:
                state = "INVALIDATED"
            results.append({
                "level": level["price"],
                "level_type": level["type"],
                "formation_index": level["index"],
                "volume": level["volume"],
                "sweep_index": sweep_index,
                "state": state,
                "trend_alignment": alignment,
                "confluence": {"trend_alignment": alignment},
                "timeframe": timeframe,
            })
        return results

    @staticmethod
    def _state(candles: List[CandleData], level: Dict[str, Any]):
        price = level["price"]
        start = level["index"] + 1
        sweep_index = None
        for i in range(start, len(candles)):
            c = candles[i]
            if level["type"] == "HIGH" and c.high > price and c.close <= price:
                sweep_index = i
                break
            if level["type"] == "LOW" and c.low < price and c.close >= price:
                sweep_index = i
                break

        if sweep_index is None:
            return "VIRGIN", None

        # A later candle touching the swept level is a retest.
        for i in range(sweep_index + 1, len(candles)):
            c = candles[i]
            if c.low <= price <= c.high:
                return "RETESTED", sweep_index

        # A later confirmed swing outside the original level invalidates it.
        highs, lows = TrendEngine()._detect_swings(candles)
        if level["type"] == "HIGH" and any(x["index"] > sweep_index and x["price"] > price for x in highs):
            return "INVALIDATED", sweep_index
        if level["type"] == "LOW" and any(x["index"] > sweep_index and x["price"] < price for x in lows):
            return "INVALIDATED", sweep_index

        return "SWEPT", sweep_index

    @staticmethod
    def _alignment(level_type: str, trend: str) -> bool:
        return (level_type == "LOW" and trend == "BULLISH") or (level_type == "HIGH" and trend == "BEARISH")
