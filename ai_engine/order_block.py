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
    """Part 4: Rule Book order-block detection, state and priority only."""

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

    @classmethod
    def _state(cls, candles: list[CandleData], start: int, low: float, high: float, direction: str) -> str:
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

    @staticmethod
    def _is_high_quality(direction: str, trend_context: dict[str, Any]) -> bool:
        return trend_context.get("direction") == direction

    def detect(
        self,
        candles: list[CandleData],
        current_index: int,
        trend_context: dict[str, Any],
        timeframe: str,
    ) -> list[OBZone]:
        if not candles or current_index < 0:
            return []
        end = min(current_index, len(candles) - 1)
        visible = candles[: end + 1]
        trend = trend_context.get("direction", "SIDEWAYS")
        if trend not in {"BULLISH", "BEARISH"}:
            return []

        last_index = len(visible) - 1
        current_price = visible[-1].close
        zones: list[tuple[OBZone, bool]] = []

        for i in range(len(visible) - 1):
            if not self._is_formation(visible, i, trend):
                continue
            candle = visible[i]
            low = min(candle.open, candle.close)
            high = max(candle.open, candle.close)
            state = self._state(visible, i, low, high, trend)
            distance = abs(current_price - ((low + high) / 2.0))
            zone = OBZone(
                zone_low=low,
                zone_high=high,
                direction=trend,
                state=state,
                formation_index=i,
                last_processed_index=last_index,
                distance=distance,
                age=last_index - i,
                ob_id=f"{timeframe}:{trend}:{i}",
            )
            zones.append((zone, self._is_high_quality(trend, trend_context)))

        zones.sort(key=lambda item: (
            item[0].state == "INVALIDATED",
            not item[1],
            item[0].distance,
            -item[0].formation_index,
        ))
        return [zone for zone, _ in zones]
