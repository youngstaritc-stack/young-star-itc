from typing import Any

from .candle import CandleData
from .channel import ChannelEngine
from .fibonacci import FibonacciEngine
from .fvg import FVGEngine
from .liquidity import LiquidityEngine
from .order_block import OBZone, OrderBlockEngine
from .trend_engine import TrendEngine


class AnalysisPipeline:
    """Parts 1-7 orchestrator only. No entry, signal, SL/TP, risk or lot logic."""

    def __init__(self) -> None:
        self.trend_engine = TrendEngine()
        self.fibonacci_engine = FibonacciEngine()
        self.order_block_engine = OrderBlockEngine()
        self.channel_engine = ChannelEngine()
        self.fvg_engine = FVGEngine()
        self.liquidity_engine = LiquidityEngine()

    @staticmethod
    def _attach_ob_fib_confluence(
        zones: list[OBZone], fib_result: dict[str, Any]
    ) -> list[OBZone]:
        prices = tuple(
            float(level["price"])
            for level in fib_result.get("levels", {}).values()
            if isinstance(level, dict) and "price" in level
        )
        enriched: list[OBZone] = []
        for zone in zones:
            matched = tuple(price for price in prices if zone.zone_low <= price <= zone.zone_high)
            enriched.append(
                OBZone(
                    zone_low=zone.zone_low,
                    zone_high=zone.zone_high,
                    direction=zone.direction,
                    state=zone.state,
                    formation_index=zone.formation_index,
                    last_processed_index=zone.last_processed_index,
                    distance=zone.distance,
                    age=zone.age,
                    fib_confluence=bool(matched),
                    fib_levels=matched,
                    ob_id=zone.ob_id,
                )
            )
        return enriched

    def analyze(
        self,
        candles: list[CandleData],
        current_index: int,
        timeframe: str,
    ) -> dict[str, Any]:
        empty = {
            "trend": {},
            "fibonacci": {},
            "fibonacci_extension": {},
            "order_blocks": [],
            "parallel_channel": {},
            "fvg": {},
            "liquidity": {},
        }
        if not candles or current_index < 0:
            return empty

        end = min(current_index, len(candles) - 1)
        # Slicing is the only visibility boundary. Candle indices remain in the
        # original coordinate system because the slice always starts at index 0.
        visible = candles[: end + 1]
        visible_index = len(visible) - 1

        trend = self.trend_engine.detect_market_structure(visible, visible_index)
        trend_context = trend
        fib = self.fibonacci_engine.analyze(visible, timeframe)
        extension = self.fibonacci_engine.analyze_extension(visible, timeframe, fib)

        ob_zones = self.order_block_engine.detect(
            visible, visible_index, trend_context, timeframe
        )
        ob_zones = self._attach_ob_fib_confluence(ob_zones, fib)

        channel = self.channel_engine.detect(visible, visible_index, trend_context, timeframe)
        fvg = self.fvg_engine.detect(visible, visible_index, trend_context, timeframe)
        liquidity = self.liquidity_engine.detect(visible, visible_index, trend_context, timeframe)

        return {
            "trend": trend,
            "fibonacci": fib,
            "fibonacci_extension": extension,
            "order_blocks": [zone.to_dict() for zone in ob_zones],
            "parallel_channel": channel,
            "fvg": fvg,
            "liquidity": liquidity,
        }


def analyze(candles: list[CandleData], current_index: int, timeframe: str) -> dict[str, Any]:
    return AnalysisPipeline().analyze(candles, current_index, timeframe)
