import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { TrainIcon } from './Icons';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError('');
    try { await login(form.username, form.password); navigate('/'); }
    catch { setError('Invalid credentials'); }
    finally { setLoading(false); }
  };

  return (
    <div style={s.page}>
      <div style={s.card} className="fade-in">
        <div style={s.brand}>
          <div style={s.logo}><TrainIcon size={18} /></div>
          <h1 style={s.title}>RailOps</h1>
        </div>
        <p style={s.subtitle}>Block Planning System</p>

        <form onSubmit={handleSubmit} style={s.form}>
          <input
            style={s.input}
            placeholder="Username"
            value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })}
            required
          />
          <input
            style={s.input}
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            required
          />
          {error && <p style={s.error}>{error}</p>}
          <button style={s.btn} className="btn-hover" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={s.hint}>admin / railway123 &nbsp;·&nbsp; operator / railway123</div>
      </div>
    </div>
  );
}

const s = {
  page: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#0A0A0A' },
  card: { background: '#FFFFFF', borderRadius: 14, padding: 40, width: 360 },
  brand: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 },
  logo: { width: 32, height: 32, borderRadius: 8, background: '#2563EB', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: 20, fontWeight: 700, letterSpacing: -0.3 },
  subtitle: { fontSize: 13, color: '#9CA3AF', marginBottom: 28 },
  form: { display: 'flex', flexDirection: 'column', gap: 10 },
  input: { padding: '11px 14px', border: '1px solid #E5E5E5', borderRadius: 8, fontSize: 14, outline: 'none', transition: 'border 0.15s' },
  error: { fontSize: 12, color: '#0A0A0A', background: '#F5F5F5', padding: '8px 10px', borderRadius: 6 },
  btn: { padding: 12, background: '#0A0A0A', color: '#FFFFFF', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 600, marginTop: 6 },
  hint: { marginTop: 20, fontSize: 11, color: '#9CA3AF', textAlign: 'center' }
};
