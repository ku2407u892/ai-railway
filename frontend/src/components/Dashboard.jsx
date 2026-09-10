import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './Navbar';
import StatsCards from './StatsCards';
import BlockMap from './BlockMap';
import TrainTable from './TrainTable';
import AlertPanel from './AlertPanel';
import OptimizationPanel from './OptimizationPanel';
import { getBlocks, getTrains, getAlerts, getSuggestions, getSystemStatus } from '../services/api';

export default function Dashboard() {
  const [blocks, setBlocks] = useState([]);
  const [trains, setTrains] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    try {
      const [b, t, a, s, ss] = await Promise.all([
        getBlocks(), getTrains(), getAlerts(), getSuggestions(), getSystemStatus()
      ]);
      setBlocks(b.data); setTrains(t.data); setAlerts(a.data);
      setSuggestions(s.data); setSystemStatus(ss.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    fetchAll();
    const i = setInterval(fetchAll, 30000);
    return () => clearInterval(i);
  }, [fetchAll]);

  if (loading) return (
    <div className="loading-screen">
      <div className="spinner" />
      <p style={{ fontSize: 13 }}>Loading...</p>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', background: '#F5F5F5' }}>
      <Navbar systemStatus={systemStatus} />
      <div style={{ padding: '28px 32px', maxWidth: 1200, margin: '0 auto' }}>
        <StatsCards systemStatus={systemStatus} trains={trains} blocks={blocks} alerts={alerts} />
        <BlockMap blocks={blocks} trains={trains} />
        <TrainTable trains={trains} />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <AlertPanel alerts={alerts} onRefresh={fetchAll} />
          <OptimizationPanel suggestions={suggestions} onRefresh={fetchAll} />
        </div>
      </div>
    </div>
  );
}
