from dataclasses import dataclass, asdict
from typing import Any

from .candle import CandleData


@dataclass(frozen=True)
class FVGZone:
    index: int
    direction: str
    zone_low: float
    zone_high: float
    state: str
    confirmed: bool
    trend_alignment: str
    confluence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FVGEngine:
    """Part 6: three-candle Fair Value Gap detection only."""

    @staticmethod
    def _state(candles: list[CandleData], start: int, low: float, high: float, direction: str) -> str:
        touches = 0
        for c in candles[start + 1:]:
            if direction == "BULLISH" and c.close < low:
                return "INVALIDATED"
            if direction == "BEARISH" and c.close > high:
                return "INVALIDATED"
            if c.low <= high and c.high >= low:
                touches += 1
                if touches >= 2:
                    return "RETESTED"
        return "TOUCHED" if touches == 1 else "VIRGIN"

    def detect(self, candles: list[CandleData], current_index: int, trend_context: dict[str, Any], timeframe: str) -> dict[str, Any]:
        if not candles or current_index < 0:
            return {"timeframe": timeframe, "zones": [], "priority": None}
        end = min(current_index, len(candles) - 1)
        visible = candles[: end + 1]
        trend = trend_context.get("direction", "SIDEWAYS")
        zones: list[FVGZone] = []

        for i in range(2, len(visible)):
            c1, _, c3 = visible[i - 2], visible[i - 1], visible[i]
            direction: str | None = None
            low = high = 0.0
            if c1.low > c3.high:
                direction, low, high = "BULLISH", c3.high, c1.low
            elif c1.high < c3.low:
                direction, low, high = "BEARISH", c1.high, c3.low
            if direction is None:
                continue

            confirmed = i + 1 < len(visible)
            state = self._state(visible, i, low, high, direction) if confirmed else "VIRGIN"
            alignment = "ALIGNED" if trend == direction else "NOT_ALIGNED"
            zones.append(FVGZone(i, direction, low, high, state, confirmed, alignment, {}))

        zones.sort(key=lambda z: z.index, reverse=True)
        return {"timeframe": timeframe, "zones": [z.to_dict() for z in zones], "priority": zones[0].to_dict() if zones else None}
