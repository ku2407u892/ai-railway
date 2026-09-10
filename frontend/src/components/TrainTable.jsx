import React, { useState } from 'react';
import { predictDelay } from '../services/api';
import { TrainIcon } from './Icons';

export default function TrainTable({ trains }) {
  const [prediction, setPrediction] = useState(null);
  const [loadingId, setLoadingId] = useState(null);

  const handlePredict = async (id) => {
    setLoadingId(id);
    try { const r = await predictDelay(id); setPrediction(r.data); }
    catch { alert('Prediction failed'); }
    finally { setLoadingId(null); }
  };

  return (
    <div style={s.card} className="card-hover">
      <div style={s.header}>
        <span style={s.icon}><TrainIcon size={15} /></span>
        <h3 style={s.title}>Trains</h3>
      </div>
      <table>
        <thead>
          <tr>
            {['Train', 'Route', 'Type', 'Delay', 'Priority', ''].map(h => (
              <th key={h} style={s.th}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {trains.map(t => (
            <tr key={t.id} style={s.row} className="row-hover">
              <td style={s.td}>
                <strong>{t.train_number}</strong>
                <div style={s.subText}>{t.train_name}</div>
              </td>
              <td style={{ ...s.td, color: '#9CA3AF' }}>{t.origin} → {t.destination}</td>
              <td style={{ ...s.td, textTransform: 'capitalize' }}>{t.train_type.replace('_', ' ')}</td>
              <td style={s.td}>
                {t.delay_minutes > 0
                  ? <span style={s.delayTag}>+{t.delay_minutes} min</span>
                  : <span style={s.onTimeTag}>On time</span>}
              </td>
              <td style={s.td}>
                <div style={s.priorityBar}>
                  <div style={{ ...s.priorityFill, width: `${t.priority_score}%` }} />
                </div>
              </td>
              <td style={s.td}>
                <button
                  style={s.predictBtn}
                  className="btn-hover"
                  onClick={() => handlePredict(t.id)}
                  disabled={loadingId === t.id}
                >
                  {loadingId === t.id ? '…' : 'Predict'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {prediction && (
        <div style={s.predictBox} className="fade-in">
          <div style={s.predictHeader}>
            <span style={s.predictTitle}>Prediction · {prediction.train_number}</span>
            <button style={s.closeBtn} className="btn-hover" onClick={() => setPrediction(null)}>Close</button>
          </div>
          <div style={s.predictGrid}>
            <div><p style={s.predLabel}>Current delay</p><p style={s.predValue}>{prediction.current_delay} min</p></div>
            <div><p style={s.predLabel}>Predicted delay</p><p style={s.predValue}>{prediction.prediction.predicted_delay_minutes} min</p></div>
            <div><p style={s.predLabel}>Confidence</p><p style={s.predValue}>{(prediction.prediction.confidence * 100).toFixed(0)}%</p></div>
            <div><p style={s.predLabel}>Weather</p><p style={s.predValue}>{prediction.prediction.contributing_factors.weather}</p></div>
          </div>
        </div>
      )}
    </div>
  );
}

const s = {
  card: { background: '#FFFFFF', borderRadius: 10, padding: 20, border: '1px solid #E5E5E5', marginBottom: 16 },
  header: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 },
  icon: { color: '#2563EB', display: 'flex' },
  title: { fontSize: 14, fontWeight: 700 },
  th: { textAlign: 'left', fontSize: 11, color: '#9CA3AF', fontWeight: 600, padding: '0 10px 10px 0', textTransform: 'uppercase', letterSpacing: 0.3 },
  row: { borderTop: '1px solid #F5F5F5' },
  td: { padding: '12px 10px 12px 0', fontSize: 13, verticalAlign: 'middle' },
  subText: { fontSize: 11, color: '#9CA3AF', marginTop: 2 },
  delayTag: { fontSize: 12, fontWeight: 600, color: '#2563EB' },
  onTimeTag: { fontSize: 12, color: '#9CA3AF' },
  priorityBar: { width: 70, height: 4, background: '#F5F5F5', borderRadius: 2 },
  priorityFill: { height: '100%', background: '#0A0A0A', borderRadius: 2 },
  predictBtn: { fontSize: 11, fontWeight: 600, background: '#0A0A0A', color: '#FFFFFF', border: 'none', padding: '6px 12px', borderRadius: 6 },
  predictBox: { marginTop: 16, borderTop: '1px solid #E5E5E5', paddingTop: 16 },
  predictHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: 12 },
  predictTitle: { fontSize: 13, fontWeight: 700 },
  closeBtn: { fontSize: 11, color: '#9CA3AF', background: 'none', border: 'none' },
  predictGrid: { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 },
  predLabel: { fontSize: 11, color: '#9CA3AF', marginBottom: 4 },
  predValue: { fontSize: 16, fontWeight: 700, color: '#0A0A0A' }
};
