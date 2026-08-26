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
    RETRACEMENT_RATIOS = (0.382, 0.50, 0.618)
    EXTENSION_RATIOS = (1.618, 2.618, 3.618, 4.618)
    PRIORITY = (0.382, 0.50, 0.618)

    @staticmethod
    def _detect_main_swing(candles: list[CandleData]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        highs: list[dict[str, Any]] = []
        lows: list[dict[str, Any]] = []
        for i in range(2, len(candles) - 2):
            c = candles[i]
            if all(c.high > candles[j].high for j in (i - 2, i - 1, i + 1, i + 2)):
                highs.append({"index": i, "price": c.high})
            if all(c.low < candles[j].low for j in (i - 2, i - 1, i + 1, i + 2)):
                lows.append({"index": i, "price": c.low})
        if not highs or not lows:
            return None, None
        high = highs[-1]
        low = lows[-1]
        return (high, low) if high["index"] > low["index"] else (low, high)

    @staticmethod
    def _update_virgin_status(level: FibonacciLevel, candles: list[CandleData], swing_end: int) -> FibonacciLevel:
        status = "VIRGIN"
        touched = False
        retested = False
        for c in candles[swing_end + 1 :]:
            if c.low <= level.price <= c.high:
                if not touched:
                    touched = True
                    status = "TOUCHED"
                else:
                    retested = True
                    status = "RETESTED"
            if touched and ((level.ratio < 0.5 and c.close > level.price) or (level.ratio >= 0.5 and c.close < level.price)):
                continue
        return FibonacciLevel(level.name, level.ratio, level.price, status)

    def analyze(self, candles: list[CandleData], timeframe: str) -> dict[str, Any]:
        if len(candles) < 5:
            return {"timeframe": timeframe, "levels": {}, "virgin_levels": [], "priority_level": None, "swing_high": None, "swing_low": None}
        swing_a, swing_b = self._detect_main_swing(candles)
        if swing_a is None or swing_b is None:
            return {"timeframe": timeframe, "levels": {}, "virgin_levels": [], "priority_level": None, "swing_high": None, "swing_low": None}
        swing_high = max(swing_a, swing_b, key=lambda x: x["price"])
        swing_low = min(swing_a, swing_b, key=lambda x: x["price"])
        high = swing_high["price"]
        low = swing_low["price"]
        span = high - low
        levels: dict[str, dict[str, Any]] = {}
        for ratio in self.RETRACEMENT_RATIOS:
            price = high - span * ratio
            level = FibonacciLevel(str(ratio), ratio, price)
            level = self._update_virgin_status(level, candles, max(swing_high["index"], swing_low["index"]))
            levels[str(ratio)] = {"ratio": ratio, "price": level.price, "status": level.status}
        virgin = [v for v in levels.values() if v["status"] == "VIRGIN"]
        priority = next((levels[str(r)] for r in self.PRIORITY if str(r) in levels and levels[str(r)]["status"] != "INVALIDATED"), None)
        return {"timeframe": timeframe, "levels": levels, "virgin_levels": virgin, "priority_level": priority, "swing_high": swing_high, "swing_low": swing_low}

    def analyze_extension(self, candles: list[CandleData], timeframe: str, retracement_data: dict[str, Any]) -> dict[str, Any]:
        priority = retracement_data.get("priority_level")
        swing_high = retracement_data.get("swing_high")
        swing_low = retracement_data.get("swing_low")
        if not priority or not swing_high or not swing_low:
            return {"timeframe": timeframe, "extension_1_618": None, "extension_2_618": None, "tp_always": None, "final_target": None}
        a = swing_low["price"]
        b = swing_high["price"]
        c = priority["price"]
        leg = abs(b - a)
        bullish = swing_low["index"] < swing_high["index"]
        def ext(ratio: float) -> float:
            return c + leg * ratio if bullish else c - leg * ratio
        result = {
            "timeframe": timeframe,
            "point_c": c,
            "extension_1_618": ext(1.618),
            "extension_2_618": ext(2.618),
            "extension_3_618": ext(3.618),
            "extension_4_618": ext(4.618),
        }
        result["tp_always"] = result["extension_3_618"]
        result["final_target"] = result["extension_4_618"]
        return result
