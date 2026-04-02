/**
 * ReconScan API Client
 */

const API_BASE = '/api/v1';

const API = {
    // Scan endpoints
    async createScan(data) {
        const response = await fetch(`${API_BASE}/scan/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async getScan(scanId) {
        const response = await fetch(`${API_BASE}/scan/${scanId}`);
        return response.json();
    },

    async getScanHistory(limit = 50, scanType = '') {
        const params = new URLSearchParams({ limit, scan_type: scanType });
        const response = await fetch(`${API_BASE}/scan/history?${params}`);
        return response.json();
    },

    async deleteScan(scanId) {
        const response = await fetch(`${API_BASE}/scan/${scanId}`, {
            method: 'DELETE'
        });
        return response.json();
    },

    // Health check
    async healthCheck() {
        const response = await fetch('/health');
        return response.json();
    }
};

// Helper functions
function createScanRequest(scanType, query, options = {}) {
    return {
        scan_type: scanType,
        query: query,
        timeout: options.timeout || 10,
        concurrent: options.concurrent || 10,
        deep_scan: options.deepScan || false
    };
}