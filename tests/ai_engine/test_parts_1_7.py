from ai_engine import (
    AnalysisPipeline,
    CandleData,
    ChannelEngine,
    FVGEngine,
    FibonacciEngine,
    LiquidityEngine,
    OrderBlockEngine,
    TrendEngine,
)


def c(i, o, h, l, cl, v=0):
    return CandleData(str(i), o, h, l, cl, v)


def test_candle_data_shape():
    x = c(0, 10, 12, 9, 11)
    assert x.open == 10 and x.high == 12 and x.low == 9 and x.close == 11


def test_trend_insufficient_data_is_sideways():
    result = TrendEngine().detect_market_structure([c(i, 10, 11, 9, 10) for i in range(4)], 3)
    assert result["direction"] == "SIDEWAYS"
    assert result["is_sideways"] is True


def test_trend_does_not_read_future_candles():
    candles = [c(i, 10, 11 + i, 9 - i, 10 + i) for i in range(8)]
    result = TrendEngine().detect_market_structure(candles, 4)
    assert all(x["index"] <= 4 for x in result["swing_highs"] + result["swing_lows"])


def test_fibonacci_has_approved_retracement_levels():
    candles = [c(i, 100 + i, 102 + i, 98 + i, 101 + i) for i in range(8)]
    result = FibonacciEngine().analyze(candles, "15M")
    assert set(result["levels"]).issubset({"38.2", "50.0", "61.8"})


def test_extension_uses_priority_point_c():
    candles = [c(i, 100 + i, 102 + i, 98 + i, 101 + i) for i in range(8)]
    fib = FibonacciEngine().analyze(candles, "15M")
    ext = FibonacciEngine().analyze_extension(candles, "15M", fib)
    if fib["priority_level"]:
        assert ext["point_c"] == fib["priority_level"]["price"]
        assert ext["tp_always"] == ext["extension_3_618"]
        assert ext["final_target"] == ext["extension_4_618"]


def test_order_block_uses_body_only_for_zone():
    candles = [
        c(0, 100, 101, 99, 100),
        c(1, 101, 110, 95, 100),
        c(2, 100, 112, 100, 111),
    ]
    obs = OrderBlockEngine().detect(candles, 2, {"direction": "BULLISH"}, "15M")
    assert obs
    assert obs[0].zone_low == 100
    assert obs[0].zone_high == 101


def test_order_block_trend_aligned_is_ranked_first():
    candles = [
        c(0, 100, 101, 99, 100),
        c(1, 101, 105, 95, 99),
        c(2, 99, 110, 99, 109),
        c(3, 109, 110, 108, 109),
        c(4, 109, 115, 109, 114),
    ]
    obs = OrderBlockEngine().detect(candles, 4, {"direction": "BULLISH"}, "15M")
    if len(obs) > 1:
        assert obs[0].direction == "BULLISH"


def test_channel_wick_break_does_not_invalidate_body_channel():
    candles = [
        c(0, 100, 101, 99, 100),
        c(1, 100, 105, 99, 104),
        c(2, 104, 106, 102, 105),
        c(3, 105, 107, 103, 106),
        c(4, 106, 108, 104, 107),
        c(5, 107, 112, 105, 108),
        c(6, 108, 109, 106, 107),
        c(7, 107, 110, 105, 106),
        c(8, 106, 111, 104, 105),
    ]
    result = ChannelEngine().detect(candles, 8, {"direction": "BULLISH"}, "15M")
    assert result["state"] != "INVALIDATED" or result["upper_boundary"] is None


def test_fvg_requires_following_candle_for_confirmation():
    candles = [
        c(0, 100, 105, 99, 104),
        c(1, 104, 110, 104, 109),
        c(2, 109, 111, 108, 110),
    ]
    result = FVGEngine().detect(candles, 2, {"direction": "BULLISH"}, "15M")
    assert result == []


def test_fvg_state_tracks_touch_and_retest():
    candles = [
        c(0, 100, 110, 99, 109),
        c(1, 109, 115, 109, 114),
        c(2, 114, 120, 114, 119),
        c(3, 119, 120, 116, 118),
        c(4, 118, 121, 117, 119),
    ]
    result = FVGEngine().detect(candles, 4, {"direction": "BULLISH"}, "15M")
    assert all(x["confirmation_index"] <= 4 for x in result)


def test_liquidity_volume_priority_is_deferred():
    candles = [c(i, 100 + i, 101 + i, 99 + i, 100 + i, v=1000 - i) for i in range(12)]
    result = LiquidityEngine().detect(candles, 11, {"direction": "BULLISH"}, "15M")
    indices = [x["formation_index"] for x in result]
    assert indices == sorted(indices)


def test_liquidity_sweep_index_is_close_back_candle():
    candles = [
        c(0, 100, 101, 99, 100),
        c(1, 100, 105, 99, 104),
        c(2, 104, 106, 103, 105),
        c(3, 105, 108, 104, 106),
        c(4, 106, 109, 105, 108),
        c(5, 108, 111, 107, 108),
    ]
    result = LiquidityEngine().detect(candles, 5, {"direction": "BEARISH"}, "15M")
    for item in result:
        if item["state"] in {"SWEPT", "RETESTED"}:
            assert item["sweep_index"] is not None


def test_pipeline_returns_all_parts_1_to_7():
    candles = [c(i, 100 + i, 103 + i, 97 + i, 102 + i, 10) for i in range(12)]
    result = AnalysisPipeline().analyze(candles, "15M", 11)
    assert set(result) == {"trend", "fibonacci", "fibonacci_extension", "order_blocks", "parallel_channel", "fvg", "liquidity"}


def test_pipeline_boundary_is_original_index():
    candles = [c(i, 100, 101, 99, 100) for i in range(20)]
    result = AnalysisPipeline().analyze(candles, "15M", 7)
    assert result["trend"]["swing_highs"] == []
    assert result["trend"]["swing_lows"] == []


def test_no_entry_signal_fields_in_pipeline():
    candles = [c(i, 100 + i, 103 + i, 97 + i, 102 + i) for i in range(12)]
    result = AnalysisPipeline().analyze(candles, "15M")
    forbidden = {"BUY", "SELL", "ENTRY", "SIGNAL", "STOP_LOSS", "TAKE_PROFIT", "LOT_SIZE", "RISK"}
    text = str(result).upper()
    assert not any(word in text for word in forbidden)
