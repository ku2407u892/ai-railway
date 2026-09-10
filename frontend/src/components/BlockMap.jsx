import React from 'react';
import { BlockIcon } from './Icons';

const STATUS_LABEL = { free: 'Free', occupied: 'Occupied', reserved: 'Reserved', maintenance: 'Maintenance' };

export default function BlockMap({ blocks, trains }) {
  const trainFor = (id) => trains.find(t => t.current_block_id === id);

  return (
    <div style={s.card} className="card-hover">
      <div style={s.header}>
        <span style={s.icon}><BlockIcon size={15} /></span>
        <h3 style={s.title}>Block status</h3>
      </div>
      <table>
        <thead>
          <tr>
            {['Block', 'Location', 'Status', 'Track health', 'Train'].map(h => (
              <th key={h} style={s.th}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {blocks.map(b => {
            const t = trainFor(b.id);
            const isActive = b.status !== 'free';
            return (
              <tr key={b.id} style={s.row} className="row-hover">
                <td style={s.td}><strong>{b.name}</strong></td>
                <td style={{ ...s.td, color: '#9CA3AF' }}>{b.location}</td>
                <td style={s.td}>
                  <span style={{ ...s.badge, ...(isActive ? s.badgeActive : s.badgeFree) }}>
                    {STATUS_LABEL[b.status]}
                  </span>
                </td>
                <td style={s.td}>
                  <div style={s.healthBar}>
                    <div style={{ ...s.healthFill, width: `${b.track_health}%` }} />
                  </div>
                </td>
                <td style={{ ...s.td, color: '#0A0A0A' }}>{t ? t.train_number : '—'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
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
  td: { padding: '10px 10px 10px 0', fontSize: 13 },
  badge: { fontSize: 11, fontWeight: 600, padding: '3px 9px', borderRadius: 5 },
  badgeFree: { background: '#F5F5F5', color: '#9CA3AF' },
  badgeActive: { background: '#EFF4FF', color: '#2563EB' },
  healthBar: { width: 80, height: 4, background: '#F5F5F5', borderRadius: 2 },
  healthFill: { height: '100%', background: '#0A0A0A', borderRadius: 2 }
};
