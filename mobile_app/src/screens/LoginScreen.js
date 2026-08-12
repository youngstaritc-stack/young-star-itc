import React, { useState } from 'react';

export default function LoginScreen({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('https://miniature-tribble-xr9qxv7xrv5gfvgv6-8000.app.github.dev/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (data.token || res.ok) {
        onLoginSuccess();
      } else {
        alert('Login failed: ' + (data.message || 'Invalid credentials'));
      }
    } catch (err) {
      alert('Error connecting to backend server');
    }
  };

  return (
    <div style={{ backgroundColor: '#0b0e14', color: '#fff', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: 'sans-serif' }}>
      <h2 style={{ color: '#38bdf8', marginBottom: '20px' }}>Young Star ITC</h2>
      <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', width: '80%', maxWidth: '320px', gap: '15px' }}>
        <input 
          type="email" 
          placeholder="Email" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', backgroundColor: '#1e293b', color: '#fff' }}
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', backgroundColor: '#1e293b', color: '#fff' }}
        />
        <button type="submit" style={{ padding: '12px', borderRadius: '8px', border: 'none', backgroundColor: '#0284c7', color: '#fff', fontWeight: 'bold', cursor: 'pointer' }}>
          Login
        </button>
      </form>
    </div>
  );
}
