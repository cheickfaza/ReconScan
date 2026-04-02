/**
 * ReconScan Dashboard Application
 */

// State
let currentTab = 'dashboard';
let charts = {};

// DOM Elements
const navItems = document.querySelectorAll('.nav-item');
const tabContents = document.querySelectorAll('.tab-content');
const pageTitle = document.getElementById('page-title');

// Tab titles
const tabTitles = {
    'dashboard': 'Dashboard',
    'username': 'Recherche par Pseudo',
    'email': 'Recherche par Email',
    'deep-scan': 'Deep Scan',
    'correlation': 'Corrélation de Pseudos',
    'history': 'Historique des Scans'
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDashboard();
    initEventListeners();
    loadDashboardData();
});

// Navigation
function initNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tab = item.dataset.tab;
            switchTab(tab);
        });
    });
}

function switchTab(tab) {
    currentTab = tab;
    
    // Update nav
    navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.tab === tab);
    });
    
    // Update content
    tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tab}-tab`);
    });
    
    // Update title
    pageTitle.textContent = tabTitles[tab] || 'Dashboard';
    
    // Load tab data
    if (tab === 'dashboard') {
        loadDashboardData();
    } else if (tab === 'history') {
        loadHistory();
    }
}

// Event Listeners
function initEventListeners() {
    // Username scan
    document.getElementById('start-username-scan').addEventListener('click', () => {
        const username = document.getElementById('username-input').value.trim();
        if (!username) {
            showToast('Veuillez entrer un pseudo', 'error');
            return;
        }
        
        const deepScan = document.getElementById('deep-scan-check').checked;
        const timeout = parseInt(document.getElementById('timeout-input').value) || 10;
        
        startScan('username', username, { deepScan, timeout });
    });
    
    // Email scan
    document.getElementById('start-email-scan').addEventListener('click', () => {
        const email = document.getElementById('email-input').value.trim();
        if (!email || !email.includes('@')) {
            showToast('Veuillez entrer un email valide', 'error');
            return;
        }
        
        startScan('email', email);
    });
    
    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', () => {
        if (currentTab === 'dashboard') {
            loadDashboardData();
        } else if (currentTab === 'history') {
            loadHistory();
        }
        showToast('Rafraîchi avec succès', 'success');
    });
    
    // History filter
    document.getElementById('history-type-filter').addEventListener('change', (e) => {
        loadHistory(e.target.value);
    });
}

// Scan Functions
async function startScan(type, query, options = {}) {
    const progress = document.getElementById(`${type === 'username' ? 'username' : ''}-progress`);
    if (progress) progress.style.display = 'block';
    
    try {
        const data = createScanRequest(type, query, options);
        const response = await API.createScan(data);
        
        showToast(`Scan lancé: ${response.scan_id}`, 'success');
        
        // Poll for results
        pollScanResults(response.scan_id);
        
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
    } finally {
        if (progress) progress.style.display = 'none';
    }
}

async function pollScanResults(scanId) {
    const maxAttempts = 30;
    let attempts = 0;
    
    const poll = async () => {
        try {
            const result = await API.getScan(scanId);
            displayScanResults(result);
            
            if (result.status === 'completed' || result.status === 'failed') {
                loadDashboardData();
                return;
            }
            
            if (attempts < maxAttempts) {
                attempts++;
                setTimeout(poll, 2000);
            }
        } catch (error) {
            showToast(`Erreur lors du polling: ${error.message}`, 'error');
        }
    };
    
    poll();
}

function displayScanResults(result) {
    const container = document.getElementById(`${result.scan_type === 'username' ? 'username' : result.scan_type === 'email' ? 'email' : 'deep-scan'}-results`);
    if (!container) return;
    
    let html = `<h3>Résultats pour: ${result.query}</h3>`;
    html += `<div class="summary">`;
    html += `<span class="stat">Total: ${result.summary?.total || 0}</span>`;
    html += `<span class="stat found">Trouvés: ${result.summary?.found || 0}</span>`;
    html += `<span class="stat not-found">Non trouvés: ${result.summary?.not_found || 0}</span>`;
    html += `<span class="stat errors">Erreurs: ${result.summary?.errors || 0}</span>`;
    html += `</div>`;
    
    if (result.results && result.results.length > 0) {
        html += '<div class="results-list">';
        result.results.forEach(r => {
            const statusClass = r.status === 'found' ? 'found' : 
                               r.status === 'not_found' ? 'not-found' : 'error';
            html += `<div class="result-item ${statusClass}">`;
            html += `<div class="platform">${r.platform}</div>`;
            if (r.url) {
                html += `<div class="url"><a href="${r.url}" target="_blank">${r.url}</a></div>`;
            }
            if (r.response_time) {
                html += `<div class="time">⏱️ ${r.response_time}s</div>`;
            }
            if (r.error_message) {
                html += `<div class="error">${r.error_message}</div>`;
            }
            html += '</div>';
        });
        html += '</div>';
    }
    
    container.innerHTML = html;
}

// Dashboard
async function loadDashboardData() {
    try {
        const history = await API.getScanHistory(100);
        
        // Update stats
        document.getElementById('total-scans').textContent = history.length;
        
        const foundCount = history.reduce((sum, s) => sum + (s.found_count || 0), 0);
        const errorCount = history.reduce((sum, s) => sum + (s.error_count || 0), 0);
        
        document.getElementById('found-count').textContent = foundCount;
        document.getElementById('error-count').textContent = errorCount;
        
        // Update charts
        updateCharts(history);
        
        // Update recent scans
        updateRecentScans(history.slice(0, 10));
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateCharts(history) {
    // Type distribution
    const types = {};
    history.forEach(s => {
        types[s.scan_type] = (types[s.scan_type] || 0) + 1;
    });
    
    const typeCtx = document.getElementById('typeChart');
    if (typeCtx) {
        if (charts.type) charts.type.destroy();
        
        charts.type = new Chart(typeCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(types).map(t => t.charAt(0).toUpperCase() + t.slice(1)),
                datasets: [{
                    data: Object.values(types),
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4CAF50']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#fff' } }
                }
            }
        });
    }
    
    // Results over time
    const dailyResults = {};
    history.forEach(s => {
        const date = new Date(s.created_at).toLocaleDateString();
        dailyResults[date] = (dailyResults[date] || 0) + 1;
    });
    
    const resultsCtx = document.getElementById('resultsChart');
    if (resultsCtx) {
        if (charts.results) charts.results.destroy();
        
        const dates = Object.keys(dailyResults).slice(-7);
        const counts = Object.values(dailyResults).slice(-7);
        
        charts.results = new Chart(resultsCtx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Scans',
                    data: counts,
                    backgroundColor: 'rgba(102, 126, 234, 0.8)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#fff' }, grid: { color: '#2a2a4a' } },
                    x: { ticks: { color: '#fff' }, grid: { display: false } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

function updateRecentScans(scans) {
    const container = document.getElementById('recent-scans-list');
    if (!container) return;
    
    let html = '';
    scans.forEach(scan => {
        const date = new Date(scan.created_at).toLocaleString();
        html += `<div class="history-item">`;
        html += `<div class="info">`;
        html += `<h4>${scan.scan_type}: ${scan.query}</h4>`;
        html += `<p>${date}</p>`;
        html += `</div>`;
        html += `<span class="status ${scan.status}">${scan.status}</span>`;
        html += `</div>`;
    });
    
    container.innerHTML = html || '<p>Aucun scan récent</p>';
}

// History
async function loadHistory(scanType = '') {
    try {
        const history = await API.getScanHistory(100, scanType);
        const container = document.getElementById('history-list');
        
        let html = '';
        history.forEach(scan => {
            const date = new Date(scan.created_at).toLocaleString();
            html += `<div class="history-item">`;
            html += `<div class="info">`;
            html += `<h4>${scan.scan_type.toUpperCase()}: ${scan.query}</h4>`;
            html += `<p>${date} - ${scan.found_count} trouvés, ${scan.error_count} erreurs</p>`;
            html += `</div>`;
            html += `<div class="actions">`;
            html += `<span class="status ${scan.status}">${scan.status}</span>`;
            html += `<button class="btn btn-secondary" onclick="viewScan(${scan.id})">Voir</button>`;
            html += `<button class="btn btn-secondary" onclick="deleteScan(${scan.id})">Supprimer</button>`;
            html += `</div>`;
            html += `</div>`;
        });
        
        container.innerHTML = html || '<p>Aucun historique</p>';
        
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
    }
}

// View scan details
async function viewScan(scanId) {
    try {
        const result = await API.getScan(scanId);
        displayScanResults(result);
        switchTab(result.scan_type === 'username' ? 'username' : 
                              result.scan_type === 'email' ? 'email' : 'deep-scan');
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
    }
}

// Delete scan
async function deleteScan(scanId) {
    if (!confirm('Supprimer ce scan ?')) return;
    
    try {
        await API.deleteScan(scanId);
        showToast('Scan supprimé', 'success');
        loadHistory();
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Initialize dashboard
function initDashboard() {
    // Placeholder for charts
}