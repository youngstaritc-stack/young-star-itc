from typing import Any, Dict, List

from .candle import CandleData
from .trend_engine import TrendEngine


class ChannelEngine:
    """Part 5: Parallel Channel using candle body boundaries."""

    PARALLEL_SLOPE_TOLERANCE = 0.05

    def detect(self, candles: List[CandleData], current_index: int, trend_context: Dict[str, Any], timeframe: str) -> Dict[str, Any]:
        visible = candles[: min(current_index, len(candles) - 1) + 1] if candles and current_index >= 0 else []
        highs, lows = TrendEngine()._detect_swings(visible)
        direction = trend_context.get("direction", "SIDEWAYS")
        if len(highs) < 2 or len(lows) < 2:
            return self._empty(timeframe, direction)
        h1, h2 = highs[-2], highs[-1]
        l1, l2 = lows[-2], lows[-1]
        hs = (h2["price"] - h1["price"]) / (h2["index"] - h1["index"])
        ls = (l2["price"] - l1["price"]) / (l2["index"] - l1["index"])
        if direction == "SIDEWAYS":
            hs = ls = 0.0
        elif abs(hs - ls) > self.PARALLEL_SLOPE_TOLERANCE:
            return self._empty(timeframe, direction)
        upper = (h1["index"], h1["price"], hs)
        lower = (l1["index"], l1["price"], ls)
        state = self._state(visible, upper, lower)
        invalid = self._shadow_break(visible, upper, lower)
        if invalid:
            state = "INVALIDATED"
        return {"timeframe": timeframe, "direction": direction, "upper_boundary": upper, "lower_boundary": lower, "slope": hs, "upper_touches": 2, "lower_touches": 2, "state": state}

    @staticmethod
    def _state(candles, upper, lower):
        hits = 0
        u_i, u_p, u_s = upper
        l_i, l_p, l_s = lower
        for i in range(max(u_i, l_i), len(candles)):
            up = u_p + u_s * (i - u_i)
            lp = l_p + l_s * (i - l_i)
            if candles[i].low <= up <= candles[i].high or candles[i].low <= lp <= candles[i].high:
                hits += 1
        return "RETESTED" if hits > 1 else ("TOUCHED" if hits else "VIRGIN")

    @staticmethod
    def _shadow_break(candles, upper, lower):
        u_i, u_p, u_s = upper
        l_i, l_p, l_s = lower
        for i in range(max(u_i, l_i), len(candles)):
            up = u_p + u_s * (i - u_i)
            lp = l_p + l_s * (i - l_i)
            if candles[i].high > up or candles[i].low < lp:
                return True
        return False

    @staticmethod
    def _empty(timeframe, direction):
        return {"timeframe": timeframe, "direction": direction, "upper_boundary": None, "lower_boundary": None, "slope": 0.0, "upper_touches": 0, "lower_touches": 0, "state": "INVALIDATED" if direction != "SIDEWAYS" else "VIRGIN"}
