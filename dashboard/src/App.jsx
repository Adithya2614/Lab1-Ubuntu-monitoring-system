/**
 * WMI Dashboard — Root Application Component
 * =============================================
 * Sets up routing, providers, and the app shell layout.
 * Preserves backward-compatible routes (/node/:id → PCDetail).
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AppProvider, useAppContext } from './context/AppContext';

// Layout
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';

// Pages
import DashboardPage from './pages/DashboardPage';
import PCsPage from './pages/PCsPage';
import LabsPage from './pages/LabsPage';
import MonitoringPage from './pages/MonitoringPage';
import ActionsPage from './pages/ActionsPage';
import AlertsPage from './pages/AlertsPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';

// Existing components (backward compat)
import PCDetail from './components/PCDetail';
import AddPCModal from './components/AddPCModal';

/** App shell layout with sidebar + topbar */
const AppShell = ({ children }) => {
  const { sidebarCollapsed } = useAppContext();
  return (
    <div className="app-shell">
      <Sidebar />
      <div className={`app-main ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <TopBar />
        <main className="app-content">
          {children}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AppProvider>
      <Router>
        <AppShell>
          <Routes>
            {/* Main pages */}
            <Route path="/" element={<DashboardPage />} />
            <Route path="/pcs" element={<PCsPage />} />
            <Route path="/labs" element={<LabsPage />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
            <Route path="/actions" element={<ActionsPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/settings" element={<SettingsPage />} />

            {/* PC Detail — backward-compatible route */}
            <Route path="/node/:id" element={<PCDetail />} />

            {/* Backward compat: old audit route */}
            <Route path="/audit" element={<Navigate to="/reports" replace />} />
          </Routes>

          {/* Global modals */}
          <AddPCModal />
        </AppShell>
      </Router>

      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.875rem',
          },
          success: { iconTheme: { primary: 'var(--success)', secondary: 'white' } },
          error: { iconTheme: { primary: 'var(--danger)', secondary: 'white' } },
        }}
      />
    </AppProvider>
  );
}

export default App;
