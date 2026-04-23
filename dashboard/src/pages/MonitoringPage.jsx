/** MonitoringPage — Live metrics view. */
import React from 'react';
import { Activity } from 'lucide-react';

const MonitoringPage = () => (
  <div className="animate-fade-in">
    <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}>Live Monitoring</h1>
    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
      Real-time metrics via WebSocket — select a PC to view live data
    </p>
    <div className="empty-state">
      <Activity size={48} />
      <h3>Select a PC for live monitoring</h3>
      <p>Navigate to a PC detail page to see real-time metrics and charts</p>
    </div>
  </div>
);

export default MonitoringPage;
