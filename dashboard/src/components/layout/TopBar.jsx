/**
 * TopBar — Top navigation bar with search, notifications, and theme toggle.
 */

import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { Search, Bell, Sun, Moon, Menu, Plus } from 'lucide-react';

const TopBar = () => {
  const {
    theme, toggleTheme, sidebarCollapsed,
    setSidebarMobileOpen, setIsAddPCModalOpen,
    unreadCount, notifications, clearUnread,
  } = useAppContext();
  const [showNotifs, setShowNotifs] = useState(false);

  return (
    <header className={`topbar ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <div className="topbar-left">
        <button className="btn-icon lg:hidden"
                onClick={() => setSidebarMobileOpen(true)}>
          <Menu size={20} />
        </button>
        <div className="search-box">
          <Search />
          <input type="text" placeholder="Search PCs, labs, alerts..." />
        </div>
      </div>

      <div className="topbar-right">
        <button className="btn btn-primary btn-sm"
                onClick={() => setIsAddPCModalOpen(true)}>
          <Plus size={16} /> Add PC
        </button>

        <div style={{ position: 'relative' }}>
          <button className="btn-icon notification-btn"
                  onClick={() => { setShowNotifs(!showNotifs); clearUnread(); }}>
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className="notification-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
            )}
          </button>

          {showNotifs && (
            <div style={{
              position: 'absolute', right: 0, top: '100%', marginTop: '0.5rem',
              width: '320px', maxHeight: '400px', overflowY: 'auto',
              background: 'var(--bg-card)', border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-lg)',
              zIndex: 50, animation: 'slideUp 0.2s ease-out',
            }}>
              <div style={{ padding: '0.75rem 1rem', borderBottom: '1px solid var(--border)',
                            fontWeight: 600, fontSize: '0.875rem' }}>
                Notifications
              </div>
              {notifications.length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No notifications
                </div>
              ) : (
                notifications.slice(0, 10).map(n => (
                  <div key={n.id} style={{
                    padding: '0.75rem 1rem', borderBottom: '1px solid var(--border)',
                    fontSize: '0.8125rem',
                  }}>
                    <div style={{ color: 'var(--text-primary)' }}>{n.message}</div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                      {n.timestamp?.toLocaleTimeString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <button className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
};

export default TopBar;
