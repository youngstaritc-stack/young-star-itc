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
    def detect(self, candles: list[CandleData], current_index: int, trend_context: dict[str, Any], timeframe: str) -> dict[str, Any]:
        visible = candles[: min(current_index, len(candles) - 1) + 1]
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
            state = "VIRGIN"
            touches = 0
            for later in visible[i + 1:]:
                if later.low <= high and later.high >= low:
                    touches += 1
            if touches == 1:
                state = "TOUCHED"
            elif touches >= 2:
                state = "RETESTED"
            if direction == "BULLISH" and any(c.close < low for c in visible[i + 1:]):
                state = "INVALIDATED"
            if direction == "BEARISH" and any(c.close > high for c in visible[i + 1:]):
                state = "INVALIDATED"
            trend = trend_context.get("direction", "SIDEWAYS")
            alignment = "ALIGNED" if trend == direction else "NOT_ALIGNED"
            zones.append(FVGZone(i, direction, low, high, state, confirmed, alignment, {}))
        return {"timeframe": timeframe, "zones": [z.to_dict() for z in zones], "priority": zones[-1].to_dict() if zones else None}
