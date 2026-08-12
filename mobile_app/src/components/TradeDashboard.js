import React, { useEffect, useState } from 'react';

export default function TradeDashboard() {
  const [signalData, setSignalData] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Connect to FastAPI WebSocket Endpoint
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host;
    const ws = new WebSocket(`${wsProtocol}//${wsHost}/ws/signals`);

    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      if (parsed.type === 'SIGNAL_UPDATE') {
        setSignalData(parsed.data);
        setHistory((prev) => [parsed.data, ...prev.slice(0, 9)]);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{ padding: '15px', color: '#fff', backgroundColor: '#121212', minHeight: '100vh' }}>
      <h2>Young Star ITC Trade Signals</h2>
      
      {/* Live Signal Card */}
      {signalData ? (
        <div style={{
          padding: '15px',
          borderRadius: '8px',
          backgroundColor: signalData.signal === 'BUY' ? '#1b5e20' : signalData.signal === 'SELL' ? '#b71c1c' : '#333',
          marginBottom: '20px'
        }}>
          <h3>Signal: {signalData.signal}</h3>
          <p>Price: ${signalData.price.toFixed(2)}</p>
          <p>RSI: {signalData.rsi} | EMA20: {signalData.ema_20} | EMA50: {signalData.ema_50}</p>
          <p><small>{signalData.reason}</small></p>
        </div>
      ) : (
        <p>Connecting to AI Signal Engine...</p>
      )}

      {/* Recent Signals History */}
      <h3>Recent Signal History</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {history.map((item, idx) => (
          <li key={idx} style={{ padding: '8px', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between' }}>
            <span>Price: ${item.price.toFixed(2)}</span>
            <span style={{ color: item.signal === 'BUY' ? '#4caf50' : item.signal === 'SELL' ? '#f44336' : '#ffeb3b', fontWeight: 'bold' }}>
              {item.signal} (RSI: {item.rsi})
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
