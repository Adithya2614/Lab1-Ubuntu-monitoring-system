import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import { useAppContext } from '../context/AppContext';
import { Globe, Lock, Cpu, Database, HardDrive, Wifi, Radio, Shield, Archive, RotateCcw, Trash2, AppWindow, RefreshCw, Clock, FileText, X } from 'lucide-react';

const Dashboard = () => {
    const navigate = useNavigate();
    const { viewMode } = useAppContext();
    const [nodes, setNodes] = useState([]);
    const [stats, setStats] = useState({ total: 0, online: 0, offline: 0 });
    const [logs, setLogs] = useState([]);
    const [isLogsModalOpen, setIsLogsModalOpen] = useState(false);
    const [isActionRunning, setIsActionRunning] = useState(false);

    useEffect(() => {
        fetchNodes();
        const interval = setInterval(fetchNodes, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchNodes = async () => {
        try {
            const data = await api.getNodes();
            setNodes(data.nodes || []);

            // Calculate stats
            const total = data.nodes.length;
            const online = data.nodes.filter(n => n.status === 'online').length;
            setStats({ total, online, offline: total - online });
        } catch (e) {
            console.error("Failed to fetch nodes", e);
        }
    };

    const fetchLogs = async () => {
        try {
            const data = await api.getAuditLogs();
            setLogs(data.logs || []);
            setIsLogsModalOpen(true);
        } catch (e) {
            console.error("Failed to fetch logs", e);
        }
    };

    const handleGlobalAction = async (action, params) => {
        const onlineNodes = nodes.filter(n => n.status === 'online');
        if (onlineNodes.length === 0) {
            alert("No online nodes detected to target.");
            return;
        }

        if (!confirm(`Are you sure you want to trigger ${action} on ALL ${onlineNodes.length} online nodes?`)) return;

        setIsActionRunning(true);

        const actionMap = {
            'internet': 'update_internet',
            'browsers': 'manage_browsers',
            'archive': 'archive_files',
            'restore': 'restore_files',
            'cleanup': 'cleanup_apps',
            'sync_time': 'sync_time',
            'restrict': 'restrict_websites'
        };

        const actionType = actionMap[action];

        try {
            // Run actions in parallel
            const results = await Promise.allSettled(
                onlineNodes.map(node => api.runAction(node.id, actionType, params))
            );

            const successCount = results.filter(r => r.status === 'fulfilled').length;
            const failCount = results.length - successCount;

            alert(`Global ${action} finished.\nSuccess: ${successCount}\nFailed: ${failCount}`);

            // Refresh nodes to see changes
            await fetchNodes();

            // If it was a cleanup, show logs immediately to see what was removed
            if (action === 'cleanup') {
                fetchLogs();
            }
        } catch (e) {
            console.error("Global action failed", e);
            alert("Global execution encountered an error.");
        } finally {
            setIsActionRunning(false);
        }
    };

    return (
        <section id="dashboard-view" className="view active animate-fade-in">
            <div className="content-header">
                <h2>Monitored PCs</h2>
                <div className="stats-bar">
                    <div className="stat">
                        <span className="stat-value">{stats.total}</span>
                        <span className="stat-label">Total</span>
                    </div>
                    <div className="stat online">
                        <span className="stat-value">{stats.online}</span>
                        <span className="stat-label">Online</span>
                    </div>
                    <div className="stat offline">
                        <span className="stat-value">{stats.offline}</span>
                        <span className="stat-label">Offline</span>
                    </div>
                </div>
            </div>

            {/* Global Controls Panel */}
            <div className="global-controls-panel">
                <h3>Global Controls</h3>
                <p className="global-controls-desc">Apply controls to all registered PCs</p>
                <div className="global-controls-grid">
                    <div className="global-control">
                        <span className="global-control-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Globe size={16} /> Internet
                        </span>
                        <div className="global-control-buttons">
                            <button className="btn btn-success btn-sm" onClick={() => handleGlobalAction('internet', { state: 'enabled' })}>Enable All</button>
                            <button className="btn btn-danger btn-sm" onClick={() => handleGlobalAction('internet', { state: 'disabled' })}>Disable All</button>
                        </div>
                    </div>
                    <div className="global-control">
                        <span className="global-control-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Lock size={16} /> Browsers
                        </span>
                        <div className="global-control-buttons">
                            <button className="btn btn-success btn-sm" onClick={() => handleGlobalAction('browsers', { action: 'unblock' })}>Enable All</button>
                            <button className="btn btn-danger btn-sm" onClick={() => handleGlobalAction('browsers', { action: 'block' })}>Disable All</button>
                        </div>
                    </div>
                    <div className="global-control">
                        <span className="global-control-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Shield size={16} /> Secure Vault
                        </span>
                        <div className="global-control-buttons">
                            <button className="btn btn-primary btn-sm" onClick={() => handleGlobalAction('archive')}>
                                <Archive size={14} style={{ marginRight: '4px' }} /> Archive All
                            </button>
                            <button className="btn btn-success btn-sm" onClick={() => handleGlobalAction('restore')}>
                                <RotateCcw size={14} style={{ marginRight: '4px' }} /> Restore All
                            </button>
                        </div>
                    </div>
                    <div className="global-control">
                        <span className="global-control-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Globe size={16} /> Web Filter
                        </span>
                        <div className="global-control-buttons">
                            <button className="btn btn-danger btn-sm" onClick={() => handleGlobalAction('restrict', { target_state: 'restrict' })}>Lockdown</button>
                            <button className="btn btn-success btn-sm" onClick={() => handleGlobalAction('restrict', { target_state: 'restore' })}>Restore</button>
                        </div>
                    </div>
                    <div className="global-control">
                        <span className="global-control-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Clock size={16} /> Time & Region
                        </span>
                        <div className="global-control-buttons">
                            <button className="btn btn-success btn-sm" onClick={() => handleGlobalAction('sync_time')}>
                                <RefreshCw size={14} style={{ marginRight: '4px' }} /> Sync All
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className={`pc-grid ${viewMode === 'list' ? 'list-view' : ''}`} style={viewMode === 'list' ? { display: 'flex', flexDirection: 'column' } : {}}>
                {nodes.length === 0 ? (
                    <div className="empty-state" style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                        <div style={{ marginBottom: '1rem' }}><HardDrive size={48} /></div>
                        <h3>No PCs Registered</h3>
                        <p>Click "Add PC" to start monitoring computers</p>
                    </div>
                ) : (
                    nodes.map(node => (
                        <div key={node.id} className="pc-card" onClick={() => navigate(`/node/${node.id}`)}>
                            <div className="pc-header">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <div style={{ padding: '0.5rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '0.5rem', color: 'var(--accent)' }}>
                                        <Radio size={20} />
                                    </div>
                                    <div className="pc-name">{node.name}</div>
                                </div>
                                <div className={`pc-status ${node.status === 'online' ? 'online' : 'offline'}`}>
                                    {node.status === 'online' ? 'Online' : 'Offline'}
                                </div>
                            </div>

                            <div className="pc-metrics">
                                <div className="pc-metric">
                                    <span className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                        <Cpu size={12} /> CPU
                                    </span>
                                    <span className="metric-val">{node.facts?.cpu_load || '0.00'}</span>
                                </div>
                                <div className="pc-metric">
                                    <span className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                        <Database size={12} /> RAM
                                    </span>
                                    <span className="metric-val">{node.facts?.ram_percentage || '0%'}</span>
                                </div>
                                <div className="pc-metric">
                                    <span className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                        <HardDrive size={12} /> HDD
                                    </span>
                                    <span className="metric-val">{node.facts?.disk_percentage || '0%'}</span>
                                </div>
                                <div className="pc-metric">
                                    <span className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                        <Wifi size={12} /> Net
                                    </span>
                                    <span className="metric-val">{node.status === 'online' ? 'Conn' : 'Disc'}</span>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Logs Modal */}
            {
                isLogsModalOpen && (
                    <div className="modal-overlay" onClick={() => setIsLogsModalOpen(false)}>
                        <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '800px', width: '90%' }}>
                            <div className="modal-header">
                                <h3><FileText size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} /> App Removal Audit Logs</h3>
                                <button className="close-btn" onClick={() => setIsLogsModalOpen(false)}><X size={20} /></button>
                            </div>
                            <div className="modal-body" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
                                {logs.length === 0 ? (
                                    <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>No removal records found.</p>
                                ) : (
                                    <div className="logs-list">
                                        {logs.map((log, index) => (
                                            <div key={index} className="log-item" style={{
                                                padding: '1rem',
                                                borderBottom: '1px solid var(--border)',
                                                background: index % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent'
                                            }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                    <strong style={{ color: 'var(--accent)' }}>{log.pc}</strong>
                                                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{log.timestamp}</span>
                                                </div>
                                                <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', wordBreak: 'break-all' }}>
                                                    <span style={{ color: 'var(--text-secondary)', marginRight: '4px' }}>Removed:</span>
                                                    {log.removed}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                            <div className="modal-footer">
                                <button className="btn btn-secondary" onClick={() => setIsLogsModalOpen(false)}>Close</button>
                            </div>
                        </div>
                    </div>
                )
            }
            {/* Action Loading Overlay */}
            {
                isActionRunning && (
                    <div className="modal-overlay" style={{ background: 'rgba(0, 0, 0, 0.8)', zIndex: 9999 }}>
                        <div style={{ textAlign: 'center' }}>
                            <div className="animate-spin" style={{ marginBottom: '1rem', color: 'var(--accent)' }}>
                                <RefreshCw size={48} />
                            </div>
                            <h2>Processing Global Action...</h2>
                            <p style={{ color: 'var(--text-secondary)' }}>Syncing with workstations...</p>
                        </div>
                    </div>
                )
            }
        </section >
    );
};

export default Dashboard;
