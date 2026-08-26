from typing import Any

from .candle import CandleData
from .channel import ChannelEngine
from .fibonacci import FibonacciEngine
from .fvg import FVGEngine
from .liquidity import LiquidityEngine
from .order_block import OrderBlockEngine
from .trend_engine import TrendEngine


class AnalysisPipeline:
    def __init__(self) -> None:
        self.trend_engine = TrendEngine()
        self.fibonacci_engine = FibonacciEngine()
        self.order_block_engine = OrderBlockEngine()
        self.channel_engine = ChannelEngine()
        self.fvg_engine = FVGEngine()
        self.liquidity_engine = LiquidityEngine()

    def analyze(self, candles: list[CandleData], current_index: int, timeframe: str) -> dict[str, Any]:
        if not candles:
            return {"trend": {}, "fibonacci": {}, "extension": {}, "order_block": {}, "channel": {}, "fvg": {}, "liquidity": {}}
        end = min(current_index, len(candles) - 1)
        visible = candles[: end + 1]
        trend = self.trend_engine.detect_market_structure(visible, len(visible) - 1)
        fib = self.fibonacci_engine.analyze(visible, timeframe)
        extension = self.fibonacci_engine.analyze_extension(visible, timeframe, fib)
        return {
            "trend": trend,
            "fibonacci": fib,
            "extension": extension,
            "order_block": self.order_block_engine.detect(visible, len(visible) - 1, trend, timeframe),
            "channel": self.channel_engine.detect(visible, len(visible) - 1, trend, timeframe),
            "fvg": self.fvg_engine.detect(visible, len(visible) - 1, trend, timeframe),
            "liquidity": self.liquidity_engine.detect(visible, len(visible) - 1, trend, timeframe),
        }


def analyze(candles: list[CandleData], current_index: int, timeframe: str) -> dict[str, Any]:
    return AnalysisPipeline().analyze(candles, current_index, timeframe)
