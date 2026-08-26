from dataclasses import dataclass, asdict
from typing import Any

from .candle import CandleData


@dataclass(frozen=True)
class OBZone:
    zone_low: float
    zone_high: float
    direction: str
    state: str
    formation_index: int
    last_processed_index: int
    distance: float
    age: int
    fib_confluence: bool = False
    fib_levels: tuple[float, ...] = ()
    ob_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OrderBlockEngine:
    """Part 4: Rule Book OB detection/state/priority only."""

    STATES = ("VIRGIN", "TOUCHED", "RETESTED", "INVALIDATED")

    @staticmethod
    def _is_formation(candles: list[CandleData], i: int, direction: str) -> bool:
        if i + 1 >= len(candles):
            return False
        c = candles[i]
        nxt = candles[i + 1]
        if direction == "BULLISH":
            return c.close < c.open and nxt.close > c.high
        if direction == "BEARISH":
            return c.close > c.open and nxt.close < c.low
        return False

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
        if trend not in {"BULLISH", "BEARISH"}:
            return {"timeframe": timeframe, "zones": [], "priority": None}

        zones: list[OBZone] = []
        last_index = len(visible) - 1
        for i in range(len(visible) - 1):
            if not self._is_formation(visible, i, trend):
                continue
            c = visible[i]
            low = min(c.open, c.close)
            high = max(c.open, c.close)
            state = self._state(visible, i, low, high, trend)
            zones.append(OBZone(
                zone_low=low,
                zone_high=high,
                direction=trend,
                state=state,
                formation_index=i,
                last_processed_index=last_index,
                distance=0.0,
                age=last_index - i,
                ob_id=f"{timeframe}:{trend}:{i}",
            ))

        zones.sort(key=lambda z: (z.state != "INVALIDATED", z.age * -1), reverse=True)
        return {
            "timeframe": timeframe,
            "zones": [z.to_dict() for z in zones],
            "priority": zones[0].to_dict() if zones else None,
        }
