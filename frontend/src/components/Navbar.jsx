import React from 'react';
import { useAuth } from '../context/AuthContext';
import { TrainIcon } from './Icons';

export default function Navbar({ systemStatus }) {
  const { user, logout } = useAuth();
  return (
    <nav style={s.nav}>
      <div style={s.left}>
        <div style={s.logo}><TrainIcon size={16} /></div>
        <span style={s.brand}>RailOps</span>
      </div>
      <div style={s.right}>
        <span style={s.status}>
          <span style={s.statusDot} />
          {systemStatus?.status || '—'}
        </span>
        <span style={s.user}>{user?.username} · {user?.role}</span>
        <button style={s.logout} className="btn-hover" onClick={logout}>Sign out</button>
      </div>
    </nav>
  );
}

const s = {
  nav: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 32px', background: '#0A0A0A' },
  left: { display: 'flex', alignItems: 'center', gap: 10 },
  logo: { width: 28, height: 28, borderRadius: 7, background: '#2563EB', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  brand: { color: '#FFFFFF', fontSize: 15, fontWeight: 700, letterSpacing: -0.3 },
  right: { display: 'flex', alignItems: 'center', gap: 20 },
  status: { fontSize: 12, color: '#9CA3AF', textTransform: 'capitalize', display: 'flex', alignItems: 'center', gap: 6 },
  statusDot: { width: 6, height: 6, borderRadius: '50%', background: '#2563EB', display: 'inline-block' },
  user: { fontSize: 12, color: '#FFFFFF' },
  logout: { fontSize: 12, color: '#0A0A0A', background: '#FFFFFF', border: 'none', padding: '6px 14px', borderRadius: 6, fontWeight: 600 }
};
