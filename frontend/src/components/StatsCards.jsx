import React from 'react';
import { TrainIcon, BlockIcon, AlertIcon, BoltIcon } from './Icons';

export default function StatsCards({ systemStatus, trains, blocks, alerts }) {
  const delayed = trains.filter(t => t.status === 'delayed').length;
  const free = blocks.filter(b => b.status === 'free').length;

  const items = [
    { label: 'Trains running', value: trains.length, note: `${delayed} delayed`, icon: <TrainIcon size={15} /> },
    { label: 'Blocks free', value: `${free}/${blocks.length}`, note: 'available now', icon: <BlockIcon size={15} /> },
    { label: 'Open alerts', value: alerts.length, note: 'need review', icon: <AlertIcon size={15} /> },
    { label: 'Uptime', value: systemStatus?.uptime || '—', note: 'last 30 days', icon: <BoltIcon size={15} /> },
  ];

  return (
    <div style={s.grid}>
      {items.map((it, i) => (
        <div key={i} style={s.card} className="card-hover">
          <div style={s.top}>
            <p style={s.label}>{it.label}</p>
            <span style={s.icon}>{it.icon}</span>
          </div>
          <p style={s.value}>{it.value}</p>
          <p style={s.note}>{it.note}</p>
        </div>
      ))}
    </div>
  );
}

const s = {
  grid: { display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 24 },
  card: { background: '#FFFFFF', padding: '18px 20px', border: '1px solid #E5E5E5', borderRadius: 10 },
  top: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  label: { fontSize: 12, color: '#9CA3AF' },
  icon: { color: '#2563EB', display: 'flex' },
  value: { fontSize: 26, fontWeight: 700, color: '#0A0A0A', letterSpacing: -0.5 },
  note: { fontSize: 11, color: '#9CA3AF', marginTop: 4 }
};
