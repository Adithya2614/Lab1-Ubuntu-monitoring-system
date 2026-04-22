const API_BASE = "http://localhost:8000/api";

export const api = {
    getNodes: async () => {
        const res = await fetch(`${API_BASE}/nodes`);
        return res.json();
    },

    runAction: async (target, actionType, params = {}) => {
        const res = await fetch(`${API_BASE}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, action_type: actionType, parameters: params })
        });
        return res.json();
    },

    addNode: async (nodeData) => {
        const res = await fetch(`${API_BASE}/nodes/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nodeData)
        });
        return res.json();
    },

    getAuditLogs: async () => {
        const res = await fetch(`${API_BASE}/audit`);
        return res.json();
    }
};
