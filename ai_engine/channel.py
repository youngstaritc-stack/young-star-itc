from dataclasses import dataclass, asdict
from typing import Any

from .candle import CandleData


@dataclass(frozen=True)
class Channel:
    direction: str
    upper_boundary: dict[str, Any]
    lower_boundary: dict[str, Any]
    slope: float
    state: str
    upper_touches: int
    lower_touches: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ChannelEngine:
    PARALLEL_SLOPE_TOLERANCE = 0.05

    @staticmethod
    def _slope(p1: dict[str, Any], p2: dict[str, Any]) -> float:
        dx = p2["index"] - p1["index"]
        return 0.0 if dx == 0 else (p2["price"] - p1["price"]) / dx

    @staticmethod
    def _touches(candles: list[CandleData], boundary: dict[str, Any], slope: float, is_upper: bool) -> int:
        count = 0
        for i, c in enumerate(candles):
            expected = boundary["price"] + slope * (i - boundary["index"])
            if is_upper and abs(c.high - expected) <= max(1e-9, abs(expected) * 0.001):
                count += 1
            if not is_upper and abs(c.low - expected) <= max(1e-9, abs(expected) * 0.001):
                count += 1
        return count

    def detect(self, candles: list[CandleData], current_index: int, trend_context: dict[str, Any], timeframe: str) -> dict[str, Any]:
        visible = candles[: min(current_index, len(candles) - 1) + 1]
        highs = trend_context.get("swing_highs", [])
        lows = trend_context.get("swing_lows", [])
        direction = trend_context.get("direction", "SIDEWAYS")
        if direction == "BULLISH" and len(highs) >= 2 and len(lows) >= 2:
            upper = highs[-2]
            upper2 = highs[-1]
            lower = lows[-2]
            lower2 = lows[-1]
            slope_u = self._slope(upper, upper2)
            slope_l = self._slope(lower, lower2)
            slope = (slope_u + slope_l) / 2
            valid = abs(slope_u - slope_l) <= self.PARALLEL_SLOPE_TOLERANCE
            upper_touches = self._touches(visible, upper, slope_u, True)
            lower_touches = self._touches(visible, lower, slope_l, False)
            channel = Channel("BULLISH", upper, lower, slope, "VIRGIN", upper_touches, lower_touches)
            if valid and upper_touches >= 2 and lower_touches >= 2:
                for c in visible:
                    i = visible.index(c)
                    up = upper["price"] + slope * (i - upper["index"])
                    lo = lower["price"] + slope * (i - lower["index"])
                    if c.close > up or c.close < lo:
                        channel = Channel(channel.direction, channel.upper_boundary, channel.lower_boundary, channel.slope, "INVALIDATED", channel.upper_touches, channel.lower_touches)
                        break
            return {"timeframe": timeframe, **channel.to_dict()}
        if direction == "BEARISH" and len(highs) >= 2 and len(lows) >= 2:
            upper = highs[-2]
            upper2 = highs[-1]
            lower = lows[-2]
            lower2 = lows[-1]
            slope_u = self._slope(upper, upper2)
            slope_l = self._slope(lower, lower2)
            slope = (slope_u + slope_l) / 2
            valid = abs(slope_u - slope_l) <= self.PARALLEL_SLOPE_TOLERANCE
            upper_touches = self._touches(visible, upper, slope_u, True)
            lower_touches = self._touches(visible, lower, slope_l, False)
            state = "VIRGIN"
            if valid and upper_touches >= 2 and lower_touches >= 2:
                for i, c in enumerate(visible):
                    up = upper["price"] + slope * (i - upper["index"])
                    lo = lower["price"] + slope * (i - lower["index"])
                    if c.close > up or c.close < lo:
                        state = "INVALIDATED"
                        break
            return {"timeframe": timeframe, **Channel("BEARISH", upper, lower, slope, state, upper_touches, lower_touches).to_dict()}
        if visible:
            high = max(c.high for c in visible)
            low = min(c.low for c in visible)
        else:
            high = low = 0.0
        return {"timeframe": timeframe, "direction": "SIDEWAYS", "upper_boundary": {"index": len(visible) - 1, "price": high}, "lower_boundary": {"index": len(visible) - 1, "price": low}, "slope": 0.0, "state": "VIRGIN", "upper_touches": 0, "lower_touches": 0}
