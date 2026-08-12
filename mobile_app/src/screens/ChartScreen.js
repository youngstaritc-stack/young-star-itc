import React, { useState, useEffect } from 'react';

// YOUNG STAR ITC — Dedicated Chart Module (Live API Integration)
const ChartScreen = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('Gold');
  const [selectedTimeframe, setSelectedTimeframe] = useState('15M');
  const [chartData, setChartData] = useState(null);
  const [analysisState, setAnalysisState] = useState(null);
  const [loading, setLoading] = useState(true);

  const [activeOverlays, setActiveOverlays] = useState({
    trend: true,
    fibonacci: true,
    orderBlock: true,
    parallelChannel: true,
    volume: true,
    lqFvg: true,
    historicalMatch: false
  });

  const symbols = ['Gold', 'Silver', 'AUD/USD'];
  const timeframes = ['1D', '4H', '2H', '1H', '45M', '30M', '15M', '5M', '1M'];

  useEffect(() => {
    fetchData();
  }, [selectedSymbol, selectedTimeframe]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [chartRes, analysisRes] = await Promise.all([
        fetch(`http://127.0.0.1:8000/api/chart/data?symbol=${selectedSymbol}&timeframe=${selectedTimeframe}`),
        fetch(`http://127.0.0.1:8000/api/analysis/state?symbol=${selectedSymbol}&timeframe=${selectedTimeframe}`)
      ]);
      const chartJson = await chartRes.json();
      const analysisJson = await analysisRes.json();
      setChartData(chartJson);
      setAnalysisState(analysisJson);
    } catch (err) {
      console.error("API Fetch Error:", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleOverlay = (layer) => {
    setActiveOverlays(prev => ({ ...prev, [layer]: !prev[layer] }));
  };

  return (
    <div style={{ backgroundColor: '#070B14', color: '#FFFFFF', minHeight: '100vh', padding: '16px', fontFamily: 'sans-serif' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2 style={{ margin: 0, fontSize: '18px', color: '#E0E0E0' }}>YOUNG STAR ITC — CHART</h2>
        <span style={{ fontSize: '12px', padding: '4px 8px', borderRadius: '4px', backgroundColor: '#1A2332', color: '#00E676' }}>
          Engine: Young Star Volume Engine
        </span>
      </div>

      {/* Symbol Selector */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', overflowX: 'auto' }}>
        {symbols.map(symbol => (
          <button
            key={symbol}
            onClick={() => setSelectedSymbol(symbol)}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: selectedSymbol === symbol ? '#2962FF' : '#131722',
              color: '#FFF',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            {symbol}
          </button>
        ))}
      </div>

      {/* Timeframe Selector */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '16px', overflowX: 'auto' }}>
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
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            {tf}
          </button>
        ))}
      </div>

      {/* Chart Canvas Area */}
      <div style={{
        height: '320px',
        backgroundColor: '#131722',
        borderRadius: '8px',
        border: '1px solid #2A2E39',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: '16px',
        position: 'relative'
      }}>
        {loading ? (
          <div style={{ color: '#787B86' }}>Loading Market Data...</div>
        ) : (
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: '#E0E0E0', fontSize: '16px', fontWeight: 'bold' }}>
              {chartData?.symbol} ({chartData?.timeframe})
            </div>
            <div style={{ color: '#00E676', fontSize: '14px', marginTop: '4px' }}>
              Candles Loaded: {chartData?.candles?.length || 0}
            </div>
            <div style={{ color: '#FFD700', fontSize: '12px', marginTop: '8px' }}>
              Signal State: {analysisState?.signal_state || 'N/A'}
            </div>
          </div>
        )}

        {/* AI Boundary Tag */}
        <div style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          backgroundColor: 'rgba(41, 98, 255, 0.2)',
          border: '1px solid #2962FF',
          padding: '4px 10px',
          borderRadius: '4px',
          fontSize: '11px',
          color: '#2962FF'
        }}>
          {analysisState?.ai_boundary || 'BEFORE_ENTRY_INFORMATIONAL'}
        </div>
      </div>

      {/* Overlays Toggle */}
      <div>
        <div style={{ fontSize: '13px', color: '#787B86', marginBottom: '8px' }}>CHART OVERLAYS</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {Object.keys(activeOverlays).map(layer => (
            <button
              key={layer}
              onClick={() => toggleOverlay(layer)}
              style={{
                padding: '6px 10px',
                borderRadius: '4px',
                border: 'none',
                backgroundColor: activeOverlays[layer] ? '#1E222D' : '#131722',
                color: activeOverlays[layer] ? '#00E676' : '#787B86',
                fontSize: '12px',
                cursor: 'pointer'
              }}
            >
              {layer.toUpperCase()} {activeOverlays[layer] ? '✓' : ''}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChartScreen;
