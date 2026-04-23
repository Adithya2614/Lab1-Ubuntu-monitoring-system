/**
 * WMI API Client
 * Centralized fetch wrapper with error handling.
 * Base URL uses Vite proxy in dev, direct URL in production.
 */

const API_BASE = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // --- Nodes (backward-compatible) ---
  getNodes: () => request('/nodes'),
  addNode: (data) => request('/nodes/add', { method: 'POST', body: JSON.stringify(data) }),
  deleteNode: (id) => request(`/nodes/${id}`, { method: 'DELETE' }),
  bulkAddNodes: (data) => request('/nodes/bulk-add', { method: 'POST', body: JSON.stringify(data) }),
  bulkAddCSV: (file) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${API_BASE}/nodes/bulk-add/csv`, { method: 'POST', body: form }).then(r => r.json());
  },
  assignLab: (data) => request('/nodes/assign-lab', { method: 'POST', body: JSON.stringify(data) }),

  // --- Actions (backward-compatible) ---
  runAction: (target, actionType, params = {}) =>
    request('/action', { method: 'POST', body: JSON.stringify({ target, action_type: actionType, parameters: params }) }),
  runBulkAction: (targets, actionType, params = {}) =>
    request('/actions/bulk', { method: 'POST', body: JSON.stringify({ targets, action_type: actionType, parameters: params }) }),

  // --- Labs ---
  getLabs: () => request('/labs'),
  createLab: (data) => request('/labs', { method: 'POST', body: JSON.stringify(data) }),
  getLab: (id) => request(`/labs/${id}`),
  updateLab: (id, data) => request(`/labs/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteLab: (id) => request(`/labs/${id}`, { method: 'DELETE' }),
  saveLabLayout: (id, layout) => request(`/labs/${id}/layout`, { method: 'PUT', body: JSON.stringify(layout) }),

  // --- Alerts ---
  getAlerts: (params = '') => request(`/alerts${params ? '?' + params : ''}`),
  resolveAlert: (id) => request(`/alerts/${id}/resolve`, { method: 'POST' }),

  // --- Audit (backward-compatible) ---
  getAuditLogs: () => request('/audit'),

  // --- Metrics ---
  getMetricsHistory: (pcId, hours = 24) => request(`/metrics/${pcId}/history?hours=${hours}`),

  // --- Reports ---
  getReportOverview: () => request('/reports/overview'),
  getReportMetrics: (pcId, hours = 24) => request(`/reports/metrics/${pcId}?hours=${hours}`),

  // --- Settings ---
  getWhitelist: () => request('/settings/whitelist'),
  addWhitelist: (data) => request('/settings/whitelist', { method: 'POST', body: JSON.stringify(data) }),
  deleteWhitelist: (id) => request(`/settings/whitelist/${id}`, { method: 'DELETE' }),
  bulkImportWhitelist: (data) => request('/settings/whitelist/bulk', { method: 'POST', body: JSON.stringify(data) }),
  getBlockedApps: () => request('/settings/blocked-apps'),
  addBlockedApp: (data) => request('/settings/blocked-apps', { method: 'POST', body: JSON.stringify(data) }),
  deleteBlockedApp: (id) => request(`/settings/blocked-apps/${id}`, { method: 'DELETE' }),
  getSSHKeys: () => request('/settings/ssh-keys'),
  generateSSHKey: (data) => request('/settings/ssh-keys', { method: 'POST', body: JSON.stringify(data) }),
  deleteSSHKey: (id) => request(`/settings/ssh-keys/${id}`, { method: 'DELETE' }),
};
