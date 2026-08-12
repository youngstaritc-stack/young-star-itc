import React, { useState } from 'react';
import DashboardScreen from './src/screens/DashboardScreen';
import ChartScreen from './src/screens/ChartScreen';
import AnalysisScreen from './src/screens/AnalysisScreen';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');

  const renderScreen = () => {
    switch (currentTab) {
      case 'dashboard':
        return <DashboardScreen />;
      case 'chart':
        return <ChartScreen />;
      case 'analysis':
        return <AnalysisScreen />;
      default:
        return <DashboardScreen />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#070B14' }}>
      {/* Content Area */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {renderScreen()}
      </div>

      {/* Bottom Navigation Bar */}
      <div style={{
        display: 'flex',
        justify: 'space-around',
        alignItems: 'center',
        height: '60px',
        backgroundColor: '#131722',
        borderTop: '1px solid #2A2E39'
      }}>
        <button
          onClick={() => setCurrentTab('dashboard')}
          style={{
            background: 'none',
            border: 'none',
            color: currentTab === 'dashboard' ? '#2962FF' : '#787B86',
            fontWeight: currentTab === 'dashboard' ? 'bold' : 'normal',
            cursor: 'pointer'
          }}
        >
          Dashboard
        </button>
        <button
          onClick={() => setCurrentTab('chart')}
          style={{
            background: 'none',
            border: 'none',
            color: currentTab === 'chart' ? '#2962FF' : '#787B86',
            fontWeight: currentTab === 'chart' ? 'bold' : 'normal',
            cursor: 'pointer'
          }}
        >
          Chart
        </button>
        <button
          onClick={() => setCurrentTab('analysis')}
          style={{
            background: 'none',
            border: 'none',
            color: currentTab === 'analysis' ? '#2962FF' : '#787B86',
            fontWeight: currentTab === 'analysis' ? 'bold' : 'normal',
            cursor: 'pointer'
          }}
        >
          Analysis
        </button>
      </div>
    </div>
  );
}
