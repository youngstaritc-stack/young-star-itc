from dataclasses import dataclass, asdict
from typing import Any

from .candle import CandleData


@dataclass(frozen=True)
class LiquidityLevel:
    index: int
    kind: str
    price: float
    state: str
    sweep_index: int | None
    trend_alignment: str
    confluence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LiquidityEngine:
    def _is_sweep_completed(self, candles: list[CandleData], level: float, kind: str, start: int) -> int | None:
        broken = False
        for i in range(start, len(candles)):
            c = candles[i]
            if kind == "HIGH" and c.high > level:
                broken = True
            elif kind == "LOW" and c.low < level:
                broken = True
            if broken:
                if kind == "HIGH" and c.close <= level:
                    return i
                if kind == "LOW" and c.close >= level:
                    return i
        return None

    @staticmethod
    def _is_retested(candle: CandleData, level: float) -> bool:
        return candle.low <= level <= candle.high

    def detect(self, candles: list[CandleData], current_index: int, trend_context: dict[str, Any], timeframe: str) -> dict[str, Any]:
        visible = candles[: min(current_index, len(candles) - 1) + 1]
        highs = trend_context.get("swing_highs", [])
        lows = trend_context.get("swing_lows", [])
        trend = trend_context.get("direction", "SIDEWAYS")
        levels: list[LiquidityLevel] = []
        for item in highs + lows:
            kind = "HIGH" if item in highs else "LOW"
            price = item["price"]
            sweep_index = self._is_sweep_completed(visible, price, kind, item["index"] + 1)
            state = "VIRGIN"
            if sweep_index is not None:
                state = "SWEPT"
                if any(self._is_retested(c, price) for c in visible[sweep_index + 1:]):
                    state = "RETESTED"
            alignment = "ALIGNED" if ((kind == "LOW" and trend == "BULLISH") or (kind == "HIGH" and trend == "BEARISH")) else "NOT_ALIGNED"
            levels.append(LiquidityLevel(item["index"], kind, price, state, sweep_index, alignment, {}))
        return {"timeframe": timeframe, "levels": [l.to_dict() for l in levels], "priority": levels[-1].to_dict() if levels else None}
