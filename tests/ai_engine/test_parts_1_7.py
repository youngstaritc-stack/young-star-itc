from ai_engine import AnalysisPipeline, CandleData, FibonacciEngine, TrendEngine


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
    candles = [c(i, 100+i, 102+i, 98+i, 101+i) for i in range(8)]
    result = FibonacciEngine().analyze(candles, "15M")
    assert set(result["levels"]).issubset({"38.2", "50.0", "61.8"})


def test_extension_uses_priority_point_c():
    candles = [c(i, 100+i, 102+i, 98+i, 101+i) for i in range(8)]
    fib = FibonacciEngine().analyze(candles, "15M")
    ext = FibonacciEngine().analyze_extension(candles, "15M", fib)
    if fib["priority_level"]:
        assert ext["point_c"] == fib["priority_level"]["price"]
        assert ext["tp_always"] == ext["extension_3_618"]
        assert ext["final_target"] == ext["extension_4_618"]


def test_pipeline_returns_all_parts_1_to_7():
    candles = [c(i, 100+i, 103+i, 97+i, 102+i, 10) for i in range(12)]
    result = AnalysisPipeline().analyze(candles, "15M", 11)
    assert set(result) == {"trend", "fibonacci", "fibonacci_extension", "order_blocks", "parallel_channel", "fvg", "liquidity"}


def test_pipeline_boundary_is_original_index():
    candles = [c(i, 100, 101, 99, 100) for i in range(20)]
    result = AnalysisPipeline().analyze(candles, "15M", 7)
    assert result["trend"]["swing_highs"] == []
    assert result["trend"]["swing_lows"] == []


def test_no_entry_signal_fields_in_pipeline():
    candles = [c(i, 100+i, 103+i, 97+i, 102+i) for i in range(12)]
    result = AnalysisPipeline().analyze(candles, "15M")
    forbidden = {"BUY", "SELL", "ENTRY", "SIGNAL", "STOP_LOSS", "TAKE_PROFIT", "LOT_SIZE", "RISK"}
    assert not any(str(value).upper() in forbidden for value in result.values())
