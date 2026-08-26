from dataclasses import dataclass
from typing import Any

from .candle import CandleData


@dataclass(frozen=True)
class FibonacciLevel:
    name: str
    ratio: float
    price: float
    status: str = "VIRGIN"


class FibonacciEngine:
    """Parts 2-3: Fibonacci retracement and extension rules only."""

    RETRACEMENT_RATIOS = (0.382, 0.50, 0.618)
    EXTENSION_RATIOS = (1.618, 2.618, 3.618, 4.618)
    PRIORITY = (0.382, 0.50, 0.618)

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

    @classmethod
    def _detect_main_swing(cls, candles: list[CandleData]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        highs, lows = cls._detect_swings(candles)
        if not highs or not lows:
            return None, None
        return highs[-1], lows[-1]

    @staticmethod
    def _level_status(
        level: float,
        candles: list[CandleData],
        swing_high: dict[str, Any],
        swing_low: dict[str, Any],
        direction: str,
    ) -> str:
        swing_end = max(swing_high["index"], swing_low["index"])
        touches = 0
        for c in candles[swing_end + 1:]:
            if c.low <= level <= c.high:
                touches += 1
            # Invalidate only when price closes through the swing endpoint.
            if direction == "BULLISH" and c.close < swing_low["price"]:
                return "INVALIDATED"
            if direction == "BEARISH" and c.close > swing_high["price"]:
                return "INVALIDATED"
        if touches >= 2:
            return "RETESTED"
        if touches == 1:
            return "TOUCHED"
        return "VIRGIN"

    def analyze(self, candles: list[CandleData], timeframe: str) -> dict[str, Any]:
        empty = {
            "timeframe": timeframe,
            "levels": {},
            "virgin_levels": [],
            "priority_level": None,
            "swing_high": None,
            "swing_low": None,
        }
        if len(candles) < 5:
            return empty

        swing_high, swing_low = self._detect_main_swing(candles)
        if swing_high is None or swing_low is None:
            return empty

        high = float(swing_high["price"])
        low = float(swing_low["price"])
        span = high - low
        if span <= 0:
            return {**empty, "swing_high": swing_high, "swing_low": swing_low}

        direction = "BULLISH" if swing_low["index"] < swing_high["index"] else "BEARISH"
        levels: dict[str, dict[str, Any]] = {}
        for ratio in self.RETRACEMENT_RATIOS:
            price = high - span * ratio if direction == "BULLISH" else low + span * ratio
            status = self._level_status(price, candles, swing_high, swing_low, direction)
            levels[str(ratio)] = {"ratio": ratio, "price": price, "status": status}

        virgin_levels = [levels[str(r)] for r in self.PRIORITY if levels[str(r)]["status"] == "VIRGIN"]
        return {
            "timeframe": timeframe,
            "direction": direction,
            "levels": levels,
            "virgin_levels": virgin_levels,
            "priority_level": virgin_levels[0] if virgin_levels else None,
            "swing_high": swing_high,
            "swing_low": swing_low,
        }

    def analyze_extension(
        self,
        candles: list[CandleData],
        timeframe: str,
        retracement_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Part 3: FEX-001..004 from the selected retracement point C."""
        priority = retracement_data.get("priority_level")
        swing_high = retracement_data.get("swing_high")
        swing_low = retracement_data.get("swing_low")
        empty = {
            "timeframe": timeframe,
            "point_c": None,
            "extension_1_618": None,
            "extension_2_618": None,
            "extension_3_618": None,
            "extension_4_618": None,
            "tp_always": None,
            "final_target": None,
        }
        if not priority or not swing_high or not swing_low:
            return empty

        a = float(swing_low["price"])
        b = float(swing_high["price"])
        c = float(priority["price"])
        leg = abs(b - a)
        bullish = swing_low["index"] < swing_high["index"]

        def extension(ratio: float) -> float:
            return c + leg * ratio if bullish else c - leg * ratio

        values = {ratio: extension(ratio) for ratio in self.EXTENSION_RATIOS}
        return {
            "timeframe": timeframe,
            "point_c": c,
            "extension_1_618": values[1.618],
            "extension_2_618": values[2.618],
            "extension_3_618": values[3.618],
            "extension_4_618": values[4.618],
            "tp_always": values[3.618],
            "final_target": values[4.618],
        }
