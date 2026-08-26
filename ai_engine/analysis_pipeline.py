from typing import Any

from .candle import CandleData
from .channel import ChannelEngine
from .fibonacci import FibonacciEngine
from .fvg import FVGEngine
from .liquidity import LiquidityEngine
from .order_block import OrderBlockEngine
from .trend_engine import TrendEngine


class AnalysisPipeline:
    """Part 1-7 orchestrator. No entry/signal/risk decision layer is added."""

    def __init__(self) -> None:
        self.trend_engine = TrendEngine()
        self.fibonacci_engine = FibonacciEngine()
        self.order_block_engine = OrderBlockEngine()
        self.channel_engine = ChannelEngine()
        self.fvg_engine = FVGEngine()
        self.liquidity_engine = LiquidityEngine()

    @staticmethod
    def _attach_ob_fib_confluence(ob_result: dict[str, Any], fib_result: dict[str, Any]) -> dict[str, Any]:
        prices = tuple(
            float(level["price"])
            for level in fib_result.get("levels", {}).values()
            if isinstance(level, dict) and "price" in level
        )
        zones = []
        for zone in ob_result.get("zones", []):
            low = zone["zone_low"]
            high = zone["zone_high"]
            matched = tuple(price for price in prices if low <= price <= high)
            zone = dict(zone)
            zone["fib_confluence"] = bool(matched)
            zone["fib_levels"] = matched
            zones.append(zone)
        result = dict(ob_result)
        result["zones"] = zones
        if zones:
            result["priority"] = zones[0]
        return result

    def analyze(self, candles: list[CandleData], current_index: int, timeframe: str) -> dict[str, Any]:
        if not candles or current_index < 0:
            return {
                "trend": {},
                "fibonacci": {},
                "fibonacci_extension": {},
                "order_blocks": {},
                "parallel_channel": {},
                "fvg": {},
                "liquidity": {},
            }

        end = min(current_index, len(candles) - 1)
        # Keep candle indices in the original coordinate system.
        visible = candles[: end + 1]
        visible_index = len(visible) - 1

        trend = self.trend_engine.detect_market_structure(visible, visible_index)
        trend_context = trend
        fib = self.fibonacci_engine.analyze(visible, timeframe)
        extension = self.fibonacci_engine.analyze_extension(visible, timeframe, fib)

        order_blocks = self.order_block_engine.detect(visible, visible_index, trend_context, timeframe)
        order_blocks = self._attach_ob_fib_confluence(order_blocks, fib)
        channel = self.channel_engine.detect(visible, visible_index, trend_context, timeframe)
        fvg = self.fvg_engine.detect(visible, visible_index, trend_context, timeframe)
        liquidity = self.liquidity_engine.detect(visible, visible_index, trend_context, timeframe)

        return {
            "trend": trend,
            "fibonacci": fib,
            "fibonacci_extension": extension,
            "order_blocks": order_blocks,
            "parallel_channel": channel,
            "fvg": fvg,
            "liquidity": liquidity,
        }


def analyze(candles: list[CandleData], current_index: int, timeframe: str) -> dict[str, Any]:
    return AnalysisPipeline().analyze(candles, current_index, timeframe)
