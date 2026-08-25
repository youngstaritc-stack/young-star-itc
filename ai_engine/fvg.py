from typing import Any, Dict, List

from .candle import CandleData


class FVGEngine:
    """Part 6: informational FVG context only; never an entry signal."""

    def detect(self, candles: List[CandleData], current_index: int, trend_context: Dict[str, Any], timeframe: str) -> List[Dict[str, Any]]:
        visible = candles[: min(current_index, len(candles) - 1) + 1] if candles and current_index >= 0 else []
        result: List[Dict[str, Any]] = []

        # i is the third candle of the three-candle formation. A following
        # candle must also exist before the FVG is considered confirmed.
        for i in range(2, len(visible) - 1):
            c1, c2, c3 = visible[i - 2], visible[i - 1], visible[i]
            if c1.low > c3.high:
                result.append(self._make(i, "BULLISH", c3.high, c1.low, visible, trend_context.get("direction"), timeframe))
            elif c1.high < c3.low:
                result.append(self._make(i, "BEARISH", c1.high, c3.low, visible, trend_context.get("direction"), timeframe))
        return result

    @staticmethod
    def _make(index: int, kind: str, low: float, high: float, candles: List[CandleData], trend: str, timeframe: str) -> Dict[str, Any]:
        hits = 0
        state = "VIRGIN"
        for candle in candles[index + 1:]:
            if candle.low <= high and candle.high >= low:
                hits += 1
                if kind == "BULLISH" and candle.close < low:
                    state = "INVALIDATED"
                    break
                if kind == "BEARISH" and candle.close > high:
                    state = "INVALIDATED"
                    break
                state = "TOUCHED"

        if state == "TOUCHED" and hits > 1:
            state = "RETESTED"

        aligned = kind == trend
        return {
            "formation_index": index,
            "confirmation_index": index + 1,
            "zone": {"low": low, "high": high},
            "type": kind,
            "state": state,
            "trend_alignment": aligned,
            "confluence": {"trend_alignment": aligned},
            "timeframe": timeframe,
        }
