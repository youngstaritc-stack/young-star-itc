from dataclasses import dataclass
from typing import Any, Dict, List

from .candle import CandleData


@dataclass
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
    fib_levels: List[str] = None
    ob_id: str = ""

    def __post_init__(self):
        if self.fib_levels is None:
            self.fib_levels = []


class OrderBlockEngine:
    """Part 4: Order Block detection and state only."""

    def detect(self, candles: List[CandleData], current_index: int, trend_context: Dict[str, Any], timeframe: str) -> List[OBZone]:
        visible = candles[: min(current_index, len(candles) - 1) + 1] if candles and current_index >= 0 else []
        if len(visible) < 3:
            return []
        direction = trend_context.get("direction", "SIDEWAYS")
        obs: List[OBZone] = []
        for i in range(1, len(visible) - 1):
            base = visible[i]
            next_c = visible[i + 1]
            prior = visible[i - 1]
            body_low, body_high = sorted((base.open, base.close))
            if base.close < base.open and next_c.close > prior.high:
                obs.append(self._zone(body_low, body_high, "BULLISH", i, visible, direction, timeframe))
            elif base.close > base.open and next_c.close < prior.low:
                obs.append(self._zone(body_low, body_high, "BEARISH", i, visible, direction, timeframe))
        return self._rank(obs)

    def _zone(self, low: float, high: float, direction: str, formation: int, candles: List[CandleData], trend: str, timeframe: str) -> OBZone:
        state = "VIRGIN"
        for c in candles[formation + 1:]:
            if c.low <= high and c.high >= low:
                state = "TOUCHED"
                if c.low < low or c.high > high:
                    state = "INVALIDATED"
        if state == "TOUCHED":
            hits = sum(c.low <= high and c.high >= low for c in candles[formation + 1:])
            if hits > 1:
                state = "RETESTED"
        return OBZone(low, high, direction, state, formation, len(candles) - 1, abs(candles[-1].close - (low + high) / 2), len(candles) - 1 - formation, direction == trend, [], f"OB-{timeframe}-{formation}")

    @staticmethod
    def _rank(obs: List[OBZone]) -> List[OBZone]:
        return sorted(obs, key=lambda x: (x.direction == "BULLISH", x.fib_confluence, -x.distance, -x.age), reverse=True)
