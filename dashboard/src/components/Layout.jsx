import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { LayoutGrid, List, Plus, Monitor, FileText } from 'lucide-react';

const Layout = ({ children }) => {
    const { viewMode, setViewMode, setIsAddPCModalOpen } = useAppContext();
    const location = useLocation();
    const isDashboard = location.pathname === '/';

    return (
        <div className="app-container">
            {/* Status Indicator (Mock for now, could catch connection status later) */}
            <div id="status-indicator" className="status-indicator" style={{
                position: 'fixed', top: '1rem', left: '50%', transform: 'translateX(-50%)',
                background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', padding: '0.25rem 0.75rem',
                borderRadius: '1rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem',
                border: '1px solid rgba(34, 197, 94, 0.2)', zIndex: 100
            }}>
                <div className="status-dot" style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor' }}></div>
                <span className="status-text">System Active</span>
            </div>

            <header className="header">
                <div className="header-left">
                    <div className="logo">
                        <Monitor className="logo-icon" />
                        <h1>WMI Monitor</h1>
                    </div>
                </div>
                <nav className="header-nav">
                    <NavLink to="/" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}>
                        <LayoutGrid size={18} />
                        Dashboard
                    </NavLink>
                    <NavLink to="/audit" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}>
                        <FileText size={18} />
                        Audit Logs
                    </NavLink>
                </nav>
                <div className="header-right">
                    {isDashboard && (
                        <div className="view-toggle">
                            <button
                                className={`toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
                                onClick={() => setViewMode('grid')}
                                title="Grid View"
                            >
                                <LayoutGrid size={16} />
                            </button>
                            <button
                                className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
                                onClick={() => setViewMode('list')}
                                title="List View"
                            >
                                <List size={16} />
                            </button>
                        </div>
                    )}
                    <button className="btn btn-primary" onClick={() => setIsAddPCModalOpen(true)}>
                        <Plus size={16} />
                        Add PC
                    </button>
                </div>
            </header>

            <main className="main-content">
                {children}
            </main>
        </div>
    );
};

export default Layout;
