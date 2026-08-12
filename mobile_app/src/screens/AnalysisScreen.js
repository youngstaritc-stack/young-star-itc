import React, { useState, useEffect } from 'react';

// YOUNG STAR ITC — Analysis Screen Module (Live API Integrated)
const AnalysisScreen = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('Gold');
  const [selectedTimeframe, setSelectedTimeframe] = useState('15M');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  const symbols = ['Gold', 'Silver', 'AUD/USD'];
  const timeframes = ['1D', '4H', '2H', '1H', '45M', '30M', '15M', '5M', '1M'];

  useEffect(() => {
    fetchAnalysisData();
  }, [selectedSymbol, selectedTimeframe]);

  const fetchAnalysisData = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/analysis/state?symbol=${selectedSymbol}&timeframe=${selectedTimeframe}`);
      const data = await res.json();
      setAnalysisData(data);
    } catch (err) {
      console.error("Analysis API Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#070B14', color: '#FFFFFF', minHeight: '100vh', padding: '16px', fontFamily: 'sans-serif' }}>
      {/* Header */}
      <div style={{ marginBottom: '16px' }}>
        <h2 style={{ margin: 0, fontSize: '20px', color: '#FFF' }}>ANALYSIS & PREDICTION</h2>
        <span style={{ fontSize: '11px', color: '#787B86' }}>YOUNG STAR VOLUME ENGINE DATA CONTRACT</span>
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

      {/* Analysis Details Card */}
      <div style={{ backgroundColor: '#131722', borderRadius: '12px', padding: '16px', border: '1px solid #2A2E39', marginBottom: '16px' }}>
        {loading ? (
          <div style={{ color: '#787B86' }}>Loading Analysis Data...</div>
        ) : (
          <div>
            {/* Signal State */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ fontSize: '13px', color: '#787B86' }}>SIGNAL STATE</span>
              <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#FFD700', backgroundColor: '#1E222D', padding: '4px 10px', borderRadius: '4px' }}>
                {analysisData?.signal_state || 'N/A'}
              </span>
            </div>

            {/* Historical Match */}
            <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#070B14', borderRadius: '8px', border: '1px solid #2A2E39' }}>
              <div style={{ fontSize: '12px', color: '#787B86', marginBottom: '4px' }}>HISTORICAL MATCH SCORE</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#00E676' }}>
                {analysisData?.historical_match?.score || 0}%
              </div>
              <div style={{ fontSize: '12px', color: '#B2B5BE', marginTop: '4px' }}>
                Evidence: {analysisData?.historical_match?.evidence || 'N/A'}
              </div>
            </div>

            {/* AI Boundary Notification */}
            <div style={{ padding: '12px', backgroundColor: 'rgba(41, 98, 255, 0.1)', border: '1px solid #2962FF', borderRadius: '8px' }}>
              <div style={{ fontSize: '11px', color: '#2962FF', fontWeight: 'bold', marginBottom: '2px' }}>AI BOUNDARY</div>
              <div style={{ fontSize: '13px', color: '#FFF' }}>
                {analysisData?.ai_boundary || 'BEFORE_ENTRY_INFORMATIONAL_ONLY'}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisScreen;
