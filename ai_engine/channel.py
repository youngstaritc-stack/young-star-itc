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
    """Part 5: Parallel Channel rules only."""

    PARALLEL_SLOPE_TOLERANCE = 0.05

    @staticmethod
    def _slope(a: dict[str, Any], b: dict[str, Any]) -> float:
        dx = b["index"] - a["index"]
        return 0.0 if dx == 0 else (b["price"] - a["price"]) / dx

    @staticmethod
    def _touch_count(candles: list[CandleData], boundary: dict[str, Any], slope: float, upper: bool) -> int:
        count = 0
        for i, c in enumerate(candles):
            expected = boundary["price"] + slope * (i - boundary["index"])
            if upper and c.high == expected:
                count += 1
            elif not upper and c.low == expected:
                count += 1
        return count

    @staticmethod
    def _body_break(c: CandleData, upper: float, lower: float) -> bool:
        body_high = max(c.open, c.close)
        body_low = min(c.open, c.close)
        return body_low > upper or body_high < lower

    def detect(
        self,
        candles: list[CandleData],
        current_index: int,
        trend_context: dict[str, Any],
        timeframe: str,
    ) -> dict[str, Any]:
        if not candles or current_index < 0:
            return {
                "timeframe": timeframe, "direction": "SIDEWAYS",
                "upper_boundary": None, "lower_boundary": None, "slope": 0.0,
                "state": "VIRGIN", "upper_touches": 0, "lower_touches": 0,
            }

        end = min(current_index, len(candles) - 1)
        visible = candles[: end + 1]
        direction = trend_context.get("direction", "SIDEWAYS")
        highs = trend_context.get("swing_highs", [])
        lows = trend_context.get("swing_lows", [])

        if direction not in {"BULLISH", "BEARISH"} or len(highs) < 2 or len(lows) < 2:
            high = max(c.high for c in visible)
            low = min(c.low for c in visible)
            return {
                "timeframe": timeframe,
                "direction": "SIDEWAYS",
                "upper_boundary": {"index": end, "price": high},
                "lower_boundary": {"index": end, "price": low},
                "slope": 0.0,
                "state": "VIRGIN",
                "upper_touches": 0,
                "lower_touches": 0,
            }

        upper_a, upper_b = highs[-2], highs[-1]
        lower_a, lower_b = lows[-2], lows[-1]
        upper_slope = self._slope(upper_a, upper_b)
        lower_slope = self._slope(lower_a, lower_b)
        valid_parallel = abs(upper_slope - lower_slope) <= self.PARALLEL_SLOPE_TOLERANCE
        slope = (upper_slope + lower_slope) / 2.0
        upper_touches = self._touch_count(visible, upper_a, upper_slope, True)
        lower_touches = self._touch_count(visible, lower_a, lower_slope, False)
        state = "VIRGIN"

        if valid_parallel and upper_touches >= 2 and lower_touches >= 2:
            touches = 0
            for i, candle in enumerate(visible):
                upper = upper_a["price"] + slope * (i - upper_a["index"])
                lower = lower_a["price"] + slope * (i - lower_a["index"])
                if self._body_break(candle, upper, lower):
                    state = "INVALIDATED"
                    break
                if candle.low <= upper <= candle.high or candle.low <= lower <= candle.high:
                    touches += 1
            if state != "INVALIDATED":
                state = "RETESTED" if touches >= 2 else ("TOUCHED" if touches == 1 else "VIRGIN")

        return {
            "timeframe": timeframe,
            **Channel(direction, upper_a, lower_a, slope, state, upper_touches, lower_touches).to_dict(),
        }
