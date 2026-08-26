from dataclasses import dataclass, asdict
from typing import Any

from .candle import CandleData


LIQUIDITY_SWEEP_LOOKBACK = 10  # implementation default; not a Rule Book threshold


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
    """Part 7: swing liquidity, completed sweeps and retests only."""

    @staticmethod
    def _is_sweep_completed(
        candles: list[CandleData], level: float, kind: str, start: int
    ) -> int | None:
        broken = False
        for i in range(max(0, start), len(candles)):
            candle = candles[i]
            if kind == "HIGH" and candle.high > level:
                broken = True
            elif kind == "LOW" and candle.low < level:
                broken = True
            if broken:
                if kind == "HIGH" and candle.close <= level:
                    return i
                if kind == "LOW" and candle.close >= level:
                    return i
        return None

    @staticmethod
    def _is_retested(candle: CandleData, level: float) -> bool:
        return candle.low <= level <= candle.high

    @staticmethod
    def _has_new_swing_outside(
        item: dict[str, Any], later_swings: list[dict[str, Any]], kind: str
    ) -> bool:
        for swing in later_swings:
            if swing["index"] <= item["index"]:
                continue
            if kind == "HIGH" and swing["price"] > item["price"]:
                return True
            if kind == "LOW" and swing["price"] < item["price"]:
                return True
        return False

    def detect(
        self,
        candles: list[CandleData],
        current_index: int,
        trend_context: dict[str, Any],
        timeframe: str,
    ) -> dict[str, Any]:
        if not candles or current_index < 0:
            return {"timeframe": timeframe, "levels": [], "priority": None}

        end = min(current_index, len(candles) - 1)
        visible = candles[: end + 1]
        highs = trend_context.get("swing_highs", [])[-LIQUIDITY_SWEEP_LOOKBACK:]
        lows = trend_context.get("swing_lows", [])[-LIQUIDITY_SWEEP_LOOKBACK:]
        trend = trend_context.get("direction", "SIDEWAYS")
        levels: list[LiquidityLevel] = []

        for item in highs:
            price = float(item["price"])
            sweep_index = self._is_sweep_completed(visible, price, "HIGH", item["index"] + 1)
            state = "SWEPT" if sweep_index is not None else "VIRGIN"
            if sweep_index is not None and any(
                self._is_retested(candle, price) for candle in visible[sweep_index + 1:]
            ):
                state = "RETESTED"
            if self._has_new_swing_outside(item, highs, "HIGH"):
                state = "INVALIDATED"
            alignment = "ALIGNED" if trend == "BEARISH" else "NOT_ALIGNED"
            levels.append(LiquidityLevel(item["index"], "HIGH", price, state, sweep_index, alignment, {}))

        for item in lows:
            price = float(item["price"])
            sweep_index = self._is_sweep_completed(visible, price, "LOW", item["index"] + 1)
            state = "SWEPT" if sweep_index is not None else "VIRGIN"
            if sweep_index is not None and any(
                self._is_retested(candle, price) for candle in visible[sweep_index + 1:]
            ):
                state = "RETESTED"
            if self._has_new_swing_outside(item, lows, "LOW"):
                state = "INVALIDATED"
            alignment = "ALIGNED" if trend == "BULLISH" else "NOT_ALIGNED"
            levels.append(LiquidityLevel(item["index"], "LOW", price, state, sweep_index, alignment, {}))

        levels.sort(key=lambda level: level.index, reverse=True)
        return {
            "timeframe": timeframe,
            "levels": [level.to_dict() for level in levels],
            "priority": levels[0].to_dict() if levels else None,
        }
