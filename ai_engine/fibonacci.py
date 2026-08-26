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
        high = highs[-1]
        low = lows[-1]
        return high, low

    @staticmethod
    def _level_status(level: float, candles: list[CandleData], start_index: int, ratio: float) -> str:
        touches = 0
        for i in range(start_index + 1, len(candles)):
            c = candles[i]
            if c.low <= level <= c.high:
                touches += 1
            # A retracement is invalidated when price closes beyond the swing
            # side represented by the level. No extra threshold is introduced.
            if ratio < 0.5 and c.close > level:
                return "INVALIDATED" if touches == 0 else "RETESTED"
            if ratio >= 0.5 and c.close < level:
                return "INVALIDATED" if touches == 0 else "RETESTED"
        if touches >= 2:
            return "RETESTED"
        if touches == 1:
            return "TOUCHED"
        return "VIRGIN"

    def analyze(self, candles: list[CandleData], timeframe: str) -> dict[str, Any]:
        if len(candles) < 5:
            return {"timeframe": timeframe, "levels": {}, "virgin_levels": [], "priority_level": None, "swing_high": None, "swing_low": None}

        swing_high, swing_low = self._detect_main_swing(candles)
        if swing_high is None or swing_low is None:
            return {"timeframe": timeframe, "levels": {}, "virgin_levels": [], "priority_level": None, "swing_high": None, "swing_low": None}

        high = swing_high["price"]
        low = swing_low["price"]
        span = high - low
        if span <= 0:
            return {"timeframe": timeframe, "levels": {}, "virgin_levels": [], "priority_level": None, "swing_high": swing_high, "swing_low": swing_low}

        levels: dict[str, dict[str, Any]] = {}
        swing_end = max(swing_high["index"], swing_low["index"])
        for ratio in self.RETRACEMENT_RATIOS:
            price = high - span * ratio
            status = self._level_status(price, candles, swing_end, ratio)
            levels[str(ratio)] = {"ratio": ratio, "price": price, "status": status}

        virgin_levels = [levels[str(r)] for r in self.PRIORITY if levels[str(r)]["status"] == "VIRGIN"]
        priority = virgin_levels[0] if virgin_levels else None
        return {
            "timeframe": timeframe,
            "levels": levels,
            "virgin_levels": virgin_levels,
            "priority_level": priority,
            "swing_high": swing_high,
            "swing_low": swing_low,
        }

    def analyze_extension(self, candles: list[CandleData], timeframe: str, retracement_data: dict[str, Any]) -> dict[str, Any]:
        """Part 3: calculate FEX-001..004 from the selected retracement point C."""
        priority = retracement_data.get("priority_level")
        swing_high = retracement_data.get("swing_high")
        swing_low = retracement_data.get("swing_low")
        if not priority or not swing_high or not swing_low:
            return {"timeframe": timeframe, "point_c": None, "extension_1_618": None, "extension_2_618": None, "extension_3_618": None, "extension_4_618": None, "tp_always": None, "final_target": None}

        a = swing_low["price"]
        b = swing_high["price"]
        c = priority["price"]
        leg = abs(b - a)
        bullish = swing_low["index"] < swing_high["index"]

        def extension(ratio: float) -> float:
            return c + leg * ratio if bullish else c - leg * ratio

        e1618 = extension(1.618)
        e2618 = extension(2.618)
        e3618 = extension(3.618)
        e4618 = extension(4.618)
        return {
            "timeframe": timeframe,
            "point_c": c,
            "extension_1_618": e1618,
            "extension_2_618": e2618,
            "extension_3_618": e3618,
            "extension_4_618": e4618,
            "tp_always": e3618,
            "final_target": e4618,
        }
