import React from 'react';
import { acknowledgeAlert } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { AlertIcon, CheckIcon } from './Icons';

const SEVERITY_LABEL = { critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low' };

export default function AlertPanel({ alerts, onRefresh }) {
  const { user } = useAuth();
  const handleAck = async (id) => { try { await acknowledgeAlert(id); onRefresh(); } catch { alert('Failed'); } };

  return (
    <div style={s.card} className="card-hover">
      <div style={s.header}>
        <span style={s.icon}><AlertIcon size={15} /></span>
        <h3 style={s.title}>Alerts ({alerts.length})</h3>
      </div>
      {alerts.length === 0 ? (
        <p style={s.empty}>No active alerts</p>
      ) : (
        <div>
          {alerts.map(a => (
            <div key={a.id} style={s.item} className="row-hover">
              <div style={s.itemTop}>
                <span style={s.severity}>{SEVERITY_LABEL[a.severity]}</span>
                <span style={s.time}>{a.timestamp}</span>
              </div>
              <p style={s.itemTitle}>{a.title}</p>
              <p style={s.itemDesc}>{a.description}</p>
              {user?.role === 'admin' && (
                <button style={s.ackBtn} className="btn-hover" onClick={() => handleAck(a.id)}>
                  <CheckIcon size={12} /> Acknowledge
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const s = {
  card: { background: '#FFFFFF', borderRadius: 10, padding: 20, border: '1px solid #E5E5E5' },
  header: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 },
  icon: { color: '#2563EB', display: 'flex' },
  title: { fontSize: 14, fontWeight: 700 },
  empty: { fontSize: 13, color: '#9CA3AF' },
  item: { padding: '14px 10px', borderTop: '1px solid #F5F5F5', borderRadius: 6, margin: '0 -10px' },
  itemTop: { display: 'flex', justifyContent: 'space-between', marginBottom: 6 },
  severity: { fontSize: 11, fontWeight: 700, color: '#2563EB', textTransform: 'uppercase', letterSpacing: 0.3 },
  time: { fontSize: 11, color: '#9CA3AF' },
  itemTitle: { fontSize: 13, fontWeight: 600, marginBottom: 4 },
  itemDesc: { fontSize: 12, color: '#9CA3AF', lineHeight: 1.5, marginBottom: 8 },
  ackBtn: { fontSize: 11, fontWeight: 600, background: 'none', border: '1px solid #E5E5E5', padding: '5px 12px', borderRadius: 6, display: 'inline-flex', alignItems: 'center', gap: 5 }
};
