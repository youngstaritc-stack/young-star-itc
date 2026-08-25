from typing import Any, Dict, List

from .candle import CandleData


class FVGEngine:
    """Part 7 FVG: informational context only; never an entry signal."""

    def detect(self, candles: List[CandleData], current_index: int, trend_context: Dict[str, Any], timeframe: str) -> List[Dict[str, Any]]:
        visible = candles[: min(current_index, len(candles) - 1) + 1] if candles and current_index >= 0 else []
        result = []
        for i in range(2, len(visible)):
            c1, c2, c3 = visible[i - 2], visible[i - 1], visible[i]
            if c1.low > c3.high:
                result.append(self._make(i, "BULLISH", c3.high, c1.low, trend_context.get("direction")))
            elif c1.high < c3.low:
                result.append(self._make(i, "BEARISH", c1.high, c3.low, trend_context.get("direction")))
        return result

    @staticmethod
    def _make(index, kind, low, high, trend):
        return {"formation_index": index, "zone": {"low": low, "high": high}, "type": kind, "state": "VIRGIN", "trend_alignment": kind == trend, "confluence": {"trend_alignment": kind == trend}}
