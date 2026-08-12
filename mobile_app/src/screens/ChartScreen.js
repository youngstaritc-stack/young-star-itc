import React, { useState, useEffect } from 'react';

export default function ChartScreen() {
  const [data, setData] = useState({ symbol: 'XAU/USD', price: 0, volume: 0, ai_signal: 'WAIT' });

  useEffect(() => {
    const ws = new WebSocket('wss://miniature-tribble-xr9qxv7xrv5gfvgv6-8000.app.github.dev/ws/stream');
    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
      } catch (err) {
        console.error('WebSocket Error:', err);
      }
    };
    return () => ws.close();
  }, []);

  return (
    <div style={{ backgroundColor: '#0b0e14', color: '#fff', minHeight: '100vh', padding: '20px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0, color: '#38bdf8' }}>Young Star ITC Chart</h3>
        <span style={{ backgroundColor: '#1e293b', padding: '6px 12px', borderRadius: '6px', fontSize: '12px' }}>LIVE</span>
      </div>

      <div style={{ backgroundColor: '#131b26', padding: '16px', borderRadius: '12px', marginBottom: '20px' }}>
        <div style={{ fontSize: '14px', color: '#94a3b8' }}>{data.symbol || 'XAU/USD'}</div>
        <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#34d399', margin: '8px 0' }}>
          ${data.price ? data.price.toFixed(2) : '0.00'}
        </div>
        <div style={{ fontSize: '12px', color: '#cbd5e1' }}>Volume: {data.volume || 0}</div>
      </div>

      <div style={{ backgroundColor: '#131b26', padding: '16px', borderRadius: '12px', borderLeft: '4px solid #0284c7' }}>
        <div style={{ fontSize: '12px', color: '#94a3b8' }}>AI Engine State</div>
        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#38bdf8', marginTop: '4px' }}>
          Signal: {data.ai_signal || 'NEUTRAL'}
        </div>
      </div>
    </div>
  );
}
