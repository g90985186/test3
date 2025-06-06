// UI-Driven API Functions
// These functions are called when users interact with specific UI elements

console.log('Loading UI-driven API functions...');

// Global API instance
const api = new CVEPlatformAPI();

// ========================================
// DASHBOARD INTERACTIONS
// ========================================

// Called when user clicks "Refresh Dashboard" button
async function refreshDashboard() {
    console.log('📊 User clicked refresh dashboard');
    showToast('Refreshing dashboard...', 'info');
    try {
        const [metrics, stats] = await Promise.all([
            api.getDashboardMetrics(),
            api.getDashboardStats()
        ]);
        updateDashboardMetrics(metrics);
        showToast('Dashboard refreshed', 'success');
    } catch (error) {
        console.error('Dashboard refresh failed:', error);
        showToast('Failed to refresh dashboard', 'error');
    }
}

// Called when user clicks on dashboard cards for detailed view
async function viewDetailedMetrics() {
    console.log('📈 User requested detailed metrics');
    try {
        const [metrics, timeline] = await Promise.all([
            api.getDashboardMetrics(),
            api.getDashboardTimeline()
        ]);
        displayDetailedMetrics(metrics, timeline);
        showToast('Detailed metrics loaded', 'success');
    } catch (error) {
        console.error('Failed to load detailed metrics:', error);
        showToast('Failed to load detailed metrics', 'error');
    }
}

// ========================================
// CVE SEARCH INTERACTIONS
// ========================================

// Called when user performs a search (clicks search button or presses Enter)
async function performCVESearch() {
    console.log('🔍 User performing CVE search');
    const searchParams = getCurrentSearchParams();
    
    if (!searchParams.query.trim()) {
        showToast('Please enter a search term', 'warning');
        return;
    }

    try {
        showToast('Searching CVEs...', 'info');
        const results = await api.searchCVEsAdvanced(searchParams);
        displaySearchResults(results);
        showToast(`Found ${results.length || 0} CVEs`, 'success');
    } catch (error) {
        console.error('CVE search failed:', error);
        showToast('Search failed', 'error');
    }
}

// Called when user clicks quick filter buttons
async function performQuickFilter(filterType) {
    console.log(`🏷️ User applied quick filter: ${filterType}`);
    
    let searchParams = {};
    switch(filterType) {
        case 'critical':
            searchParams = { severity: ['CRITICAL'], limit: 25 };
            break;
        case 'recent':
            const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
            searchParams = { date_from: weekAgo.toISOString().split('T')[0], limit: 25 };
            break;
        case 'high-cvss':
            searchParams = { cvss_min: 8.0, limit: 25 };
            break;
        case 'exploitable':
            searchParams = { has_exploit: true, limit: 25 };
            break;
    }

    try {
        showToast(`Loading ${filterType} CVEs...`, 'info');
        const results = await api.searchCVEsAdvanced(searchParams);
        displaySearchResults(results);
        showToast(`Found ${results.length || 0} ${filterType} CVEs`, 'success');
    } catch (error) {
        console.error('Quick filter failed:', error);
        showToast(`Failed to load ${filterType} CVEs`, 'error');
    }
}

// Called when user clicks "Save Search" button
async function saveCurrentSearch() {
    console.log('💾 User saving current search');
    const searchData = getCurrentSearchParams();
    const name = prompt('Enter a name for this search:');
    if (!name) return;

    try {
        showToast('Saving search...', 'info');
        await api.saveSearch({ name, ...searchData });
        showToast('Search saved successfully', 'success');
    } catch (error) {
        console.error('Failed to save search:', error);
        showToast('Failed to save search', 'error');
    }
}

// Called when user clicks "Load Saved" button
async function loadSavedSearches() {
    console.log('📁 User loading saved searches');
    try {
        showToast('Loading saved searches...', 'info');
        const searches = await api.getSavedSearches();
        displaySavedSearches(searches);
        showToast(`Loaded ${searches.length} saved searches`, 'success');
    } catch (error) {
        console.error('Failed to load saved searches:', error);
        showToast('Failed to load saved searches', 'error');
    }
}

// Called when user clicks "Import from NVD" button
async function importFromNVD() {
    console.log('⬇️ User importing from NVD');
    const keyword = prompt('Enter keyword to search NVD (or leave empty for recent CVEs):');
    
    try {
        showToast('Importing from NVD...', 'info');
        const importParams = keyword ? { keyword } : { days: 7 };
        const result = await api.importFromNVD(importParams);
        showToast(`Imported ${result.imported_count || 0} CVEs`, 'success');
    } catch (error) {
        console.error('NVD import failed:', error);
        showToast('NVD import failed', 'error');
    }
}

// ========================================
// ANALYSIS INTERACTIONS
// ========================================

// Called when user clicks "Start AI Analysis" button
async function performAnalysis() {
    console.log('🧠 User starting AI analysis');
    const cveId = document.getElementById('analysis-cve-input')?.value.trim();
    const analysisType = document.getElementById('analysis-type')?.value || 'comprehensive';
    
    if (!cveId) {
        showToast('Please enter a CVE ID', 'warning');
        return;
    }

    try {
        showToast(`Starting ${analysisType} analysis...`, 'info');
        const result = await api.analyzeCVE({ cve_id: cveId, analysis_type: analysisType });
        displayAnalysisResults(result);
        showToast('Analysis completed', 'success');
    } catch (error) {
        console.error('Analysis failed:', error);
        showToast('Analysis failed', 'error');
    }
}

// Called when user clicks "Load Analysis History" button
async function loadAnalysisHistory() {
    console.log('📊 User loading analysis history');
    try {
        showToast('Loading analysis history...', 'info');
        const results = await api.getAnalysisResults();
        displayAnalysisHistory(results);
        showToast(`Loaded ${results.length} analysis results`, 'success');
    } catch (error) {
        console.error('Failed to load analysis history:', error);
        showToast('Failed to load analysis history', 'error');
    }
}

// Called when user clicks "Check AI Status" button
async function checkAIStatus() {
    console.log('🤖 User checking AI status');
    try {
        const status = await api.getAIStatus();
        displayAIStatus(status);
        showToast('AI status updated', 'success');
    } catch (error) {
        console.error('Failed to check AI status:', error);
        showToast('Failed to check AI status', 'error');
    }
}

// ========================================
// WATCHLIST INTERACTIONS
// ========================================

// Called when user clicks "Create Watchlist" button
async function createWatchlist() {
    console.log('➕ User creating watchlist');
    const name = prompt('Enter watchlist name:');
    const description = prompt('Enter description (optional):');
    
    if (!name) return;

    try {
        showToast('Creating watchlist...', 'info');
        await api.createWatchlist({ name, description });
        loadWatchlistData();
        showToast('Watchlist created', 'success');
    } catch (error) {
        console.error('Failed to create watchlist:', error);
        showToast('Failed to create watchlist', 'error');
    }
}

// Called when user navigates to watchlist section
async function loadWatchlistData() {
    console.log('📝 Loading watchlist data');
    try {
        const [watchlists, stats] = await Promise.all([
            api.getWatchlists(),
            api.getWatchlistStats()
        ]);
        displayWatchlists(watchlists, stats);
        showToast(`Loaded ${watchlists.length} watchlists`, 'success');
    } catch (error) {
        console.error('Failed to load watchlists:', error);
        showToast('Failed to load watchlists', 'error');
    }
}

// Called when user clicks "Add to Watchlist" for a CVE
async function addToWatchlist(cveId) {
    console.log(`➕ User adding CVE ${cveId} to watchlist`);
    try {
        const watchlists = await api.getWatchlists();
        const watchlistId = await selectWatchlistModal(watchlists);
        if (watchlistId) {
            await api.addCVEsToWatchlist(watchlistId, { cve_ids: [cveId] });
            showToast('CVE added to watchlist', 'success');
        }
    } catch (error) {
        console.error('Failed to add to watchlist:', error);
        showToast('Failed to add to watchlist', 'error');
    }
}

// ========================================
// CHAT INTERACTIONS
// ========================================

// Called when user sends a chat message
async function sendChatMessage() {
    console.log('💬 User sending chat message');
    const chatInput = document.getElementById('chat-input');
    const message = chatInput?.value.trim();
    
    if (!message) return;

    try {
        const messageData = { message, session_id: getCurrentChatSession() };
        const response = await api.sendChatMessage(messageData);
        
        addChatMessage(message, true);
        addChatMessage(response.response, false);
        chatInput.value = '';
        showToast('Message sent', 'success');
    } catch (error) {
        console.error('Failed to send message:', error);
        showToast('Failed to send message', 'error');
    }
}

// Called when user clicks "Load Chat History" button
async function loadChatHistory() {
    console.log('📜 User loading chat history');
    try {
        const [sessions, stats] = await Promise.all([
            api.getChatSessions(),
            api.getChatStats()
        ]);
        displayChatHistory(sessions, stats);
        showToast(`Loaded ${sessions.length} chat sessions`, 'success');
    } catch (error) {
        console.error('Failed to load chat history:', error);
        showToast('Failed to load chat history', 'error');
    }
}

// ========================================
// POC INTERACTIONS
// ========================================

// Called when user clicks "Generate PoC" button
async function generatePoC() {
    console.log('⚡ User generating PoC');
    const cveId = document.getElementById('analysis-cve-input')?.value.trim() || 
                  document.getElementById('poc-cve-input')?.value.trim();
    const model = document.getElementById('poc-model-select')?.value || 'codellama';
    
    if (!cveId) {
        showToast('Please enter a CVE ID', 'warning');
        return;
    }

    try {
        showToast('Generating PoC...', 'info');
        const result = await api.generatePoC({ cve_id: cveId, model });
        displayPoCResults(result);
        showToast('PoC generated successfully', 'success');
    } catch (error) {
        console.error('PoC generation failed:', error);
        showToast('PoC generation failed', 'error');
    }
}

// Called when user clicks "Load PoC History" button
async function loadPoCHistory() {
    console.log('📜 User loading PoC history');
    try {
        const pocs = await api.getAllPoCs();
        displayPoCHistory(pocs);
        showToast(`Loaded ${pocs.length} PoCs`, 'success');
    } catch (error) {
        console.error('Failed to load PoC history:', error);
        showToast('Failed to load PoC history', 'error');
    }
}

// Called when user clicks "Validate PoC" button
async function validatePoC() {
    console.log('✅ User validating PoC');
    const cveId = getCurrentPoCCVE();
    
    try {
        showToast('Validating PoC...', 'info');
        const result = await api.validatePoC(cveId, { validation_type: 'syntax' });
        displayPoCValidation(result);
        showToast('PoC validation completed', 'success');
    } catch (error) {
        console.error('PoC validation failed:', error);
        showToast('PoC validation failed', 'error');
    }
}

// ========================================
// REPORTS INTERACTIONS
// ========================================

// Called when user clicks "Generate Report" button
async function generateReport() {
    console.log('📊 User generating report');
    const reportType = prompt('Enter report type (summary, detailed, executive):');
    if (!reportType) return;

    try {
        showToast('Generating report...', 'info');
        const result = await api.generateReport({ 
            type: reportType, 
            format: 'pdf',
            title: `${reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report`
        });
        loadReportsData();
        showToast('Report generated successfully', 'success');
    } catch (error) {
        console.error('Report generation failed:', error);
        showToast('Report generation failed', 'error');
    }
}

// Called when user navigates to reports section
async function loadReportsData() {
    console.log('📄 Loading reports data');
    try {
        const [reports, metrics] = await Promise.all([
            api.getReports(),
            api.getReportMetrics()
        ]);
        displayReports(reports, metrics);
        showToast(`Loaded ${reports.length} reports`, 'success');
    } catch (error) {
        console.error('Failed to load reports:', error);
        showToast('Failed to load reports', 'error');
    }
}

// ========================================
// NOTIFICATIONS INTERACTIONS
// ========================================

// Called when user opens notifications panel
async function loadNotifications() {
    console.log('🔔 User loading notifications');
    try {
        const [notifications, stats] = await Promise.all([
            api.getNotifications(),
            api.getNotificationStats()
        ]);
        displayNotifications(notifications, stats);
        updateNotificationBadge(notifications.filter(n => !n.read).length);
        showToast(`Loaded ${notifications.length} notifications`, 'success');
    } catch (error) {
        console.error('Failed to load notifications:', error);
        showToast('Failed to load notifications', 'error');
    }
}

// Called when user clicks "Mark All Read" button
async function markAllNotificationsRead() {
    console.log('✅ User marking all notifications as read');
    try {
        await api.markAllNotificationsRead();
        loadNotifications();
        showToast('All notifications marked as read', 'success');
    } catch (error) {
        console.error('Failed to mark notifications as read:', error);
        showToast('Failed to mark notifications as read', 'error');
    }
}

// Called when user clicks "Test Notifications" button
async function testNotifications() {
    console.log('🧪 User testing notifications');
    try {
        await api.testNotification();
        showToast('Test notification sent', 'success');
    } catch (error) {
        console.error('Test notification failed:', error);
        showToast('Test notification failed', 'error');
    }
}

// ========================================
// SETTINGS INTERACTIONS
// ========================================

// Called when user opens settings panel
async function loadSettings() {
    console.log('⚙️ User loading settings');
    try {
        const [userSettings, notificationSettings, systemSettings] = await Promise.all([
            api.getUserSettings(),
            api.getNotificationSettings(),
            api.getSystemSettings()
        ]);
        displaySettings(userSettings, notificationSettings, systemSettings);
        showToast('Settings loaded', 'success');
    } catch (error) {
        console.error('Failed to load settings:', error);
        showToast('Failed to load settings', 'error');
    }
}

// Called when user clicks "Save Settings" button
async function saveSettings() {
    console.log('💾 User saving settings');
    const settingsData = getCurrentSettingsData();
    
    try {
        showToast('Saving settings...', 'info');
        await Promise.all([
            api.updateUserSettings(settingsData.user),
            api.updateNotificationSettings(settingsData.notifications)
        ]);
        showToast('Settings saved successfully', 'success');
    } catch (error) {
        console.error('Failed to save settings:', error);
        showToast('Failed to save settings', 'error');
    }
}

// ========================================
// MONITORING INTERACTIONS
// ========================================

// Called when user opens monitoring panel
async function loadMonitoringData() {
    console.log('📊 User loading monitoring data');
    try {
        const [health, metrics, status] = await Promise.all([
            api.getHealthCheck(),
            api.getSystemMetrics(),
            api.getSystemStatus()
        ]);
        displayMonitoringData(health, metrics, status);
        showToast('Monitoring data loaded', 'success');
    } catch (error) {
        console.error('Failed to load monitoring data:', error);
        showToast('Failed to load monitoring data', 'error');
    }
}

// ========================================
// HELPER FUNCTIONS
// ========================================

function getCurrentSearchParams() {
    return {
        query: document.getElementById('cve-search-input')?.value || '',
        search_type: document.getElementById('search-type-filter')?.value || 'both',
        date_from: document.getElementById('date-from')?.value || '',
        date_to: document.getElementById('date-to')?.value || '',
        cvss_min: parseFloat(document.getElementById('cvss-min')?.value || '0'),
        cvss_max: parseFloat(document.getElementById('cvss-max')?.value || '10'),
        severity: Array.from(document.querySelectorAll('.severity-input:checked')).map(el => el.value),
        vendor: document.getElementById('vendor-filter')?.value || '',
        product: document.getElementById('product-filter')?.value || '',
        limit: parseInt(document.getElementById('results-per-page')?.value || '25')
    };
}

function getCurrentChatSession() {
    return document.getElementById('current-session-id')?.value || null;
}

function getCurrentPoCCVE() {
    return document.getElementById('current-poc-cve')?.value || 
           document.getElementById('analysis-cve-input')?.value || '';
}

function getCurrentSettingsData() {
    return {
        user: {
            theme: document.getElementById('theme-setting')?.value || 'light',
            language: document.getElementById('language-setting')?.value || 'en'
        },
        notifications: {
            email_enabled: document.getElementById('email-notifications')?.checked || false,
            push_enabled: document.getElementById('push-notifications')?.checked || false
        }
    };
}

async function selectWatchlistModal(watchlists) {
    // Simple selection for now - could be enhanced with proper modal
    const options = watchlists.map((w, i) => `${i + 1}. ${w.name}`).join('\n');
    const selection = prompt(`Select watchlist:\n${options}\n\nEnter number:`);
    const index = parseInt(selection) - 1;
    return watchlists[index]?.id;
}

// UI Display Functions (these would update the actual DOM elements)
function displayDetailedMetrics(metrics, timeline) {
    console.log('Displaying detailed metrics:', metrics, timeline);
    // Implementation would update the detailed metrics section
}

function displaySavedSearches(searches) {
    console.log('Displaying saved searches:', searches);
    // Implementation would show saved searches in UI
}

function displayAnalysisResults(results) {
    console.log('Displaying analysis results:', results);
    // Implementation would update analysis results section
}

function displayAnalysisHistory(history) {
    console.log('Displaying analysis history:', history);
    // Implementation would show analysis history
}

function displayAIStatus(status) {
    console.log('Displaying AI status:', status);
    // Implementation would update AI status indicator
}

function displayWatchlists(watchlists, stats) {
    console.log('Displaying watchlists:', watchlists, stats);
    // Implementation would update watchlist section
}

function displayChatHistory(sessions, stats) {
    console.log('Displaying chat history:', sessions, stats);
    // Implementation would show chat history
}

function displayPoCResults(results) {
    console.log('Displaying PoC results:', results);
    // Implementation would show generated PoC
}

function displayPoCHistory(pocs) {
    console.log('Displaying PoC history:', pocs);
    // Implementation would show PoC history
}

function displayPoCValidation(validation) {
    console.log('Displaying PoC validation:', validation);
    // Implementation would show validation results
}

function displayReports(reports, metrics) {
    console.log('Displaying reports:', reports, metrics);
    // Implementation would show reports list
}

function displayNotifications(notifications, stats) {
    console.log('Displaying notifications:', notifications, stats);
    // Implementation would update notifications panel
}

function displaySettings(userSettings, notificationSettings, systemSettings) {
    console.log('Displaying settings:', userSettings, notificationSettings, systemSettings);
    // Implementation would populate settings form
}

function displayMonitoringData(health, metrics, status) {
    console.log('Displaying monitoring data:', health, metrics, status);
    // Implementation would update monitoring dashboard
}

function addChatMessage(message, isUser) {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-2 ${isUser ? 'text-right' : 'text-left'}`;
        messageDiv.innerHTML = `
            <div class="inline-block p-2 rounded-lg ${isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}">
                ${message}
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

console.log('UI-driven API functions loaded!'); 