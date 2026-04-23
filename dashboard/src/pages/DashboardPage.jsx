/**
 * DashboardPage — Main overview with stats, charts, recent alerts, and global controls.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { useAppContext } from '../context/AppContext';
import {
  Monitor, Wifi, WifiOff, Cpu, HardDrive, Activity, Radio,
  Globe, Lock, Shield, Archive, RotateCcw, Clock, RefreshCw,
  LayoutGrid, List, FlaskConical, Bell, Zap,
} from 'lucide-react';
import toast from 'react-hot-toast';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { viewMode, setViewMode } = useAppContext();
  const [nodes, setNodes] = useState([]);
  const [stats, setStats] = useState({ total: 0, online: 0, offline: 0 });
  const [labs, setLabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [nodesData, labsData] = await Promise.all([api.getNodes(), api.getLabs()]);
      setNodes(nodesData.nodes || []);
      const total = nodesData.nodes?.length || 0;
      const online = nodesData.nodes?.filter(n => n.status === 'online').length || 0;
      setStats({ total, online, offline: total - online });
      setLabs(labsData.labs || []);
    } catch (e) {
      console.error('Failed to fetch data', e);
    } finally {
      setLoading(false);
    }
  };

  const handleGlobalAction = async (action, params) => {
    const onlineNodes = nodes.filter(n => n.status === 'online');
    if (!onlineNodes.length) { toast.error('No online nodes'); return; }
    if (!confirm(`Run ${action} on ${onlineNodes.length} online nodes?`)) return;

    setActionLoading(true);
    const actionMap = {
      internet: 'update_internet', browsers: 'manage_browsers',
      archive: 'archive_files', restore: 'restore_files',
      cleanup: 'cleanup_apps', sync_time: 'sync_time', restrict: 'restrict_websites',
    };

    try {
      const result = await api.runBulkAction(
        onlineNodes.map(n => n.hostname || n.name || n.id),
        actionMap[action], params);
      toast.success(`Done: ${result.success} succeeded, ${result.failed} failed`);
      fetchData();
    } catch (e) {
      toast.error('Action failed: ' + e.message);
    } finally {
      setActionLoading(false);
    }
  };

  const statCards = [
    { label: 'Total PCs', value: stats.total, icon: Monitor, color: 'var(--accent)', bg: 'var(--accent-glow)' },
    { label: 'Online', value: stats.online, icon: Wifi, color: 'var(--success)', bg: 'var(--success-bg)' },
    { label: 'Offline', value: stats.offline, icon: WifiOff, color: 'var(--danger)', bg: 'var(--danger-bg)' },
    { label: 'Labs', value: labs.length, icon: FlaskConical, color: 'var(--warning)', bg: 'var(--warning-bg)' },
  ];

  return (
    <div className="animate-fade-in">
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Monitor and manage your lab infrastructure
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div className="view-toggle">
            <button className={`view-toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
                    onClick={() => setViewMode('grid')}><LayoutGrid size={16} /></button>
            <button className={`view-toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
                    onClick={() => setViewMode('list')}><List size={16} /></button>
          </div>
        </div>
      </div>

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        {statCards.map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-icon" style={{ background: s.bg, color: s.color }}>
              <s.icon size={22} />
            </div>
            <div>
              <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Global Controls */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.25rem' }}>Global Controls</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem', marginBottom: '1rem' }}>
          Apply controls to all online PCs simultaneously
        </p>
        <div className="controls-grid">
          {[
            { label: 'Internet', icon: Globe,
              actions: [
                { label: 'Enable All', cls: 'btn-success', fn: () => handleGlobalAction('internet', { state: 'enabled' }) },
                { label: 'Disable All', cls: 'btn-danger', fn: () => handleGlobalAction('internet', { state: 'disabled' }) },
              ]},
            { label: 'Browsers', icon: Lock,
              actions: [
                { label: 'Unblock', cls: 'btn-success', fn: () => handleGlobalAction('browsers', { action: 'unblock' }) },
                { label: 'Block', cls: 'btn-danger', fn: () => handleGlobalAction('browsers', { action: 'block' }) },
              ]},
            { label: 'Vault', icon: Shield,
              actions: [
                { label: 'Archive', cls: 'btn-primary', fn: () => handleGlobalAction('archive') },
                { label: 'Restore', cls: 'btn-success', fn: () => handleGlobalAction('restore') },
              ]},
            { label: 'Web Filter', icon: Globe,
              actions: [
                { label: 'Lockdown', cls: 'btn-danger', fn: () => handleGlobalAction('restrict', { target_state: 'restrict' }) },
                { label: 'Restore', cls: 'btn-success', fn: () => handleGlobalAction('restrict', { target_state: 'restore' }) },
              ]},
            { label: 'Time Sync', icon: Clock,
              actions: [
                { label: 'Sync All', cls: 'btn-success', fn: () => handleGlobalAction('sync_time') },
              ]},
          ].map(ctrl => (
            <div key={ctrl.label} className="control-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500 }}>
                  <ctrl.icon size={16} /> {ctrl.label}
                </span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {ctrl.actions.map(a => (
                    <button key={a.label} className={`btn btn-xs ${a.cls}`}
                            onClick={a.fn} disabled={actionLoading}>{a.label}</button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* PC Grid / Table */}
      {loading ? (
        <div className="pc-grid">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="card" style={{ height: '160px' }}>
              <div className="skeleton" style={{ width: '60%', height: '16px', marginBottom: '1rem' }} />
              <div className="skeleton" style={{ width: '40%', height: '12px', marginBottom: '0.75rem' }} />
              <div className="skeleton" style={{ width: '80%', height: '12px', marginBottom: '0.75rem' }} />
              <div className="skeleton" style={{ width: '50%', height: '12px' }} />
            </div>
          ))}
        </div>
      ) : nodes.length === 0 ? (
        <div className="empty-state">
          <HardDrive size={48} />
          <h3>No PCs Registered</h3>
          <p>Click "Add PC" to start monitoring computers</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="pc-grid">
          {nodes.map(node => (
            <div key={node.id || node.hostname} className="card card-clickable"
                 onClick={() => navigate(`/node/${node.hostname || node.name || node.id}`)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ padding: '0.5rem', background: 'var(--accent-glow)', borderRadius: 'var(--radius-md)', color: 'var(--accent)' }}>
                    <Radio size={18} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600 }}>{node.name || node.hostname}</div>
                    {node.lab_name && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{node.lab_name}</div>}
                  </div>
                </div>
                <span className={`badge ${node.status === 'online' ? 'badge-online' : 'badge-offline'}`}>
                  <span className="badge-dot" />
                  {node.status === 'online' ? 'Online' : 'Offline'}
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                {[
                  { label: 'CPU', value: node.facts?.cpu_load || '0.00', icon: Cpu },
                  { label: 'RAM', value: node.facts?.ram_percentage || '0%', icon: Activity },
                  { label: 'Disk', value: node.facts?.disk_percentage || '0%', icon: HardDrive },
                  { label: 'Net', value: node.status === 'online' ? 'Connected' : 'Disconnected', icon: Wifi },
                ].map(m => (
                  <div key={m.label} style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                    <m.icon size={14} /> <span style={{ flex: 1 }}>{m.label}</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{m.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Table view */
        <div className="card" style={{ overflow: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>PC Name</th><th>Status</th><th>Lab</th>
                <th>CPU</th><th>RAM</th><th>Disk</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map(node => (
                <tr key={node.id || node.hostname}
                    style={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/node/${node.hostname || node.name || node.id}`)}>
                  <td style={{ fontWeight: 500 }}>{node.name || node.hostname}</td>
                  <td><span className={`badge ${node.status === 'online' ? 'badge-online' : 'badge-offline'}`}>
                    <span className="badge-dot" />{node.status}</span></td>
                  <td>{node.lab_name || '—'}</td>
                  <td>{node.facts?.cpu_load || '—'}</td>
                  <td>{node.facts?.ram_percentage || '—'}</td>
                  <td>{node.facts?.disk_percentage || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Action Loading Overlay */}
      {actionLoading && (
        <div className="modal-backdrop" style={{ zIndex: 9999 }}>
          <div style={{ textAlign: 'center' }}>
            <RefreshCw size={48} className="animate-spin" style={{ color: 'var(--accent)', marginBottom: '1rem' }} />
            <h2>Processing Global Action...</h2>
            <p style={{ color: 'var(--text-secondary)' }}>Running on all online nodes in parallel</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
