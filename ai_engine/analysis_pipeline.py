from typing import Any, Dict, List, Optional

from .candle import CandleData
from .trend_engine import TrendEngine
from .fibonacci import FibonacciEngine
from .order_block import OrderBlockEngine
from .channel import ChannelEngine
from .fvg import FVGEngine
from .liquidity import LiquidityEngine


class AnalysisPipeline:
    """Part 1-7 orchestration. Informational analysis only; no entry/signal decision."""

    def __init__(self):
        self.trend_engine = TrendEngine()
        self.fib_engine = FibonacciEngine()
        self.ob_engine = OrderBlockEngine()
        self.channel_engine = ChannelEngine()
        self.fvg_engine = FVGEngine()
        self.liquidity_engine = LiquidityEngine()

    def analyze(self, candles: List[CandleData], timeframe: str, current_index: Optional[int] = None) -> Dict[str, Any]:
        if current_index is None:
            current_index = len(candles) - 1
        current_index = max(-1, min(current_index, len(candles) - 1))
        candles_up_to = candles[: current_index + 1] if current_index >= 0 else []

        trend = self.trend_engine.detect_market_structure(candles, current_index)
        trend_context = trend
        fib = self.fib_engine.analyze(candles_up_to, timeframe)
        extension = self.fib_engine.analyze_extension(candles_up_to, timeframe, fib)
        obs = self.ob_engine.detect(candles, current_index, trend_context, timeframe)
        channel = self.channel_engine.detect(candles, current_index, trend_context, timeframe)
        fvg = self.fvg_engine.detect(candles, current_index, trend_context, timeframe)
        liquidity = self.liquidity_engine.detect(candles, current_index, trend_context, timeframe)

        return {
            "trend": trend,
            "fibonacci": fib,
            "fibonacci_extension": extension,
            "order_blocks": obs,
            "parallel_channel": channel,
            "fvg": fvg,
            "liquidity": liquidity,
        }
