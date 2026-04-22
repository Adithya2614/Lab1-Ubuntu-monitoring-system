import React from 'react';
import { HardDrive, Cpu, Activity, Wifi } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const PCCard = ({ node }) => {
    const navigate = useNavigate();

    // Parse facts if available or default
    const ram = node.facts?.ram_percentage || '0%';
    const disk = node.facts?.disk_percentage || '0%';
    const online = node.status === 'online';

    return (
        <div className="card" onClick={() => navigate(`/node/${node.id}`)} style={{ cursor: 'pointer' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0 }}>{node.name}</h3>
                <div className={`status-badge ${online ? 'status-online' : 'status-offline'}`}>
                    <Wifi size={14} /> {online ? 'Online' : 'Offline'}
                </div>
            </div>

            <div style={{ display: 'grid', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                    <Cpu size={16} /> <span style={{ flex: 1 }}>CPU Load</span> <span>{node.facts?.cpu_load || '0.00'}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                    <Activity size={16} /> <span style={{ flex: 1 }}>RAM</span> <span>{ram}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                    <HardDrive size={16} /> <span style={{ flex: 1 }}>Disk</span> <span>{disk}</span>
                </div>
            </div>

            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Last Updated: {new Date().toLocaleTimeString()}
            </div>

            {/* Verified Status Overlay */}
            {node.verificationStatus && (
                <div className={`verified-overlay ver-${node.verificationStatus}`}>
                    {node.verificationStatus}
                </div>
            )}
        </div>
    );
};

export default PCCard;
