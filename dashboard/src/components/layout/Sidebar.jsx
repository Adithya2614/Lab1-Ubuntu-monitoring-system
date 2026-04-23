/**
 * Sidebar — Collapsible navigation with lab listing.
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAppContext } from '../../context/AppContext';
import {
  LayoutDashboard, Monitor, FlaskConical, Activity, Zap,
  Bell, BarChart3, Settings, ChevronLeft, ChevronRight, Plus,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/pcs', icon: Monitor, label: 'PCs' },
  { to: '/labs', icon: FlaskConical, label: 'Labs' },
  { to: '/monitoring', icon: Activity, label: 'Monitoring' },
  { to: '/actions', icon: Zap, label: 'Actions' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/reports', icon: BarChart3, label: 'Reports' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

const Sidebar = () => {
  const {
    sidebarCollapsed, setSidebarCollapsed,
    sidebarMobileOpen, setSidebarMobileOpen,
    unreadCount,
  } = useAppContext();

  const cls = `sidebar ${sidebarCollapsed ? 'collapsed' : ''} ${sidebarMobileOpen ? 'mobile-open' : ''}`;

  return (
    <>
      {/* Mobile overlay */}
      {sidebarMobileOpen && (
        <div className="fixed inset-0 bg-black/50 z-30 md:hidden"
             onClick={() => setSidebarMobileOpen(false)} />
      )}

      <aside className={cls}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <Monitor size={18} />
          </div>
          <span className="sidebar-title">WMI Monitor</span>
          <button
            className="btn-icon ml-auto hidden lg:flex"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            style={{ marginLeft: 'auto' }}
          >
            {sidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-title">Navigation</div>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarMobileOpen(false)}
            >
              <Icon size={20} />
              <span>{label}</span>
              {label === 'Alerts' && unreadCount > 0 && (
                <span className="nav-badge">{unreadCount}</span>
              )}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
