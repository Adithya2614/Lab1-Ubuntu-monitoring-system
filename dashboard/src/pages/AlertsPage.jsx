/** AlertsPage — Alert center. */
import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Bell, Check, AlertTriangle, Info, XCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const sevIcon = { info: Info, warning: AlertTriangle, critical: XCircle };
const sevColor = { info: 'var(--accent)', warning: 'var(--warning)', critical: 'var(--danger)' };

const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => { fetchAlerts(); }, [filter]);

  const fetchAlerts = async () => {
    try {
      const params = filter === 'unresolved' ? 'resolved=false' : filter === 'resolved' ? 'resolved=true' : '';
      const d = await api.getAlerts(params);
      setAlerts(d.alerts || []);
    } catch (e) { toast.error('Failed to load alerts'); }
  };

  const resolve = async (id) => {
    try { await api.resolveAlert(id); toast.success('Alert resolved'); fetchAlerts(); }
    catch (e) { toast.error(e.message); }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div><h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Alerts</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>System alerts and notifications</p></div>
        <div className="filter-bar">
          {['all','unresolved','resolved'].map(f => (
            <button key={f} className={`chip ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}>{f}</button>))}
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="empty-state"><Bell size={48} /><h3>No Alerts</h3><p>System is running smoothly</p></div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {alerts.map(a => {
            const Icon = sevIcon[a.severity] || Info;
            return (
              <div key={a.id} className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ color: sevColor[a.severity], flexShrink: 0 }}><Icon size={20} /></div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500 }}>{a.message}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {a.pc_hostname && `${a.pc_hostname} · `}{a.alert_type} · {new Date(a.created_at).toLocaleString()}
                  </div>
                </div>
                {!a.resolved && (
                  <button className="btn btn-xs btn-success" onClick={() => resolve(a.id)}>
                    <Check size={14} /> Resolve
                  </button>
                )}
                {a.resolved && <span className="badge badge-online">Resolved</span>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AlertsPage;
