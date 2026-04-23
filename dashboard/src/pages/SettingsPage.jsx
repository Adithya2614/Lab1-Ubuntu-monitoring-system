/** SettingsPage — SSH Keys, Whitelist, Blocked Apps. */
import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Settings, Key, Globe, ShieldBan, Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

const SettingsPage = () => {
  const [tab, setTab] = useState('whitelist');
  const [domains, setDomains] = useState([]);
  const [blockedApps, setBlockedApps] = useState([]);
  const [sshKeys, setSSHKeys] = useState([]);
  const [newDomain, setNewDomain] = useState('');
  const [newApp, setNewApp] = useState('');
  const [newKeyName, setNewKeyName] = useState('');

  useEffect(() => { loadTab(); }, [tab]);

  const loadTab = async () => {
    try {
      if (tab === 'whitelist') { const d = await api.getWhitelist(); setDomains(d.domains || []); }
      if (tab === 'blocked') { const d = await api.getBlockedApps(); setBlockedApps(d.apps || []); }
      if (tab === 'ssh') { const d = await api.getSSHKeys(); setSSHKeys(d.keys || []); }
    } catch (e) { console.error(e); }
  };

  const addDomain = async () => {
    if (!newDomain) return;
    try { await api.addWhitelist({ domain: newDomain }); setNewDomain(''); loadTab(); toast.success('Domain added'); }
    catch (e) { toast.error(e.message); }
  };

  const addApp = async () => {
    if (!newApp) return;
    try { await api.addBlockedApp({ app_name: newApp }); setNewApp(''); loadTab(); toast.success('App added'); }
    catch (e) { toast.error(e.message); }
  };

  const genKey = async () => {
    if (!newKeyName) return;
    try { await api.generateSSHKey({ name: newKeyName }); setNewKeyName(''); loadTab(); toast.success('Key generated'); }
    catch (e) { toast.error(e.message); }
  };

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}>Settings</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>System configuration and security</p>

      <div className="tab-nav">
        {[{k:'whitelist',l:'URL Whitelist',i:Globe},{k:'blocked',l:'Blocked Apps',i:ShieldBan},{k:'ssh',l:'SSH Keys',i:Key}].map(t => (
          <button key={t.k} className={`tab-btn ${tab === t.k ? 'active' : ''}`} onClick={() => setTab(t.k)}>
            <t.i size={16} style={{ marginRight: '0.375rem', verticalAlign: 'middle' }} />{t.l}
          </button>
        ))}
      </div>

      {tab === 'whitelist' && (
        <div className="card">
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
            <input className="input" value={newDomain} onChange={e => setNewDomain(e.target.value)} placeholder="google.com" style={{ flex: 1 }} />
            <button className="btn btn-primary" onClick={addDomain}><Plus size={16} /> Add</button>
          </div>
          <table className="data-table"><thead><tr><th>Domain</th><th>Added</th><th></th></tr></thead><tbody>
            {domains.map(d => (
              <tr key={d.id}><td>{d.domain}</td><td style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{new Date(d.created_at).toLocaleDateString()}</td>
                <td><button className="btn-icon" onClick={() => { api.deleteWhitelist(d.id).then(loadTab); }}><Trash2 size={14} /></button></td></tr>
            ))}
          </tbody></table>
        </div>
      )}

      {tab === 'blocked' && (
        <div className="card">
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
            <input className="input" value={newApp} onChange={e => setNewApp(e.target.value)} placeholder="firefox" style={{ flex: 1 }} />
            <button className="btn btn-primary" onClick={addApp}><Plus size={16} /> Add</button>
          </div>
          <table className="data-table"><thead><tr><th>App Name</th><th>Auto Kill</th><th></th></tr></thead><tbody>
            {blockedApps.map(a => (
              <tr key={a.id}><td>{a.app_name}</td><td>{a.auto_kill ? '✓' : '✗'}</td>
                <td><button className="btn-icon" onClick={() => { api.deleteBlockedApp(a.id).then(loadTab); }}><Trash2 size={14} /></button></td></tr>
            ))}
          </tbody></table>
        </div>
      )}

      {tab === 'ssh' && (
        <div className="card">
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
            <input className="input" value={newKeyName} onChange={e => setNewKeyName(e.target.value)} placeholder="my-lab-key" style={{ flex: 1 }} />
            <button className="btn btn-primary" onClick={genKey}><Key size={16} /> Generate</button>
          </div>
          <table className="data-table"><thead><tr><th>Name</th><th>Fingerprint</th><th>Created</th><th></th></tr></thead><tbody>
            {sshKeys.map(k => (
              <tr key={k.id}><td style={{ fontWeight: 500 }}>{k.name}</td>
                <td style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>{k.fingerprint?.substring(0, 40)}...</td>
                <td style={{ fontSize: '0.8125rem' }}>{new Date(k.created_at).toLocaleDateString()}</td>
                <td><button className="btn-icon" onClick={() => { api.deleteSSHKey(k.id).then(loadTab); }}><Trash2 size={14} /></button></td></tr>
            ))}
          </tbody></table>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
