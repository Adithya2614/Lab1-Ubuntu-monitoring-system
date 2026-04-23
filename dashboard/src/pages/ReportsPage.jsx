/** ReportsPage — Analytics charts. */
import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { BarChart3, Monitor, Wifi, WifiOff, Bell, Zap } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const COLORS = ['#6366f1', '#10b981', '#ef4444', '#f59e0b'];

const ReportsPage = () => {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    api.getReportOverview().then(setOverview).catch(console.error);
  }, []);

  if (!overview) return <div className="empty-state"><BarChart3 size={48} /><h3>Loading...</h3></div>;

  const pieData = [
    { name: 'Online', value: overview.online_pcs },
    { name: 'Offline', value: overview.offline_pcs },
  ];

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}>Reports</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
        System analytics and health overview
      </p>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { label: 'Total PCs', value: overview.total_pcs, icon: Monitor, color: 'var(--accent)' },
          { label: 'Online', value: overview.online_pcs, icon: Wifi, color: 'var(--success)' },
          { label: 'Offline', value: overview.offline_pcs, icon: WifiOff, color: 'var(--danger)' },
          { label: 'Total Alerts', value: overview.total_alerts, icon: Bell, color: 'var(--warning)' },
          { label: 'Unresolved', value: overview.unresolved_alerts, icon: Bell, color: 'var(--danger)' },
          { label: 'Actions Today', value: overview.total_actions_today, icon: Zap, color: 'var(--accent)' },
        ].map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-icon" style={{ background: `${s.color}15`, color: s.color }}><s.icon size={20} /></div>
            <div><div className="stat-value" style={{ fontSize: '1.25rem' }}>{s.value}</div><div className="stat-label">{s.label}</div></div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Online vs Offline</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" label>
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>System Health</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', justifyContent: 'center', height: '250px' }}>
            {[
              { label: 'Labs', value: overview.total_labs, color: 'var(--warning)' },
              { label: 'Total Alerts', value: overview.total_alerts, color: 'var(--danger)' },
              { label: 'Actions Today', value: overview.total_actions_today, color: 'var(--accent)' },
            ].map(item => (
              <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ width: '120px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{item.label}</span>
                <div className="progress-bar" style={{ flex: 1 }}>
                  <div className="progress-fill cpu" style={{ width: `${Math.min(item.value * 10, 100)}%` }} />
                </div>
                <span style={{ fontWeight: 600, minWidth: '30px' }}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
