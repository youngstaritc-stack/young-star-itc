import React, { useState, useEffect } from 'react';

// YOUNG STAR ITC — Advanced Interactive Chart Module
const ChartScreen = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('Gold');
  const [selectedTimeframe, setSelectedTimeframe] = useState('15M');
  const [candles, setCandles] = useState([]);
  const [loading, setLoading] = useState(true);

  const symbols = ['Gold', 'Silver', 'AUD/USD'];
  const timeframes = ['1D', '4H', '2H', '1H', '45M', '30M', '15M', '5M', '1M'];

  useEffect(() => {
    fetchChartData();
  }, [selectedSymbol, selectedTimeframe]);

  const fetchChartData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/chart/data?symbol=${selectedSymbol}&timeframe=${selectedTimeframe}`);
      const data = await res.json();
      setCandles(data.candles || []);
    } catch (err) {
      console.error("Chart API Fetch Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#070B14', color: '#FFFFFF', minHeight: '100vh', padding: '16px', fontFamily: 'sans-serif' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '18px', color: '#FFF' }}>{selectedSymbol} CHART</h2>
          <span style={{ fontSize: '11px', color: '#787B86' }}>YOUNG STAR VOLUME ENGINE OVERLAY</span>
        </div>
      </div>

      {/* Symbol Selector */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
        {symbols.map(s => (
          <button
            key={s}
            onClick={() => setSelectedSymbol(s)}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: selectedSymbol === s ? '#2962FF' : '#131722',
              color: '#FFF',
              fontWeight: 'bold',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Timeframe Selector Bar */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '16px', overflowX: 'auto', paddingBottom: '4px' }}>
        {timeframes.map(tf => (
          <button
            key={tf}
            onClick={() => setSelectedTimeframe(tf)}
            style={{
              padding: '4px 8px',
              borderRadius: '4px',
              border: '1px solid #2A2E39',
              backgroundColor: selectedTimeframe === tf ? '#1E222D' : 'transparent',
              color: selectedTimeframe === tf ? '#2962FF' : '#B2B5BE',
              fontSize: '11px',
              cursor: 'pointer'
            }}
          >
            {tf}
          </button>
        ))}
      </div>

      {/* Main Candlestick & Volume Canvas Display Area */}
      <div style={{ backgroundColor: '#131722', borderRadius: '12px', padding: '16px', border: '1px solid #2A2E39', marginBottom: '16px', minHeight: '320px' }}>
        {loading ? (
          <div style={{ color: '#787B86', textAlign: 'center', marginTop: '120px' }}>Loading Candlestick Data...</div>
        ) : (
          <div>
            <div style={{ fontSize: '12px', color: '#787B86', marginBottom: '12px', display: 'flex', justifyContent: 'space-between' }}>
              <span>OHLC & VOLUME STREAM ({selectedTimeframe})</span>
              <span style={{ color: '#00E676' }}>● LIVE</span>
            </div>

            {/* Candlestick Visualization */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {candles.map((candle, idx) => {
                const isBull = candle.close >= candle.open;
                const color = isBull ? '#00E676' : '#FF5252';
                return (
                  <div key={idx} style={{ backgroundColor: '#070B14', padding: '10px', borderRadius: '6px', borderLeft: `4px solid ${color}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 'bold' }}>
                      <span>{candle.time}</span>
                      <span style={{ color }}>Close: {candle.close}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#787B86', marginTop: '4px' }}>
                      <span>O: {candle.open} | H: {candle.high} | L: {candle.low}</span>
                      <span style={{ color: '#2962FF' }}>Vol: {candle.volume}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChartScreen;
