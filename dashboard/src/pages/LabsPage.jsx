/**
 * LabsPage — Lab management with CRUD.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { FlaskConical, Plus, Edit, Trash2, Monitor, Wifi } from 'lucide-react';
import toast from 'react-hot-toast';

const LabsPage = () => {
  const navigate = useNavigate();
  const [labs, setLabs] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newLab, setNewLab] = useState({ name: '', description: '' });

  useEffect(() => { fetchLabs(); }, []);

  const fetchLabs = async () => {
    try { const d = await api.getLabs(); setLabs(d.labs || []); }
    catch (e) { toast.error('Failed to load labs'); }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.createLab(newLab);
      toast.success('Lab created');
      setShowCreate(false); setNewLab({ name: '', description: '' }); fetchLabs();
    } catch (e) { toast.error(e.message); }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete lab "${name}"? PCs will be unassigned.`)) return;
    try { await api.deleteLab(id); toast.success('Lab deleted'); fetchLabs(); }
    catch (e) { toast.error(e.message); }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Labs</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Manage lab rooms and PC assignments</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          <Plus size={16} /> Create Lab
        </button>
      </div>

      {labs.length === 0 ? (
        <div className="empty-state"><FlaskConical size={48} /><h3>No Labs</h3><p>Create your first lab to organize PCs</p></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.25rem' }}>
          {labs.map(lab => (
            <div key={lab.id} className="card card-clickable" onClick={() => navigate(`/labs/${lab.id}`)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ padding: '0.5rem', background: 'var(--warning-bg)', borderRadius: 'var(--radius-md)', color: 'var(--warning)' }}>
                    <FlaskConical size={18} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600 }}>{lab.name}</div>
                    {lab.description && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{lab.description}</div>}
                  </div>
                </div>
                <button className="btn-icon" onClick={(e) => { e.stopPropagation(); handleDelete(lab.id, lab.name); }}>
                  <Trash2 size={16} />
                </button>
              </div>
              <div style={{ display: 'flex', gap: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  <Monitor size={14} /> {lab.pc_count || 0} PCs
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.875rem', color: 'var(--success)' }}>
                  <Wifi size={14} /> {lab.online_count || 0} Online
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <div className="modal-backdrop" onClick={() => setShowCreate(false)}>
          <div className="modal-panel" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 style={{ fontWeight: 600 }}>Create New Lab</h3>
              <button className="btn-icon" onClick={() => setShowCreate(false)}>✕</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Lab Name</label>
                  <input className="input" required value={newLab.name}
                    onChange={e => setNewLab({...newLab, name: e.target.value})} placeholder="e.g. Lab 1" />
                </div>
                <div className="form-group">
                  <label>Description (optional)</label>
                  <input className="input" value={newLab.description}
                    onChange={e => setNewLab({...newLab, description: e.target.value})} placeholder="e.g. Main computer lab" />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Lab</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default LabsPage;
