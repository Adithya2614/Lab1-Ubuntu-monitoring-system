/** ActionsPage — Bulk action builder + history. */
import React, { useState } from 'react';
import { api } from '../api';
import { Zap, Play } from 'lucide-react';
import toast from 'react-hot-toast';

const actionTypes = [
  { value: 'collect_metrics', label: 'Collect Metrics' },
  { value: 'update_internet', label: 'Toggle Internet' },
  { value: 'manage_browsers', label: 'Manage Browsers' },
  { value: 'archive_files', label: 'Archive Files' },
  { value: 'restore_files', label: 'Restore Files' },
  { value: 'cleanup_apps', label: 'Cleanup Apps' },
  { value: 'sync_time', label: 'Sync Time' },
  { value: 'restrict_websites', label: 'Website Restriction' },
];

const ActionsPage = () => {
  const [targets, setTargets] = useState('');
  const [actionType, setActionType] = useState('collect_metrics');
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);

  const runAction = async () => {
    const tList = targets.split(/[\n,]+/).map(t => t.trim()).filter(Boolean);
    if (!tList.length) { toast.error('Enter target hostnames'); return; }
    setRunning(true); setResult(null);
    try {
      const res = await api.runBulkAction(tList, actionType);
      setResult(res); toast.success(`Done: ${res.success} succeeded, ${res.failed} failed`);
    } catch (e) { toast.error(e.message); }
    finally { setRunning(false); }
  };

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}>Actions</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>Execute bulk actions across multiple PCs</p>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Bulk Action Builder</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <div className="form-group">
            <label>Action Type</label>
            <select className="input" value={actionType} onChange={e => setActionType(e.target.value)}>
              {actionTypes.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Targets (one per line or comma-separated)</label>
            <textarea className="input" rows={3} value={targets} onChange={e => setTargets(e.target.value)}
              placeholder="CSE-ICB-051.local&#10;CSE-ICB-052.local" style={{ resize: 'vertical' }} />
          </div>
        </div>
        <button className="btn btn-primary" onClick={runAction} disabled={running}>
          <Play size={16} /> {running ? 'Running...' : 'Execute'}
        </button>
      </div>

      {result && (
        <div className="card">
          <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Results</h3>
          <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1rem' }}>
            <span className="badge badge-online">Success: {result.success}</span>
            <span className="badge badge-offline">Failed: {result.failed}</span>
            <span className="badge badge-info">Total: {result.total}</span>
          </div>
          <table className="data-table"><thead><tr><th>Target</th><th>Status</th><th>Message</th></tr></thead>
            <tbody>
              {Object.entries(result.results || {}).map(([host, r]) => (
                <tr key={host}><td style={{ fontWeight: 500 }}>{host}</td>
                  <td><span className={`badge ${r.status === 'success' ? 'badge-online' : 'badge-offline'}`}>{r.status}</span></td>
                  <td style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{r.message || '—'}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ActionsPage;
