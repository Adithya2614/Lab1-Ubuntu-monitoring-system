import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import {
    Terminal, FileText, AppWindow, Wifi, RefreshCw,
    Cpu, Activity, HardDrive, Clock, ArrowLeft,
    Monitor, Globe, Lock, Play, Folder, File, Search, Trash2, ArrowUp,
    Shield, ShieldAlert, Archive, RotateCcw
} from 'lucide-react';

const PCDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('overview');
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);

    // Metrics state
    const [metrics, setMetrics] = useState({
        uptime: '-',
        cpu_load: '0.00',
        ram_used: '0',
        ram_total: '0',
        ram_percent: 0,
        disk_usage: '0%',
        disk_percent: 0
    });

    // State for modules
    const [files, setFiles] = useState([]);
    const [currentPath, setCurrentPath] = useState('/home');
    const [selectedFiles, setSelectedFiles] = useState([]);

    const [packages, setPackages] = useState([]);
    const [selectedApps, setSelectedApps] = useState([]);

    const [vaultManifest, setVaultManifest] = useState([]);

    // Controls State
    const [internetStatus, setInternetStatus] = useState('Unknown');
    const [browserStatus, setBrowserStatus] = useState('Unknown');

    // Parse Metrics
    const parseMetrics = (data) => {
        try {
            if (data && data.plays && data.plays[0] && data.plays[0].tasks) {
                const tasks = data.plays[0].tasks;
                const metricsTask = tasks.find(t => t.task && t.task.name === 'Return Metrics');
                if (metricsTask && metricsTask.hosts && metricsTask.hosts[id]) {
                    const msg = metricsTask.hosts[id].msg;
                    if (msg) {
                        // Calculate percents
                        let ram_p = 0;
                        try {
                            const used = parseInt(msg.ram_used || 0);
                            const total = parseInt(msg.ram_total || 1);
                            ram_p = Math.round((used / total) * 100);
                        } catch (e) { }

                        let disk_p = 0;
                        try {
                            disk_p = parseInt((msg.disk_usage || '0%').replace('%', ''));
                        } catch (e) { }

                        setMetrics({
                            uptime: msg.uptime || '-',
                            cpu_load: msg.cpu_load || '0.00',
                            ram_used: msg.ram_used || '0',
                            ram_total: msg.ram_total || '0',
                            ram_percent: ram_p,
                            disk_usage: msg.disk_usage || '0%',
                            disk_percent: disk_p
                        });
                    }
                }
            }
        } catch (e) {
            console.error("Error parsing metrics:", e);
        }
    };

    // Search state
    const [fileSearchTerm, setFileSearchTerm] = useState('');
    const [appSearchTerm, setAppSearchTerm] = useState('');

    const handleAction = async (actionType, params = {}) => {
        setLoading(true);
        try {
            // Optimistic updates for controls
            if (actionType === 'update_internet') setInternetStatus(params.state === 'enabled' ? 'Enabled' : 'Disabled');
            if (actionType === 'update_internet') setInternetStatus(params.state === 'enabled' ? 'Enabled' : 'Disabled');
            if (actionType === 'manage_browsers') setBrowserStatus(params.action === 'block' ? 'Blocked' : 'Active');

            const res = await api.runAction(id, actionType, params);
            setLogs(prev => [`[${new Date().toLocaleTimeString()}] Action ${actionType}: ${res.status}`, ...prev]);

            if (res.status === 'success' && res.data) {
                if (actionType === 'collect_metrics') parseMetrics(res.data);
                if (actionType === 'list_files') {
                    setFiles(res.data);
                    setSelectedFiles([]); // Clear selection on new list
                }
                if (actionType === 'list_packages') {
                    setPackages(res.data);
                    setSelectedApps([]); // Clear selection
                }
                if (actionType === 'archive_files' || actionType === 'get_vault') {
                    setVaultManifest(res.data || []);
                }
                if (actionType === 'restore_files') {
                    setVaultManifest([]);
                }
            }
            return res;
        } catch (e) {
            console.error(e);
            setLogs(prev => [`Error: ${e.message}`, ...prev]);
        } finally {
            setLoading(false);
        }
    };

    // File Navigation
    const navigateDir = (dirName) => {
        let newPath = currentPath;
        if (!newPath.endsWith('/')) newPath += '/';
        newPath += dirName;
        setCurrentPath(newPath);
        handleAction('list_files', { path: newPath });
    };

    const goUpDir = () => {
        // Simple logic to go up one level
        const parts = currentPath.split('/').filter(p => p);
        parts.pop();
        const newPath = '/' + parts.join('/');
        setCurrentPath(newPath || '/'); // Default to root if empty
        handleAction('list_files', { path: newPath || '/' });
    };

    // Deletion Handlers
    const deleteSelectedFiles = async () => {
        if (!confirm(`Are you sure you want to delete ${selectedFiles.length} file(s)?`)) return;

        // Assuming delete_files playbook takes a list of full paths
        const filesToDelete = selectedFiles.map(name => {
            let path = currentPath;
            if (!path.endsWith('/')) path += '/';
            return path + name;
        });

        await handleAction('delete_files', { files: filesToDelete });
        handleAction('list_files', { path: currentPath }); // Refresh
    };

    const uninstallSelectedApps = async () => {
        if (!confirm(`Are you sure you want to uninstall ${selectedApps.length} application(s)?`)) return;

        await handleAction('remove_package', { packages: selectedApps });
        handleAction('list_packages'); // Refresh
    };

    // Selection Toggles
    const toggleFile = (name) => {
        setSelectedFiles(prev =>
            prev.includes(name) ? prev.filter(f => f !== name) : [...prev, name]
        );
    };

    const toggleApp = (name) => {
        setSelectedApps(prev =>
            prev.includes(name) ? prev.filter(a => a !== name) : [...prev, name]
        );
    };


    // Initial Load
    useEffect(() => {
        handleAction('collect_metrics');
        handleAction('get_vault');
    }, [id]);

    // Renders
    const renderOverview = () => (
        <div className="tab-content active">
            <div className="metrics-grid">
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">CPU Load</span>
                        <Cpu size={20} />
                    </div>
                    <div className="metric-value">{metrics.cpu_load}</div>
                    <div className="metric-bar">
                        <div className="metric-fill cpu" style={{ width: `${Math.min(parseFloat(metrics.cpu_load) * 20, 100)}%` }}></div>
                    </div>
                </div>
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">RAM Usage</span>
                        <Activity size={20} />
                    </div>
                    <div className="metric-value">{metrics.ram_used} / {metrics.ram_total} MB</div>
                    <div className="metric-bar">
                        <div className="metric-fill ram" style={{ width: `${metrics.ram_percent}%` }}></div>
                    </div>
                </div>
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">Disk Usage</span>
                        <HardDrive size={20} />
                    </div>
                    <div className="metric-value">{metrics.disk_usage}</div>
                    <div className="metric-bar">
                        <div className="metric-fill disk" style={{ width: `${metrics.disk_percent}%` }}></div>
                    </div>
                </div>
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">Uptime</span>
                        <Clock size={20} />
                    </div>
                    <div className="metric-value" style={{ fontSize: '1.25rem' }}>{metrics.uptime}</div>
                </div>
            </div>

            <div className="info-grid">
                <div className="info-card">
                    <h4>System Information</h4>
                    <div className="info-list">
                        <div className="info-item">
                            <span className="info-label">OS</span>
                            <span className="info-value">Ubuntu / Linux</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Node ID</span>
                            <span className="info-value">{id}</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Status</span>
                            <span className="info-value" style={{ color: 'var(--success)' }}>Active</span>
                        </div>
                    </div>
                </div>
                <div className="info-card">
                    <h4>Network</h4>
                    <div className="info-list">
                        <div className="info-item">
                            <span className="info-label">Type</span>
                            <span className="info-value">LAN / SSH</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Internet</span>
                            <span className="info-value">{internetStatus}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderFiles = () => {
        const filteredFiles = files.filter(f => f.name.toLowerCase().includes(fileSearchTerm.toLowerCase()));

        return (
            <div className="tab-content active">
                <div className="card" style={{ padding: '1.5rem' }}>
                    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                        <button className="btn btn-secondary" onClick={goUpDir} title="Go Up"><ArrowUp size={16} /></button>
                        <input
                            className="text-input"
                            value={currentPath}
                            onChange={e => setCurrentPath(e.target.value)}
                            style={{ flex: 1, minWidth: '200px' }}
                        />
                        <div style={{ position: 'relative' }}>
                            <input
                                className="text-input"
                                placeholder="Search files..."
                                value={fileSearchTerm}
                                onChange={(e) => setFileSearchTerm(e.target.value)}
                                style={{ paddingLeft: '2rem', width: '200px' }}
                            />
                            <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                        </div>
                        <button className="btn btn-secondary" onClick={() => handleAction('list_files', { path: currentPath })}>Go</button>
                        <button className="btn btn-primary" onClick={() => handleAction('list_files', { path: currentPath })}>Refresh</button>
                        <button
                            className="btn btn-danger"
                            onClick={deleteSelectedFiles}
                            disabled={selectedFiles.length === 0}
                        >
                            <Trash2 size={16} /> Delete ({selectedFiles.length})
                        </button>
                    </div>
                    <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th style={{ width: '30px' }}><input type="checkbox" onChange={(e) => {
                                        if (e.target.checked) setSelectedFiles(filteredFiles.map(f => f.name));
                                        else setSelectedFiles([]);
                                    }} /></th>
                                    <th style={{ width: '30px' }}></th>
                                    <th>Name</th>
                                    <th>Size</th>
                                    <th>Modified</th>
                                    <th>Perms</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredFiles.length === 0 ? (
                                    <tr><td colSpan="6" style={{ textAlign: 'center', padding: '2rem' }}>No files listed. Click Refresh.</td></tr>
                                ) : (
                                    filteredFiles.map((f, i) => (
                                        <tr key={i} className={selectedFiles.includes(f.name) ? 'selected-row' : ''}>
                                            <td>
                                                <input
                                                    type="checkbox"
                                                    checked={selectedFiles.includes(f.name)}
                                                    onChange={() => toggleFile(f.name)}
                                                />
                                            </td>
                                            <td>{f.type === 'directory' ? <Folder size={16} color="var(--accent)" /> : <File size={16} />}</td>
                                            <td>
                                                {f.type === 'directory' ? (
                                                    <span
                                                        style={{ color: 'var(--accent)', cursor: 'pointer', fontWeight: 500 }}
                                                        onClick={() => navigateDir(f.name)}
                                                    >
                                                        {f.name}
                                                    </span>
                                                ) : (
                                                    <span>{f.name}</span>
                                                )}
                                            </td>
                                            <td>{f.size}</td>
                                            <td>{f.modified}</td>
                                            <td>{f.permissions}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    }

    const renderApps = () => {
        const filteredApps = packages.filter(p => p.name.toLowerCase().includes(appSearchTerm.toLowerCase()));

        return (
            <div className="tab-content active">
                <div className="card" style={{ padding: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', gap: '0.5rem', flex: 1 }}>
                            <div style={{ position: 'relative', flex: 1 }}>
                                <input
                                    className="text-input"
                                    placeholder="Search packages..."
                                    value={appSearchTerm}
                                    onChange={(e) => setAppSearchTerm(e.target.value)}
                                    style={{ paddingLeft: '2rem', width: '100%' }}
                                />
                                <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                            </div>
                            <button className="btn btn-primary" onClick={() => handleAction('list_packages')}>Refresh List</button>
                            <button
                                className="btn btn-danger"
                                onClick={uninstallSelectedApps}
                                disabled={selectedApps.length === 0}
                            >
                                <Trash2 size={16} /> Uninstall ({selectedApps.length})
                            </button>
                        </div>
                    </div>
                    <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th style={{ width: '30px' }}><input type="checkbox" onChange={(e) => {
                                        if (e.target.checked) setSelectedApps(filteredApps.map(p => p.name));
                                        else setSelectedApps([]);
                                    }} /></th>
                                    <th>Name</th>
                                    <th>Version</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredApps.length === 0 ? (
                                    <tr><td colSpan="4" style={{ textAlign: 'center', padding: '2rem' }}>No packages listed. Click Refresh.</td></tr>
                                ) : (
                                    filteredApps.map((p, i) => (
                                        <tr key={i} className={selectedApps.includes(p.name) ? 'selected-row' : ''}>
                                            <td>
                                                <input
                                                    type="checkbox"
                                                    checked={selectedApps.includes(p.name)}
                                                    onChange={() => toggleApp(p.name)}
                                                />
                                            </td>
                                            <td style={{ fontWeight: 500 }}>{p.name}</td>
                                            <td>{p.version}</td>
                                            <td><span style={{ padding: '0.25rem 0.5rem', borderRadius: '1rem', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--success)', fontSize: '0.75rem' }}>{p.status}</span></td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    }

    const renderControls = () => (
        <div className="tab-content active">
            <div className="controls-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                <div className="control-card" style={{ background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid var(--border)' }}>
                    <div className="control-header" style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                        <Globe size={24} />
                        <h4>Internet Control</h4>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>Enable or disable internet access. LAN remains active.</p>
                    <div className="control-actions" style={{ display: 'flex', gap: '1rem' }}>
                        <button className="btn btn-success" onClick={() => handleAction('update_internet', { state: 'enabled' })}>Enable</button>
                        <button className="btn btn-danger" onClick={() => handleAction('update_internet', { state: 'disabled' })}>Disable</button>
                    </div>
                </div>

                <div className="control-card" style={{ background: 'var(--bg-card)', padding: '1.5rem', borderRadius: '0.75rem', border: '1px solid var(--border)' }}>
                    <div className="control-header" style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                        <Lock size={24} />
                        <h4>Browser Control</h4>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>Prevent browsers from opening (Blocks Execution). Internet remains available for other apps.</p>
                    <div className="control-actions" style={{ display: 'flex', gap: '1rem' }}>
                        <button className="btn btn-danger" onClick={() => handleAction('manage_browsers', { action: 'block' })}>Block Browsers</button>
                        <button className="btn btn-success" onClick={() => handleAction('manage_browsers', { action: 'unblock' })}>Unblock Browsers</button>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderVault = () => (
        <div className="tab-content active">
            <div className="card" style={{ padding: '1.5rem', border: '1px solid var(--border)', background: 'var(--bg-card)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <div>
                        <h4 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>Secure File Vault</h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                            Archive sensitive files to a hidden location on this PC.
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <button className="btn btn-secondary" onClick={() => handleAction('get_vault')}>
                            <RefreshCw size={16} /> Refresh
                        </button>
                        <button className="btn btn-primary" onClick={() => handleAction('archive_files')}>
                            <Archive size={16} /> Archive All Non-Whitelisted
                        </button>
                        <button className="btn btn-success" onClick={() => handleAction('restore_files')}>
                            <RotateCcw size={16} /> Restore All
                        </button>
                    </div>
                </div>

                <div className="vault-status" style={{
                    padding: '1rem',
                    background: vaultManifest.length > 0 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(34, 197, 94, 0.1)',
                    borderRadius: '0.5rem',
                    color: vaultManifest.length > 0 ? '#ef4444' : '#22c55e',
                    marginBottom: '1.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    border: '1px solid currentColor'
                }}>
                    {vaultManifest.length > 0 ? <ShieldAlert size={20} /> : <Shield size={20} />}
                    <span style={{ fontWeight: 600 }}>
                        {vaultManifest.length > 0 ? `SECURITY ALERT: ${vaultManifest.length} Files Archived & Hidden` : 'VAULT STATUS: Empty (All files in original locations)'}
                    </span>
                </div>

                {vaultManifest.length > 0 && (
                    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                        <table className="vault-table">
                            <thead>
                                <tr>
                                    <th>File Name</th>
                                    <th>Original Path</th>
                                    <th>Stored Name (Encrypted)</th>
                                    <th>Archived At</th>
                                </tr>
                            </thead>
                            <tbody>
                                {vaultManifest.map((item, i) => (
                                    <tr key={i}>
                                        <td style={{ fontWeight: 500 }}><File size={14} style={{ marginRight: '0.5rem', display: 'inline' }} /> {item.name}</td>
                                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{item.path}</td>
                                        <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{item.stored_as}</td>
                                        <td><span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{item.timestamp}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );

    return (
        <section id="pc-detail-view" className="view active">
            <div className="detail-header">
                <button className="btn btn-icon" onClick={() => navigate('/')}>
                    <ArrowLeft size={20} />
                </button>
                <div style={{ flex: 1 }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>{id}</h2>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                        <div className="status-badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', padding: '0.25rem 0.75rem', borderRadius: '1rem', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--success)', fontSize: '0.75rem' }}>
                            <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor' }}></div>
                            Online
                        </div>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Last updated: {new Date().toLocaleTimeString()}</span>
                    </div>
                </div>
                <div className="detail-status">
                    <button className="btn btn-secondary" onClick={() => handleAction('collect_metrics')}>
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Refresh Data
                    </button>
                </div>
            </div>

            <div className="detail-content">
                <div className="detail-tabs">
                    {['overview', 'files', 'apps', 'controls', 'vault'].map(tab => (
                        <button
                            key={tab}
                            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab)}
                            style={{ textTransform: 'capitalize' }}
                        >
                            {tab}
                        </button>
                    ))}
                </div>

                <div className="animate-fade-in">
                    {activeTab === 'overview' && renderOverview()}
                    {activeTab === 'files' && renderFiles()}
                    {activeTab === 'apps' && renderApps()}
                    {activeTab === 'controls' && renderControls()}
                    {activeTab === 'vault' && renderVault()}
                </div>
            </div>

            <div className="card" style={{ marginTop: '2rem', background: 'var(--bg-card)', padding: '1rem', borderRadius: '0.75rem', border: '1px solid var(--border)' }}>
                <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Session Logs</h3>
                <div style={{ maxHeight: '150px', overflowY: 'auto', background: 'var(--bg-dark)', padding: '0.5rem', borderRadius: '0.5rem', fontFamily: 'monospace', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    {logs.map((log, i) => <div key={i}>{log}</div>)}
                </div>
            </div>
        </section>
    );
};

export default PCDetail;
