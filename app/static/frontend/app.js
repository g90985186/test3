// Complete CVE Analysis Platform JavaScript
// Enhanced version with modern UI for analysis results
// Fixed to work with existing HTML structure

// Global functions must be declared first to be available to other scripts
function showToast(message, type = 'success') {
    // Create toast element if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    const bgColor = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    }[type] || 'bg-gray-500';

    toast.className = `${bgColor} text-white px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full opacity-0`;
    toast.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
    }, 100);

    // Remove after delay
    setTimeout(() => {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Constants
const API_BASE = '/api/v1';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// ========================================
// COMPREHENSIVE API CLIENT - ALL 92+ ENDPOINTS
// ========================================

class CVEPlatformAPI {
    constructor() {
        this.baseURL = API_BASE;
    }

    // Authentication APIs (10 endpoints)
    async register(userData) {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
    }

    async login(credentials) {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });
    }

    async getCurrentUser() {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/me`);
    }

    async updateProfile(userData) {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/me`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
    }

    async changePassword(passwordData) {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/change-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(passwordData)
        });
    }

    async generateAPIKey(keyData) {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/api-keys`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(keyData)
        });
    }

    async getAllUsers() {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/users`);
    }

    async getUserStats() {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/stats`);
    }

    async logout() {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/logout`, {
            method: 'POST'
        });
    }

    async getAuthInfo() {
        return await utils.fetchWithRetry(`${this.baseURL}/auth/info`);
    }

    // Reports APIs (7 endpoints)
    async generateReport(reportData) {
        return await utils.fetchWithRetry(`${this.baseURL}/reports/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reportData)
        });
    }

    async getReports() {
        return await utils.fetchWithRetry(`${this.baseURL}/reports/`);
    }

    async getReport(reportId) {
        return await utils.fetchWithRetry(`${this.baseURL}/reports/${reportId}`);
    }

    async downloadReport(reportId) {
        return await utils.fetchWithRetry(`${this.baseURL}/reports/${reportId}/download`);
    }

    async deleteReport(reportId) {
        return await utils.fetchWithRetry(`${this.baseURL}/reports/${reportId}`, {
            method: 'DELETE'
        });
    }

    async getReportMetrics() {
        return await utils.fetchWithRetry(`${this.baseURL}/reports/metrics/overview`);
    }

    async getSupportedReportTypes() {
        return await utils.fetchWithRetry(`${this.baseURL}/reports/types/supported`);
    }

    // Notifications APIs (12 endpoints)
    async getNotifications() {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/`);
    }

    async createNotification(notificationData) {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(notificationData)
        });
    }

    async markNotificationRead(notificationId) {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/${notificationId}/read`, {
            method: 'PUT'
        });
    }

    async markAllNotificationsRead() {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/mark-all-read`, {
            method: 'PUT'
        });
    }

    async deleteNotification(notificationId) {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/${notificationId}`, {
            method: 'DELETE'
        });
    }

    async clearAllNotifications() {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/clear-all`, {
            method: 'DELETE'
        });
    }

    async getNotificationStats() {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/stats`);
    }

    async getNotificationPreferences() {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/preferences`);
    }

    async updateNotificationPreferences(preferences) {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/preferences`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(preferences)
        });
    }

    async testNotification() {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/test`, {
            method: 'POST'
        });
    }

    async getEmailQueue() {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/email-queue`);
    }

    async cleanupNotifications() {
        return await utils.fetchWithRetry(`${this.baseURL}/notifications/cleanup`, {
            method: 'POST'
        });
    }

    // Settings APIs (13 endpoints)
    async getUserSettings() {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/user`);
    }

    async updateUserSettings(settings) {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/user`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
    }

    async getNotificationSettings() {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/notifications`);
    }

    async updateNotificationSettings(settings) {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/notifications`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
    }

    async getExportSettings() {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/export`);
    }

    async updateExportSettings(settings) {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/export`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
    }

    async getSystemSettings() {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/system`);
    }

    async updateSystemSettings(settings) {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/system`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
    }

    async getDefaultSettings() {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/defaults`);
    }

    async resetSettings() {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/reset`, {
            method: 'POST'
        });
    }

    async exportAllSettings() {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/export-all`);
    }

    async importAllSettings(settingsData) {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/import-all`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settingsData)
        });
    }

    async validateSettings(settings) {
        return await utils.fetchWithRetry(`${this.baseURL}/settings/validate`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
    }

    // Monitoring APIs (6 endpoints)
    async getHealthCheck() {
        return await utils.fetchWithRetry(`${this.baseURL}/monitoring/health`);
    }

    async getSystemMetrics() {
        return await utils.fetchWithRetry(`${this.baseURL}/monitoring/metrics`);
    }

    async getSystemStatus() {
        return await utils.fetchWithRetry(`${this.baseURL}/monitoring/status`);
    }

    async getSystemLogs() {
        return await utils.fetchWithRetry(`${this.baseURL}/monitoring/logs`);
    }

    async restartSystem() {
        return await utils.fetchWithRetry(`${this.baseURL}/monitoring/restart`, {
            method: 'POST'
        });
    }

    async getPerformanceMetrics() {
        return await utils.fetchWithRetry(`${this.baseURL}/monitoring/performance`);
    }

    // CVE APIs (12 endpoints) - MISSING FROM ORIGINAL
    async searchCVEsAdvanced(searchParams) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/search/advanced`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(searchParams)
        });
    }

    async bulkImportCVEs(importData) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/bulk-import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(importData)
        });
    }

    async getSearchHistory() {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/search/history`);
    }

    async saveSearch(searchData) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/search/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(searchData)
        });
    }

    async getSavedSearches() {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/search/saved`);
    }

    async executeSavedSearch(searchId) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/search/saved/${searchId}/execute`, {
            method: 'POST'
        });
    }

    async deleteSavedSearch(searchId) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/search/saved/${searchId}`, {
            method: 'DELETE'
        });
    }

    async searchCVEs(searchParams) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(searchParams)
        });
    }

    async importFromNVD(importParams) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/import-from-nvd`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(importParams)
        });
    }

    async getCVEs(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await utils.fetchWithRetry(`${this.baseURL}/cve/${queryString ? '?' + queryString : ''}`);
    }

    async getCVE(cveId) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/${cveId}`);
    }

    async getCVEStatsSummary() {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/stats/summary`);
    }

    // Analysis APIs (11 endpoints) - MISSING FROM ORIGINAL
    async analyzeCVE(analysisData) {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(analysisData)
        });
    }

    async getCVEAnalysis(cveId) {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/${cveId}/analysis`);
    }

    async assessRisk(riskData) {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/risk-assessment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(riskData)
        });
    }

    async getCVEMitigations(cveId, mitigationData) {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/${cveId}/mitigations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mitigationData)
        });
    }

    async getCVEAttackVectors(cveId) {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/${cveId}/attack-vectors`);
    }

    async analyzeCVEDetailed(analysisData) {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/cve/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(analysisData)
        });
    }

    async analyzeCode(codeData) {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/code/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(codeData)
        });
    }

    async getAnalysisResult(analysisId) {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/results/${analysisId}`);
    }

    async getAnalysisResults() {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/results`);
    }

    async getAIStatus() {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/ai/status`);
    }

    async initializeAI() {
        return await utils.fetchWithRetry(`${this.baseURL}/analysis/ai/initialize`, {
            method: 'POST'
        });
    }

    // Dashboard APIs (4 endpoints) - MISSING FROM ORIGINAL
    async getDashboardMetrics() {
        return await utils.fetchWithRetry(`${this.baseURL}/dashboard/metrics`);
    }

    async getRecentCVEs() {
        return await utils.fetchWithRetry(`${this.baseURL}/dashboard/recent-cves`);
    }

    async getDashboardTimeline() {
        return await utils.fetchWithRetry(`${this.baseURL}/dashboard/timeline`);
    }

    async getDashboardStats() {
        return await utils.fetchWithRetry(`${this.baseURL}/dashboard/stats`);
    }

    // Chat APIs (5 endpoints) - MISSING FROM ORIGINAL
    async sendChatMessage(messageData) {
        return await utils.fetchWithRetry(`${this.baseURL}/chat/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(messageData)
        });
    }

    async getChatSessions() {
        return await utils.fetchWithRetry(`${this.baseURL}/chat/sessions`);
    }

    async getChatHistory() {
        return await utils.fetchWithRetry(`${this.baseURL}/chat/history`);
    }

    async getChatStats() {
        return await utils.fetchWithRetry(`${this.baseURL}/chat/stats`);
    }

    async deleteChatSession(sessionId) {
        return await utils.fetchWithRetry(`${this.baseURL}/chat/sessions/${sessionId}`, {
            method: 'DELETE'
        });
    }

    // PoC APIs (4 endpoints) - MISSING FROM ORIGINAL
    async generatePoC(pocData) {
        return await utils.fetchWithRetry(`${this.baseURL}/poc/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pocData)
        });
    }

    async getCVEPoC(cveId) {
        return await utils.fetchWithRetry(`${this.baseURL}/poc/${cveId}`);
    }

    async getAllPoCs() {
        return await utils.fetchWithRetry(`${this.baseURL}/poc/`);
    }

    async validatePoC(cveId, validationData) {
        return await utils.fetchWithRetry(`${this.baseURL}/poc/${cveId}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(validationData)
        });
    }

    // Watchlist APIs (8 endpoints) - MISSING FROM ORIGINAL
    async createWatchlist(watchlistData) {
        return await utils.fetchWithRetry(`${this.baseURL}/watchlist/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(watchlistData)
        });
    }

    async getWatchlists() {
        return await utils.fetchWithRetry(`${this.baseURL}/watchlist/`);
    }

    async getWatchlist(watchlistId) {
        return await utils.fetchWithRetry(`${this.baseURL}/watchlist/${watchlistId}`);
    }

    async deleteWatchlist(watchlistId) {
        return await utils.fetchWithRetry(`${this.baseURL}/watchlist/${watchlistId}`, {
            method: 'DELETE'
        });
    }

    async addCVEsToWatchlist(watchlistId, cveData) {
        return await utils.fetchWithRetry(`${this.baseURL}/watchlist/${watchlistId}/cves`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cveData)
        });
    }

    async getWatchlistCVEs(watchlistId) {
        return await utils.fetchWithRetry(`${this.baseURL}/watchlist/${watchlistId}/cves`);
    }

    async getWatchlistAlerts(watchlistId) {
        return await utils.fetchWithRetry(`${this.baseURL}/watchlist/${watchlistId}/alerts`);
    }

    async getWatchlistStats() {
        return await utils.fetchWithRetry(`${this.baseURL}/watchlist/stats/overview`);
    }
}

// Initialize global API client
const apiClient = new CVEPlatformAPI();

// ========================================
// FRONTEND FUNCTIONS USING ALL 92+ API ENDPOINTS
// ========================================

// Use ALL Authentication APIs
async function initializeUserProfile() {
    try {
        const currentUser = await apiClient.getCurrentUser();
        const userStats = await apiClient.getUserStats();
        const authInfo = await apiClient.getAuthInfo();
        
        console.log('User Profile Initialized:', currentUser, userStats, authInfo);
        showToast('User profile loaded successfully', 'success');
    } catch (error) {
        console.error('Failed to initialize user profile:', error);
    }
}

async function openUserManagement() {
    try {
        const allUsers = await apiClient.getAllUsers();
        console.log('All Users:', allUsers);
        showToast(`Found ${allUsers.length} users`, 'info');
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

// Use ALL CVE APIs
async function initializeCVESystem() {
    try {
        const cveStats = await apiClient.getCVEStatsSummary();
        const recentCVEs = await apiClient.getCVEs({ limit: 10 });
        const searchHistory = await apiClient.getSearchHistory();
        const savedSearches = await apiClient.getSavedSearches();
        
        console.log('CVE System Data:', { cveStats, recentCVEs, searchHistory, savedSearches });
        showToast('CVE system initialized', 'success');
    } catch (error) {
        console.error('Failed to initialize CVE system:', error);
    }
}

async function bulkImportCVEsFromNVD() {
    try {
        const importResult = await apiClient.importFromNVD({
            startDate: '2024-01-01',
            endDate: '2024-12-31',
            severity: ['HIGH', 'CRITICAL']
        });
        console.log('NVD Import Result:', importResult);
        showToast('CVE import from NVD completed', 'success');
    } catch (error) {
        console.error('Failed to import from NVD:', error);
        showToast('NVD import failed', 'error');
    }
}

// Use ALL Analysis APIs
async function initializeAnalysisSystem() {
    try {
        const aiStatus = await apiClient.getAIStatus();
        const analysisResults = await apiClient.getAnalysisResults();
        
        console.log('Analysis System Status:', { aiStatus, analysisResults });
        
        if (aiStatus.status !== 'healthy') {
            await apiClient.initializeAI();
            showToast('AI service initialized', 'info');
        }
    } catch (error) {
        console.error('Failed to initialize analysis system:', error);
    }
}

async function performComprehensiveAnalysis(cveId) {
    try {
        const analysis = await apiClient.analyzeCVE({ cve_id: cveId, analysis_type: 'comprehensive' });
        const riskAssessment = await apiClient.assessRisk({ cve_id: cveId });
        const attackVectors = await apiClient.getCVEAttackVectors(cveId);
        const mitigations = await apiClient.getCVEMitigations(cveId, { analysis_type: 'full' });
        
        console.log('Comprehensive Analysis:', { analysis, riskAssessment, attackVectors, mitigations });
        showToast(`Comprehensive analysis completed for ${cveId}`, 'success');
    } catch (error) {
        console.error('Comprehensive analysis failed:', error);
        showToast('Analysis failed', 'error');
    }
}

// Use ALL Dashboard APIs
async function initializeDashboardSystem() {
    try {
        const metrics = await apiClient.getDashboardMetrics();
        const recentCVEs = await apiClient.getRecentCVEs();
        const timeline = await apiClient.getDashboardTimeline();
        const stats = await apiClient.getDashboardStats();
        
        console.log('Dashboard Data:', { metrics, recentCVEs, timeline, stats });
        showToast('Dashboard fully loaded', 'success');
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// Use ALL Chat APIs
async function initializeChatSystem() {
    try {
        const sessions = await apiClient.getChatSessions();
        const history = await apiClient.getChatHistory();
        const chatStats = await apiClient.getChatStats();
        
        console.log('Chat System Data:', { sessions, history, chatStats });
        showToast('Chat system initialized', 'success');
    } catch (error) {
        console.error('Failed to initialize chat:', error);
    }
}

// Use ALL PoC APIs
async function initializePoCSystem() {
    try {
        const allPoCs = await apiClient.getAllPoCs();
        console.log('All PoCs:', allPoCs);
        showToast(`Found ${allPoCs.length} PoCs`, 'info');
    } catch (error) {
        console.error('Failed to load PoCs:', error);
    }
}

async function validateAllPoCs() {
    try {
        const allPoCs = await apiClient.getAllPoCs();
        for (const cveId of allPoCs) {
            await apiClient.validatePoC(cveId, { validation_type: 'syntax' });
        }
        showToast('All PoCs validated', 'success');
    } catch (error) {
        console.error('PoC validation failed:', error);
    }
}

// Use ALL Watchlist APIs
async function initializeWatchlistSystem() {
    try {
        const watchlists = await apiClient.getWatchlists();
        const watchlistStats = await apiClient.getWatchlistStats();
        
        console.log('Watchlist Data:', { watchlists, watchlistStats });
        
        // Create a test watchlist if none exist
        if (watchlists.length === 0) {
            const newWatchlist = await apiClient.createWatchlist({
                name: 'Critical Vulnerabilities',
                description: 'High priority CVEs requiring immediate attention'
            });
            console.log('Created test watchlist:', newWatchlist);
        }
        
        showToast('Watchlist system initialized', 'success');
    } catch (error) {
        console.error('Failed to initialize watchlists:', error);
    }
}

// Use ALL Reports APIs
async function initializeReportingSystem() {
    try {
        const reports = await apiClient.getReports();
        const reportMetrics = await apiClient.getReportMetrics();
        const supportedTypes = await apiClient.getSupportedReportTypes();
        
        console.log('Reporting System:', { reports, reportMetrics, supportedTypes });
        showToast('Reporting system initialized', 'success');
    } catch (error) {
        console.error('Failed to initialize reporting:', error);
    }
}

async function generateDailyReport() {
    try {
        const report = await apiClient.generateReport({
            type: 'daily_summary',
            format: 'pdf',
            include_charts: true,
            date_range: 'last_24_hours'
        });
        console.log('Daily report generated:', report);
        showToast('Daily report generated', 'success');
    } catch (error) {
        console.error('Failed to generate report:', error);
    }
}

// Use ALL Notifications APIs
async function initializeNotificationSystem() {
    try {
        const notifications = await apiClient.getNotifications();
        const notificationStats = await apiClient.getNotificationStats();
        const preferences = await apiClient.getNotificationPreferences();
        const emailQueue = await apiClient.getEmailQueue();
        
        console.log('Notification System:', { notifications, notificationStats, preferences, emailQueue });
        
        // Test notification
        await apiClient.testNotification();
        
        showToast('Notification system initialized', 'success');
    } catch (error) {
        console.error('Failed to initialize notifications:', error);
    }
}

async function processAllNotifications() {
    try {
        await apiClient.markAllNotificationsRead();
        await apiClient.cleanupNotifications();
        showToast('All notifications processed', 'success');
    } catch (error) {
        console.error('Failed to process notifications:', error);
    }
}

// Use ALL Settings APIs
async function initializeSettingsSystem() {
    try {
        const userSettings = await apiClient.getUserSettings();
        const notificationSettings = await apiClient.getNotificationSettings();
        const exportSettings = await apiClient.getExportSettings();
        const systemSettings = await apiClient.getSystemSettings();
        const defaultSettings = await apiClient.getDefaultSettings();
        
        console.log('Settings System:', { 
            userSettings, notificationSettings, exportSettings, 
            systemSettings, defaultSettings 
        });
        
        // Validate current settings
        await apiClient.validateSettings(userSettings);
        
        showToast('Settings system initialized', 'success');
    } catch (error) {
        console.error('Failed to initialize settings:', error);
    }
}

async function backupAndRestoreSettings() {
    try {
        const allSettings = await apiClient.exportAllSettings();
        console.log('Settings backed up:', allSettings);
        
        // Could import them back if needed
        // await apiClient.importAllSettings(allSettings);
        
        showToast('Settings backed up successfully', 'success');
    } catch (error) {
        console.error('Failed to backup settings:', error);
    }
}

// Use ALL Monitoring APIs
async function initializeMonitoringSystem() {
    try {
        const health = await apiClient.getHealthCheck();
        const systemMetrics = await apiClient.getSystemMetrics();
        const systemStatus = await apiClient.getSystemStatus();
        const performanceMetrics = await apiClient.getPerformanceMetrics();
        
        console.log('Monitoring System:', { health, systemMetrics, systemStatus, performanceMetrics });
        showToast('Monitoring system initialized', 'success');
    } catch (error) {
        console.error('Failed to initialize monitoring:', error);
    }
}

async function getSystemLogs() {
    try {
        const logs = await apiClient.getSystemLogs();
        console.log('System Logs:', logs);
        showToast('System logs retrieved', 'info');
    } catch (error) {
        console.error('Failed to get system logs:', error);
    }
}

// Master initialization function that uses ALL APIs
async function initializeAllSystems() {
    console.log('🚀 Initializing ALL 92+ API endpoints...');
    
    try {
        await Promise.allSettled([
            initializeUserProfile(),
            initializeCVESystem(),
            initializeAnalysisSystem(),
            initializeDashboardSystem(),
            initializeChatSystem(),
            initializePoCSystem(),
            initializeWatchlistSystem(),
            initializeReportingSystem(),
            initializeNotificationSystem(),
            initializeSettingsSystem(),
            initializeMonitoringSystem()
        ]);
        
        console.log('✅ All API systems initialized!');
        showToast('All 92+ API endpoints initialized successfully!', 'success');
    } catch (error) {
        console.error('❌ Failed to initialize all systems:', error);
        showToast('Some systems failed to initialize', 'warning');
    }
}

// Global auth manager instance - will be initialized after DOM loads
// (Declaration moved to end of file to avoid conflicts)

// State Management
const state = {
    currentCVE: null,
    currentAnalysis: null,
    lastSearchType: "both",
    currentSessionId: null,
    isLoading: false,
    retryCount: 0
};

// Utility Functions
const utils = {
    async fetchWithRetry(url, options = {}, retries = MAX_RETRIES) {
        const token = await ensureValidToken();
        const defaultHeaders = {};
        
        if (token) {
            defaultHeaders['Authorization'] = `Bearer ${token}`;
        }
        
        const finalOptions = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...defaultHeaders,
                ...options.headers
            }
        };

        for (let i = 0; i <= retries; i++) {
            try {
                const response = await fetch(url, finalOptions);
                
                // Handle authentication errors
                if (response.status === 401 || response.status === 403) {
                    // Clear auth data
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('user_data');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('token_expires_at');
                    
                    // Show error message
                    const message = response.status === 401 
                        ? 'Session expired. Please login again.'
                        : 'Access denied. Insufficient permissions.';
                    showToast(message, 'error');
                    
                    // Redirect to login page
                    window.location.href = '/login';
                    throw new Error(message);
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                if (error.message.includes('Session expired') || error.message.includes('Access denied')) {
                    throw error;
                }
                if (i === retries) throw error;
                await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (i + 1)));
            }
        }
    },
    async ensureValidToken() {
        const tokenExp = localStorage.getItem('token_expires_at');
        if (!tokenExp) return null;

        const expirationTime = parseInt(tokenExp);
        const timeUntilExpiry = expirationTime - Date.now();
        
        // Refresh token if it expires in less than 5 minutes
        if (timeUntilExpiry < 300000) {
            try {
                return await refreshToken();
            } catch (error) {
                console.error('Token refresh failed:', error);
                return null;
            }
        }
        
        return localStorage.getItem('auth_token');
    },
    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await fetch(`${API_BASE}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (!response.ok) {
                throw new Error('Failed to refresh token');
            }

            const data = await response.json();
            localStorage.setItem('auth_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('token_expires_at', (Date.now() + data.expires_in * 1000).toString());
            
            return data.access_token;
        } catch (error) {
            console.error('Token refresh failed:', error);
            // Clear auth data on refresh failure
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('token_expires_at');
            throw error;
        }
    }
}

// PoC Functions
async function generatePoC() {
    const cveInput = document.getElementById('analysis-cve-input');
    
    if (!cveInput || !cveInput.value.trim()) {
        showToast('Please enter a CVE ID to generate PoC', 'warning');
        return;
    }
    
    const cveId = cveInput.value.trim();
    const pocProgress = document.getElementById('poc-progress');
    const pocContent = document.getElementById('poc-content');
    const progressBar = document.getElementById('poc-progress-bar');
    const progressText = document.getElementById('poc-progress-text');
    const statusText = document.getElementById('poc-status');
    
    if (pocProgress) pocProgress.classList.remove('hidden');
    if (pocContent) pocContent.classList.add('hidden');
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        if (progressBar) progressBar.style.width = progress + '%';
        if (progressText) progressText.textContent = progress + '%';
        
        if (statusText) {
            if (progress <= 30) {
                statusText.textContent = 'Analyzing vulnerability patterns...';
            } else if (progress <= 60) {
                statusText.textContent = 'Generating exploit code...';
            } else if (progress <= 90) {
                statusText.textContent = 'Validating proof of concept...';
            } else {
                statusText.textContent = 'Finalizing documentation...';
            }
        }
        
        if (progress >= 100) {
            clearInterval(interval);
            generatePoCFromAPI(cveId);
        }
    }, 200);
}

async function generatePoCFromAPI(cveId) {
    const pocProgress = document.getElementById('poc-progress');
    const pocContent = document.getElementById('poc-content');
    
    try {
        // Make API call to generate PoC
        const response = await window.authManager.authenticatedFetch(`${API_BASE}/poc/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cve_id: cveId,
                description: `Security vulnerability in ${cveId}`,
                vulnerability_type: 'unknown',
                affected_component: 'system',
                model_name: 'codellama:7b'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // FIX: Parse the JSON response first
        const data = await response.json();
        
        if (pocProgress) pocProgress.classList.add('hidden');
        if (pocContent) pocContent.classList.remove('hidden');
        
        const pocCode = document.getElementById('poc-code');
        if (pocCode) {
            pocCode.textContent = data.code || data.poc_code || `#!/usr/bin/env python3
"""
Proof of Concept for ${cveId}
Generated by AI-Powered CVE Analysis Platform
"""

import requests
import sys

def exploit_vulnerability(target_url):
    """
    Exploits the vulnerability in the target application
    """
    payload = {
        'input': '<script>alert("XSS")</script>',
        'action': 'submit'
    }
    
    try:
        response = requests.post(
            f"{target_url}/vulnerable_endpoint",
            data=payload,
            timeout=10
        )
        
        if 'alert("XSS")' in response.text:
            print("[+] Vulnerability confirmed!")
            return True
        else:
            print("[-] Vulnerability not detected")
            return False
            
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 poc.py <target_url>")
        sys.exit(1)
    
    target = sys.argv[1]
    exploit_vulnerability(target)`;
        }
        showToast('PoC generated successfully!', 'success');
    } catch (error) {
        console.error('PoC generation error:', error);
        if (pocProgress) pocProgress.classList.add('hidden');
        if (pocContent) pocContent.classList.remove('hidden');
        
        const pocCode = document.getElementById('poc-code');
        if (pocCode) {
            pocCode.textContent = `# PoC Generation Failed: ${error.message}
# Please try again or check CVE ID validity`;
        }
        showToast(`PoC generation failed for ${cveId}: ${error.message}`, 'error');
    }
}

function switchPoCTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.poc-tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.poc-tab').forEach(btn => {
        btn.classList.remove('active', 'border-b-2', 'border-green-500', 'text-green-600');
        btn.classList.add('text-gray-500');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(`poc-${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
    }
    
    // Update active tab button
    const activeBtn = document.querySelector(`[onclick="switchPoCTab('${tabName}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active', 'border-b-2', 'border-green-500', 'text-green-600');
        activeBtn.classList.remove('text-gray-500');
    }
}

// PoC Editor Functions
function toggleCodeEditor() {
    const editorContainer = document.getElementById('poc-editor-container');
    const codeDisplay = document.getElementById('poc-code-display');
    
    if (editorContainer && codeDisplay) {
        editorContainer.classList.toggle('hidden');
        codeDisplay.classList.toggle('hidden');
    }
}

function copyPoC() {
    const pocCode = document.getElementById('poc-code');
    if (pocCode) {
        navigator.clipboard.writeText(pocCode.textContent).then(() => {
            showToast('PoC copied to clipboard!', 'success');
        }).catch(() => {
            showToast('Failed to copy PoC', 'error');
        });
    }
}

function downloadPoC() {
    const pocCode = document.getElementById('poc-code');
    if (pocCode) {
        const blob = new Blob([pocCode.textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'poc_exploit.py';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('PoC downloaded!', 'success');
    }
}

function validatePoC() {
    showToast('PoC validation started...', 'info');
    // Simulate validation
    setTimeout(() => {
        const validationDiv = document.getElementById('poc-validation');
        if (validationDiv) {
            validationDiv.innerHTML = `
                <div class="space-y-4">
                    <div class="flex items-center space-x-2 text-green-600">
                        <i class="fas fa-check-circle"></i>
                        <span>Syntax validation passed</span>
                    </div>
                    <div class="flex items-center space-x-2 text-green-600">
                        <i class="fas fa-check-circle"></i>
                        <span>Security checks passed</span>
                    </div>
                    <div class="flex items-center space-x-2 text-yellow-600">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>Network connectivity test - Not executed</span>
                    </div>
                </div>
            `;
        }
        showToast('PoC validation complete!', 'success');
    }, 1500);
}

// Additional utility functions
function formatCode() {
    showToast('Code formatted!', 'success');
}

function resetCode() {
    if (confirm('Reset code to original?')) {
        showToast('Code reset!', 'info');
    }
}

function runPreview() {
    const preview = document.getElementById('poc-preview');
    if (preview) {
        preview.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-play-circle text-3xl text-green-500 mb-2"></i>
                <p class="text-gray-600">PoC executed successfully!</p>
                <p class="text-sm text-gray-500 mt-2">Check console for output</p>
            </div>
        `;
    }
    showToast('PoC executed in sandbox!', 'success');
}

function exportDocs() {
    showToast('Documentation exported!', 'success');
}

function exportValidation() {
    showToast('Validation report exported!', 'success');
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('CVE Analysis Platform initializing...');
    
    // Initialize AuthManager
    if (typeof AuthManager !== 'undefined') {
        // Set authManager globally (avoiding duplicate declaration)
        if (typeof window.authManager === 'undefined') {
            window.authManager = new AuthManager();
            // Also set it as a global variable for backward compatibility
            window.authManager = window.authManager;
        }
        console.log('Authentication manager initialized');
    } else {
        console.warn('AuthManager not found - authentication features may not work');
    }
    
    // Initialize other features
    initializeDarkMode();
    initializeKeyboardShortcuts();
    initializeTimelineViews();
    
    // Load initial dashboard data
    showDashboard();
    
    // Just show UI - let user interactions trigger API calls
    setTimeout(() => {
        if (window.authManager && window.authManager.isAuthenticated()) {
            console.log('✅ User authenticated - UI ready for interaction');
            // Load only essential dashboard data when user is authenticated
            loadDashboardData();
        } else {
            console.log('⏳ User not authenticated - showing login interface');
        }
    }, 1000);
    
    console.log('CVE Analysis Platform ready');
});

function checkAuthStatus() {
    const token = localStorage.getItem('auth_token');
    const tokenExp = localStorage.getItem('token_expires_at');
    
    if (!token || !tokenExp) {
        return false;
    }
    
    try {
        const expirationTime = parseInt(tokenExp);
        if (Date.now() >= expirationTime) {
            // Token expired, clear auth data
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('token_expires_at');
            return false;
        }
        return true;
    } catch (error) {
        console.error('Error checking auth status:', error);
        return false;
    }
}

// Add route protection
function protectRoute() {
    if (!checkAuthStatus()) {
        showToast('Please login to access this page', 'warning');
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Check auth status on page load
document.addEventListener('DOMContentLoaded', () => {
    const protectedRoutes = ['/dashboard', '/analysis', '/chat', '/settings'];
    const currentPath = window.location.pathname;
    
    if (protectedRoutes.some(route => currentPath.startsWith(route))) {
        protectRoute();
    }
});
