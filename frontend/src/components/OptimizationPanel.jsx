import React, { useState } from 'react';
import { executeOptimization } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { BoltIcon } from './Icons';

export default function OptimizationPanel({ suggestions, onRefresh }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const { user } = useAuth();

  const handleExec = async () => {
    setLoading(true);
    try { const r = await executeOptimization(); setResult(r.data); onRefresh(); }
    catch { alert('Failed'); }
    finally { setLoading(false); }
  };

  return (
    <div style={s.card} className="card-hover">
      <div style={s.header}>
        <div style={s.headerLeft}>
          <span style={s.icon}><BoltIcon size={15} /></span>
          <h3 style={s.title}>Optimization ({suggestions.length})</h3>
        </div>
        {user?.role === 'admin' && (
          <button style={s.execBtn} className="btn-hover" onClick={handleExec} disabled={loading}>
            {loading ? 'Running…' : 'Run optimization'}
          </button>
        )}
      </div>

      {result && (
        <div style={s.result} className="fade-in">
          <span>Saved <strong>{result.delay_saved_minutes} min</strong></span>
          <span>Efficiency <strong>+{result.efficiency_gain_percent}%</strong></span>
        </div>
      )}

      {suggestions.length === 0 ? (
        <p style={s.empty}>No suggestions right now</p>
      ) : (
        suggestions.map(sg => (
          <div key={sg.id} style={s.item} className="row-hover">
            <div style={s.itemTop}>
              <span style={s.type}>{sg.type}</span>
              <span style={s.priority}>{sg.priority}</span>
            </div>
            <p style={s.desc}>{sg.description}</p>
            <p style={s.meta}>{sg.impact}% impact · ~{sg.estimated_time} min</p>
          </div>
        ))
      )}
    </div>
  );
}

const s = {
  card: { background: '#FFFFFF', borderRadius: 10, padding: 20, border: '1px solid #E5E5E5' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  headerLeft: { display: 'flex', alignItems: 'center', gap: 8 },
  icon: { color: '#2563EB', display: 'flex' },
  title: { fontSize: 14, fontWeight: 700 },
  execBtn: { fontSize: 12, fontWeight: 600, background: '#0A0A0A', color: '#FFFFFF', border: 'none', padding: '8px 14px', borderRadius: 6 },
  result: { display: 'flex', gap: 20, fontSize: 12, color: '#2563EB', background: '#EFF4FF', padding: '10px 14px', borderRadius: 8, marginBottom: 14 },
  empty: { fontSize: 13, color: '#9CA3AF' },
  item: { padding: '12px 10px', borderTop: '1px solid #F5F5F5', borderRadius: 6, margin: '0 -10px' },
  itemTop: { display: 'flex', justifyContent: 'space-between', marginBottom: 6 },
  type: { fontSize: 12, fontWeight: 700 },
  priority: { fontSize: 11, color: '#9CA3AF', textTransform: 'capitalize' },
  desc: { fontSize: 12, color: '#525252', lineHeight: 1.5, marginBottom: 4 },
  meta: { fontSize: 11, color: '#9CA3AF' }
};
