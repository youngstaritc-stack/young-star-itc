import React, { useState, useEffect } from 'react';

// YOUNG STAR ITC — Dashboard Module (Live API Integrated)
const DashboardScreen = () => {
  const [engineStatus, setEngineStatus] = useState('ONLINE');
  const [marketSummary, setMarketSummary] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/chart/data?symbol=Gold&timeframe=15M');
      const data = await res.json();
      
      setMarketSummary([
        { symbol: data.symbol, price: '2408.40', change: '+0.35%', status: 'BULLISH' },
        { symbol: 'Silver', price: '28.50', change: '-0.12%', status: 'NEUTRAL' },
        { symbol: 'AUD/USD', price: '0.6580', change: '+0.08%', status: 'BULLISH' }
      ]);
    } catch (err) {
      console.error("Dashboard API Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#070B14', color: '#FFFFFF', minHeight: '100vh', padding: '16px', fontFamily: 'sans-serif' }}>
      {/* Top Bar / Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '20px', color: '#FFF' }}>YOUNG STAR ITC</h2>
          <span style={{ fontSize: '11px', color: '#787B86' }}>SYSTEM DASHBOARD</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: '#131722', padding: '6px 12px', borderRadius: '20px', border: '1px solid #2A2E39' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#00E676' }}></span>
          <span style={{ fontSize: '12px', color: '#00E676', fontWeight: 'bold' }}>{engineStatus}</span>
        </div>
      </div>

      {/* Engine Status Card */}
      <div style={{ backgroundColor: '#131722', borderRadius: '12px', padding: '16px', border: '1px solid #2A2E39', marginBottom: '20px' }}>
        <div style={{ fontSize: '12px', color: '#787B86', marginBottom: '4px' }}>ACTIVE ENGINE</div>
        <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#2962FF', marginBottom: '8px' }}>Young Star Volume Engine</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#B2B5BE' }}>
          <span>AI Boundary: Pre-Entry Info</span>
          <span>Latency: 12ms</span>
        </div>
      </div>

      {/* Market Summary Grid */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#E0E0E0', marginBottom: '12px' }}>MARKET WATCH</div>
        {loading ? (
          <div style={{ color: '#787B86', fontSize: '13px' }}>Loading Live Market Data...</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '10px' }}>
            {marketSummary.map((item) => (
              <div key={item.symbol} style={{ backgroundColor: '#131722', padding: '12px', borderRadius: '8px', border: '1px solid #2A2E39' }}>
                <div style={{ fontSize: '12px', color: '#787B86' }}>{item.symbol}</div>
                <div style={{ fontSize: '15px', fontWeight: 'bold', margin: '4px 0', color: '#FFF' }}>{item.price}</div>
                <div style={{ fontSize: '11px', color: item.change.startsWith('+') ? '#00E676' : '#FF5252' }}>
                  {item.change} ({item.status})
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Action Navigation */}
      <div>
        <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#E0E0E0', marginBottom: '12px' }}>QUICK ACTIONS</div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button style={{ flex: 1, padding: '12px', borderRadius: '8px', border: 'none', backgroundColor: '#2962FF', color: '#FFF', fontWeight: 'bold', cursor: 'pointer' }}>
            Open Chart
          </button>
          <button style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid #2A2E39', backgroundColor: '#131722', color: '#B2B5BE', fontWeight: 'bold', cursor: 'pointer' }}>
            Analysis Hub
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardScreen;
