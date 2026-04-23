/** PCsPage — All PCs with search, filter. */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { useAppContext } from '../context/AppContext';
import { useDebounce } from '../hooks/useDebounce';
import { Monitor, Search, LayoutGrid, List, Cpu, Activity, HardDrive, Wifi, Radio } from 'lucide-react';

const filters = ['All', 'Online', 'Offline', 'High CPU', 'High RAM'];

const PCsPage = () => {
  const navigate = useNavigate();
  const { viewMode, setViewMode } = useAppContext();
  const [nodes, setNodes] = useState([]);
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    const fetch = async () => { try { const d = await api.getNodes(); setNodes(d.nodes || []); } catch (e) { console.error(e); } };
    fetch(); const i = setInterval(fetch, 5000); return () => clearInterval(i);
  }, []);

  const filtered = nodes.filter(n => {
    const s = debouncedSearch.toLowerCase();
    const matchSearch = !s || (n.name || n.hostname || '').toLowerCase().includes(s) ||
      (n.ip || '').includes(s) || (n.lab_name || '').toLowerCase().includes(s);
    const matchFilter = activeFilter === 'All' ||
      (activeFilter === 'Online' && n.status === 'online') ||
      (activeFilter === 'Offline' && n.status !== 'online') ||
      (activeFilter === 'High CPU' && parseFloat(n.facts?.cpu_load || 0) > 3) ||
      (activeFilter === 'High RAM' && parseInt(n.facts?.ram_percentage || '0') > 80);
    return matchSearch && matchFilter;
  });

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>All PCs</h1>
        <div className="view-toggle">
          <button className={`view-toggle-btn ${viewMode === 'grid' ? 'active' : ''}`} onClick={() => setViewMode('grid')}><LayoutGrid size={16} /></button>
          <button className={`view-toggle-btn ${viewMode === 'list' ? 'active' : ''}`} onClick={() => setViewMode('list')}><List size={16} /></button>
        </div>
      </div>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div className="search-box" style={{ width: '280px' }}><Search /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name, IP, lab..." /></div>
        <div className="filter-bar" style={{ padding: 0 }}>
          {filters.map(f => (<button key={f} className={`chip ${activeFilter === f ? 'active' : ''}`} onClick={() => setActiveFilter(f)}>{f}</button>))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state"><Monitor size={48} /><h3>No PCs found</h3><p>Try adjusting your search or filters</p></div>
      ) : viewMode === 'grid' ? (
        <div className="pc-grid">
          {filtered.map(n => (
            <div key={n.id || n.hostname} className="card card-clickable" onClick={() => navigate(`/node/${n.hostname || n.name || n.id}`)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Radio size={16} style={{ color: 'var(--accent)' }} />
                  <span style={{ fontWeight: 600 }}>{n.name || n.hostname}</span>
                </div>
                <span className={`badge ${n.status === 'online' ? 'badge-online' : 'badge-offline'}`}><span className="badge-dot" />{n.status}</span>
              </div>
              {n.lab_name && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{n.lab_name}</div>}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Cpu size={12} /> CPU: {n.facts?.cpu_load || '—'}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Activity size={12} /> RAM: {n.facts?.ram_percentage || '—'}</div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card" style={{ overflow: 'auto' }}>
          <table className="data-table"><thead><tr><th>Name</th><th>Status</th><th>Lab</th><th>IP</th><th>CPU</th><th>RAM</th><th>Disk</th></tr></thead>
            <tbody>{filtered.map(n => (
              <tr key={n.id || n.hostname} style={{ cursor: 'pointer' }} onClick={() => navigate(`/node/${n.hostname || n.name || n.id}`)}>
                <td style={{ fontWeight: 500 }}>{n.name || n.hostname}</td>
                <td><span className={`badge ${n.status === 'online' ? 'badge-online' : 'badge-offline'}`}><span className="badge-dot" />{n.status}</span></td>
                <td>{n.lab_name || '—'}</td><td style={{ fontFamily: 'monospace', fontSize: '0.8125rem' }}>{n.ip || '—'}</td>
                <td>{n.facts?.cpu_load || '—'}</td><td>{n.facts?.ram_percentage || '—'}</td><td>{n.facts?.disk_percentage || '—'}</td>
              </tr>))}</tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default PCsPage;
