from ai_engine.candle import CandleData
from ai_engine.analysis_pipeline import AnalysisPipeline
from ai_engine.trend_engine import TrendEngine
from ai_engine.fibonacci import FibonacciEngine
from ai_engine.order_block import OBZone, OrderBlockEngine
from ai_engine.channel import ChannelEngine
from ai_engine.fvg import FVGEngine
from ai_engine.liquidity import LiquidityEngine


def candles(values):
    return [CandleData(i, *v) for i, v in enumerate(values)]


def sample():
    return candles([
        (10, 11, 9, 10.5),
        (10.5, 12, 10, 11.5),
        (11.5, 13, 11, 12.5),
        (12.5, 14, 12, 13.5),
        (13.5, 15, 13, 14.5),
        (14.5, 16, 14, 15.5),
        (15.5, 17, 15, 16.5),
    ])


def test_part1_boundary_and_schema():
    result = TrendEngine().detect_market_structure(sample(), 3)
    assert set(result) == {
        "direction", "confidence", "structure", "swing_highs", "swing_lows",
        "trend_change_detected", "trend_start_confirmed", "is_sideways",
    }
    assert all(s["index"] <= 3 for s in result["swing_highs"] + result["swing_lows"])


def test_part2_schema_without_future_data():
    result = FibonacciEngine().analyze(sample(), "15M")
    assert result["timeframe"] == "15M"
    assert set(result) >= {"levels", "virgin_levels", "priority_level", "swing_high", "swing_low"}


def test_part3_empty_extension_is_safe():
    result = FibonacciEngine().analyze_extension(sample(), "15M", {})
    assert result["point_c"] is None
    assert result["tp_always"] is None
    assert result["final_target"] is None


def test_part4_returns_obzone_list():
    result = OrderBlockEngine().detect(sample(), len(sample()) - 1, {"direction": "BULLISH"}, "15M")
    assert isinstance(result, list)
    assert all(isinstance(zone, OBZone) for zone in result)


def test_part5_sideways_fallback():
    result = ChannelEngine().detect(sample(), len(sample()) - 1, {"direction": "SIDEWAYS"}, "15M")
    assert result["direction"] == "SIDEWAYS"
    assert result["slope"] == 0.0


def test_part6_fvg_schema():
    result = FVGEngine().detect(sample(), len(sample()) - 1, {"direction": "BULLISH"}, "15M")
    assert result["timeframe"] == "15M"
    assert "zones" in result and "priority" in result


def test_part7_liquidity_schema_and_lookback():
    result = LiquidityEngine().detect(sample(), len(sample()) - 1, {"direction": "BULLISH", "swing_highs": [], "swing_lows": []}, "15M")
    assert result["timeframe"] == "15M"
    assert result["levels"] == []


def test_pipeline_returns_all_parts_1_7():
    result = AnalysisPipeline().analyze(sample(), len(sample()) - 1, "15M")
    assert set(result) == {
        "trend", "fibonacci", "fibonacci_extension", "order_blocks",
        "parallel_channel", "fvg", "liquidity",
    }
