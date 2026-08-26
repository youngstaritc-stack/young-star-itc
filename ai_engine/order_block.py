from dataclasses import dataclass, asdict
from typing import Any

from .candle import CandleData


@dataclass(frozen=True)
class OBZone:
    index: int
    direction: str
    zone_low: float
    zone_high: float
    state: str
    high_quality: bool
    fib_confluence: bool = False
    fib_levels: tuple[float, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OrderBlockEngine:
    STATES = ("VIRGIN", "TOUCHED", "RETESTED", "INVALIDATED")

    @staticmethod
    def _is_high_quality(direction: str, trend_context: dict[str, Any]) -> bool:
        return direction == trend_context.get("direction")

    @staticmethod
    def _state(candle: CandleData, candles: list[CandleData], direction: str) -> str:
        body_low = min(candle.open, candle.close)
        body_high = max(candle.open, candle.close)
        touched = 0
        for future in candles[candles.index(candle) + 1:]:
            if future.low <= body_high and future.high >= body_low:
                touched += 1
        if touched == 0:
            return "VIRGIN"
        if touched == 1:
            return "TOUCHED"
        return "RETESTED"

    @staticmethod
    def _invalidated(zone_low: float, zone_high: float, candles: list[CandleData], direction: str) -> bool:
        for c in candles:
            if direction == "BULLISH" and c.close < zone_low:
                return True
            if direction == "BEARISH" and c.close > zone_high:
                return True
        return False

    def detect(self, candles: list[CandleData], current_index: int, trend_context: dict[str, Any], timeframe: str) -> dict[str, Any]:
        visible = candles[: min(current_index, len(candles) - 1) + 1]
        direction = trend_context.get("direction", "SIDEWAYS")
        zones: list[OBZone] = []
        for i, c in enumerate(visible):
            body_low = min(c.open, c.close)
            body_high = max(c.open, c.close)
            if direction == "BULLISH" and c.close < c.open:
                zone_direction = "BULLISH"
            elif direction == "BEARISH" and c.close > c.open:
                zone_direction = "BEARISH"
            else:
                continue
            state = "VIRGIN"
            touches = 0
            for later in visible[i + 1:]:
                if later.low <= body_high and later.high >= body_low:
                    touches += 1
            if touches == 1:
                state = "TOUCHED"
            elif touches >= 2:
                state = "RETESTED"
            if self._invalidated(body_low, body_high, visible[i + 1:], zone_direction):
                state = "INVALIDATED"
            zones.append(OBZone(i, zone_direction, body_low, body_high, state, self._is_high_quality(zone_direction, trend_context)))
        ranked = sorted(zones, key=lambda z: (z.high_quality, z.state != "INVALIDATED", -z.index), reverse=True)
        return {"timeframe": timeframe, "zones": [z.to_dict() for z in ranked], "priority": ranked[0].to_dict() if ranked else None}
