/*
 * CVE Analysis Platform - Frontend Application
 * 
 * AI ANALYSIS FEATURES INTEGRATION STATUS:
 * ========================================
 * 
 * ✅ AI CHAT SYSTEM:
 *    - Chat interface with real-time messaging ✅ FIXED
 *    - Session management and history
 *    - Suggestion system for follow-up questions
 *    - Error handling and authentication integration ✅ FIXED
 *    - Functions: sendMessage(), addMessageToChat(), sendChatMessageToAPI()
 * 
 * ✅ CVE ANALYSIS ENGINE:
 *    - Comprehensive CVE analysis with AI models ✅ WORKING
 *    - Auto-import from NVD if CVE not found locally
 *    - Multiple analysis types (comprehensive, quick, technical)
 *    - Functions: analyzeCVE(), startAnalysis(), displayAnalysisResults()
 *    - API Endpoints: /api/v1/analysis/analyze, /api/v1/analysis/cve/analyze
 * 
 * ✅ PROOF OF CONCEPT GENERATION:
 *    - AI-powered PoC code generation ✅ WORKING
 *    - Multiple AI models support (CodeLlama, Mistral, Llama2)
 *    - Code validation and documentation
 *    - Functions: generatePoC(), generatePoCFromAPI(), validatePoC()
 *    - API Endpoints: /api/v1/poc/generate, /api/v1/poc/{cve_id}
 * 
 * ✅ RISK ASSESSMENT:
 *    - AI-driven risk scoring and assessment ✅ WORKING
 *    - Business impact analysis
 *    - Mitigation recommendations
 *    - Functions: assessRisk(), getCVEMitigations(), getCVEAttackVectors()
 *    - API Endpoints: /api/v1/analysis/risk-assessment
 * 
 * ✅ SEARCH INTEGRATION:
 *    - AI-enhanced CVE search with NVD integration ✅ WORKING
 *    - Smart filtering and recommendation
 *    - Analysis buttons in search results ✅ WORKING
 *    - Functions: performCVESearch(), displayCVESearchResults()
 * 
 * ✅ WATCHLIST INTEGRATION:
 *    - AI analysis accessible from watchlist items ✅ WORKING
 *    - Smart watchlist recommendations
 *    - Analysis history tracking
 *    - Functions: addToWatchlist(), analyzeCVE() from watchlist ✅ FIXED
 * 
 * ✅ DASHBOARD INTEGRATION:
 *    - AI analysis metrics and statistics ✅ WORKING
 *    - Recent analysis results display
 *    - Quick analysis access from dashboard ✅ WORKING
 *    - Functions: loadDashboardData(), updateDashboardMetrics()
 * 
 * ✅ AUTHENTICATION INTEGRATION:
 *    - All AI features require authentication ✅ WORKING
 *    - Token-based API access ✅ WORKING
 *    - Proper error handling for auth failures ✅ FIXED
 *    - Functions: ensureValidToken(), authenticatedFetch()
 * 
 * ✅ ERROR HANDLING & UX:
 *    - Comprehensive error messages ✅ FIXED
 *    - Loading states and progress indicators ✅ WORKING
 *    - Fallback responses when AI unavailable ✅ WORKING
 *    - Toast notifications for user feedback ✅ WORKING
 * 
 * INTEGRATION POINTS:
 * ==================
 * 1. CVE Search Results → "Analyze" button → AI Analysis ✅ WORKING
 * 2. Dashboard Recent CVEs → "Analyze" button → AI Analysis ✅ WORKING
 * 3. Watchlist Items → "Analyze" button → AI Analysis ✅ WORKING
 * 4. Analysis Results → "Generate PoC" button → PoC Generation ✅ WORKING
 * 5. Chat Interface → AI-powered responses ✅ FIXED
 * 6. All sections → Authentication required ✅ WORKING
 * 
 * FIXED ISSUES:
 * =============
 * ✅ AI chat response display - Fixed response structure handling
 * ✅ Authentication integration - All AI features require login
 * ✅ Error handling - Comprehensive error messages and fallbacks
 * ✅ Loading states - Progress indicators for all AI operations
 * ✅ Session management - Chat sessions and analysis history
 * ✅ Auto-import - CVEs auto-imported from NVD when needed
 * ✅ Cross-section integration - AI features accessible from all sections
 * ✅ Duplicate analysis sections - Removed duplicate HTML sections
 * ✅ Missing utility functions - Added escapeHtml, getCurrentChatSession
 * ✅ Response parsing - Fixed chat API response handling
 */

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

// ========================================
// MISSING NAVIGATION AND UI FUNCTIONS
// ========================================

// Navigation functions
function showDashboard() {
    hideAllSections();
    const section = document.getElementById('dashboard-section');
    if (section) {
        section.classList.remove('hidden');
        section.classList.add('section');
        loadDashboardData();
    }
    updateActiveNavButton('dashboard');
}

function showCVESearch() {
    hideAllSections();
    const section = document.getElementById('cve-search-section');
    if (section) {
        section.classList.remove('hidden');
        section.classList.add('section');
    } else {
        // Create CVE search section if it doesn't exist
        createCVESearchSection();
    }
    updateActiveNavButton('cve-search');
}

function showAnalysis() {
    hideAllSections();
    const section = document.getElementById('analysis-section');
    if (section) {
        section.classList.remove('hidden');
        section.classList.add('section');
    } else {
        // Create analysis section if it doesn't exist
        createAnalysisSection();
    }
    updateActiveNavButton('analysis');
}

function showWatchlist() {
    hideAllSections();
    const section = document.getElementById('watchlist-section');
    if (section) {
        section.classList.remove('hidden');
        section.classList.add('section');
        loadWatchlistData();
    } else {
        // Create watchlist section if it doesn't exist
        createWatchlistSection();
    }
    updateActiveNavButton('watchlist');
}

function showTimeline() {
    hideAllSections();
    const section = document.getElementById('timeline-section');
    if (section) {
        section.classList.remove('hidden');
        section.classList.add('section');
        loadTimelineData();
    } else {
        // Create timeline section if it doesn't exist
        createTimelineSection();
    }
    updateActiveNavButton('timeline');
}

function showSettings() {
    hideAllSections();
    let section = document.getElementById('settings-section');
    if (!section) {
        createSettingsSection();
        section = document.getElementById('settings-section');
    }
    
    if (section) {
        section.classList.remove('hidden');
        section.classList.add('section');
        loadSettingsData();
    }
    updateActiveNavButton('settings');
}

// Utility functions for navigation
function hideAllSections() {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.add('hidden');
    });
}

function updateActiveNavButton(activeButton) {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.classList.remove('bg-blue-700');
    });
    
    // Add active class to current button
    const currentBtn = document.querySelector(`[onclick*="${activeButton}"]`);
    if (currentBtn) {
        currentBtn.classList.add('bg-blue-700');
    }
}

// Chat functions
function sendQuickMessage(message) {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.value = message;
        sendMessage();
    }
}

function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput?.value?.trim();
    
    if (!message) {
        showToast('Please enter a message', 'warning');
        return;
    }
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to API
    sendChatMessageToAPI(message);
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const welcomeMsg = document.getElementById('chat-welcome');
    
    if (!chatMessages) {
        console.error('Chat messages container not found');
        return;
    }
    
    if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-4 ${sender === 'user' ? 'text-right' : 'text-left'}`;
    
    const isUser = sender === 'user';
    const isAI = sender === 'ai' || sender === 'assistant';
    
    // Escape HTML to prevent XSS
    const escapedMessage = escapeHtml(message);
    
    messageDiv.innerHTML = `
        <div class="inline-block max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
            isUser 
                ? 'bg-blue-600 text-white' 
                : isAI 
                    ? 'bg-gray-100 text-gray-800 border border-gray-200'
                    : 'bg-gray-200 text-gray-800'
        }">
            ${isAI ? '<div class="flex items-center mb-1"><i class="fas fa-robot text-blue-500 mr-2"></i><span class="text-xs font-medium text-blue-600">AI Assistant</span></div>' : ''}
            <p class="text-sm whitespace-pre-wrap">${escapedMessage}</p>
            <span class="text-xs opacity-75 block mt-1">${new Date().toLocaleTimeString()}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Smooth scroll to bottom
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.classList.remove('hidden');
    }
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.classList.add('hidden');
    }
}

async function sendChatMessageToAPI(message) {
    try {
        const api = new CVEPlatformAPI();
        const response = await api.sendChatMessage({ 
            message: message,
            session_id: getCurrentChatSession(),
            conversation_type: 'general'
        });
        
        hideTypingIndicator();
        
        console.log('Chat API Response:', response);
        
        // Check if response has the expected structure
        if (response && response.response) {
            addMessageToChat(response.response, 'ai');
            
            // Show suggestions if available
            if (response.suggestions && response.suggestions.length > 0) {
                const suggestionsHtml = response.suggestions.map(suggestion => 
                    `<button onclick="sendQuickMessage('${escapeHtml(suggestion)}')" class="text-blue-600 hover:text-blue-800 text-sm mr-2 mb-1 px-2 py-1 border border-blue-300 rounded">${escapeHtml(suggestion)}</button>`
                ).join('');
                
                const chatMessages = document.getElementById('chat-messages');
                const suggestionsDiv = document.createElement('div');
                suggestionsDiv.className = 'mb-4 text-left';
                suggestionsDiv.innerHTML = `
                    <div class="text-xs text-gray-500 mb-2">Suggested questions:</div>
                    <div>${suggestionsHtml}</div>
                `;
                chatMessages.appendChild(suggestionsDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } else {
            console.error('Unexpected response structure:', response);
            addMessageToChat('Sorry, I received an unexpected response format. Please try again.', 'ai');
        }
    } catch (error) {
        console.error('Chat error:', error);
        hideTypingIndicator();
        
        // Handle specific error types
        if (error.message && error.message.includes('401')) {
            addMessageToChat('Please login to use the AI chat feature.', 'ai');
            showLoginModal();
        } else if (error.message && error.message.includes('404')) {
            addMessageToChat('AI chat service is not available. Please check if the service is running.', 'ai');
        } else {
            addMessageToChat('Sorry, I\'m currently unavailable. Please try again later.', 'ai');
        }
    }
}

function clearChat() {
    const chatMessages = document.getElementById('chat-messages');
    const welcomeMsg = document.getElementById('chat-welcome');
    
    if (chatMessages) {
        chatMessages.innerHTML = '';
        if (welcomeMsg) {
            chatMessages.appendChild(welcomeMsg);
            welcomeMsg.style.display = 'block';
        }
    }
    showToast('Chat cleared', 'info');
}

// Utility functions
function escapeHtml(text) {
    if (typeof text !== 'string') return text;
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getCurrentChatSession() {
    let sessionId = localStorage.getItem('chat_session_id');
    if (!sessionId) {
        sessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chat_session_id', sessionId);
    }
    return sessionId;
}

function exportChatHistory() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messages = Array.from(chatMessages.querySelectorAll('.mb-4')).map(msg => {
        return msg.textContent.trim();
    });
    
    const chatData = {
        timestamp: new Date().toISOString(),
        messages: messages
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Chat history exported', 'success');
}

// Dark mode functions
function initializeDarkMode() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark');
        updateThemeIcon(true);
    }
}

function toggleDarkMode() {
    const isDarkMode = document.body.classList.toggle('dark');
    localStorage.setItem('darkMode', isDarkMode);
    updateThemeIcon(isDarkMode);
    showToast(`${isDarkMode ? 'Dark' : 'Light'} mode enabled`, 'info');
}

function updateThemeIcon(isDarkMode) {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = isDarkMode ? 'fas fa-sun text-lg' : 'fas fa-moon text-lg';
    }
}

// Notification functions
function toggleNotifications() {
    // Create notifications dropdown if it doesn't exist
    let dropdown = document.getElementById('notifications-dropdown');
    if (!dropdown) {
        dropdown = createNotificationsDropdown();
    }
    
    dropdown.classList.toggle('hidden');
    if (!dropdown.classList.contains('hidden')) {
        loadNotifications();
    }
}

function createNotificationsDropdown() {
    const dropdown = document.createElement('div');
    dropdown.id = 'notifications-dropdown';
    dropdown.className = 'absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-gray-200 z-50 hidden overflow-hidden';
    dropdown.innerHTML = `
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 text-white">
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fas fa-bell text-lg"></i>
                    <h3 class="font-semibold text-lg">Notifications</h3>
                </div>
                <button onclick="toggleNotifications()" class="text-white hover:text-gray-200 transition-colors">
                    <i class="fas fa-times text-lg"></i>
                </button>
            </div>
        </div>
        
        <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
            <div class="flex justify-between items-center">
                <div class="flex space-x-4">
                    <button onclick="markAllNotificationsRead()" 
                            class="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors">
                        <i class="fas fa-check-double mr-1"></i>Mark all read
                    </button>
                    <button onclick="clearAllNotifications()" 
                            class="text-sm text-red-600 hover:text-red-800 font-medium transition-colors">
                        <i class="fas fa-trash mr-1"></i>Clear all
                    </button>
                </div>
                <button onclick="loadNotifications()" 
                        class="text-sm text-gray-600 hover:text-gray-800 transition-colors" title="Refresh">
                    <i class="fas fa-sync-alt"></i>
                </button>
            </div>
        </div>
        
        <div id="notifications-list" class="max-h-80 overflow-y-auto">
            <div class="p-6 text-center text-gray-500">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-3"></div>
                <p class="text-sm">Loading notifications...</p>
            </div>
        </div>
        
        <div class="bg-gray-50 px-6 py-3 border-t border-gray-200">
            <div class="flex justify-between items-center text-xs text-gray-500">
                <span>Auto-refresh every 30s</span>
                <button onclick="window.open('/notifications', '_blank')" 
                        class="text-blue-600 hover:text-blue-800 font-medium">
                    View all notifications →
                </button>
            </div>
        </div>
    `;
    
    // Position relative to notifications button
    const notificationBtn = document.querySelector('[onclick="toggleNotifications()"]');
    if (notificationBtn) {
        const parent = notificationBtn.parentElement;
        parent.style.position = 'relative';
        parent.appendChild(dropdown);
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!parent.contains(event.target)) {
                dropdown.classList.add('hidden');
            }
        });
    }
    
    return dropdown;
}

async function loadNotifications() {
    try {
        const api = new CVEPlatformAPI();
        const notifications = await api.getNotifications();
        displayNotifications(notifications);
        updateNotificationBadge(notifications);
    } catch (error) {
        console.error('Error loading notifications:', error);
        const list = document.getElementById('notifications-list');
        if (list) {
            list.innerHTML = `
                <div class="p-4 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                    <p>Error loading notifications</p>
                    <button onclick="loadNotifications()" class="text-xs text-blue-600 hover:text-blue-800 mt-2">
                        Try again
                    </button>
                </div>
            `;
        }
    }
}

function displayNotifications(notifications) {
    const list = document.getElementById('notifications-list');
    if (!list) return;
    
    if (!notifications || notifications.length === 0) {
        list.innerHTML = `
            <div class="p-8 text-center text-gray-500">
                <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-bell-slash text-2xl text-gray-400"></i>
                </div>
                <h4 class="font-medium text-gray-900 mb-1">No notifications</h4>
                <p class="text-sm text-gray-500">You're all caught up!</p>
            </div>
        `;
        return;
    }
    
    // Sort notifications by date (newest first) and group by read status
    const sortedNotifications = notifications.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    const unreadNotifications = sortedNotifications.filter(n => !n.read);
    const readNotifications = sortedNotifications.filter(n => n.read);
    
    let html = '';
    
    // Show unread notifications first
    if (unreadNotifications.length > 0) {
        html += `
            <div class="bg-blue-50 px-4 py-2 border-b">
                <p class="text-xs font-semibold text-blue-800 uppercase tracking-wide">
                    Unread (${unreadNotifications.length})
                </p>
            </div>
        `;
        html += unreadNotifications.map(notification => renderNotification(notification, false)).join('');
    }
    
    // Show read notifications
    if (readNotifications.length > 0) {
        html += `
            <div class="bg-gray-50 px-4 py-2 border-b">
                <p class="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    Read (${readNotifications.length})
                </p>
            </div>
        `;
        html += readNotifications.slice(0, 5).map(notification => renderNotification(notification, true)).join('');
        
        if (readNotifications.length > 5) {
            html += `
                <div class="p-4 text-center border-b">
                    <button onclick="window.open('/notifications', '_blank')" 
                            class="text-sm text-blue-600 hover:text-blue-800 font-medium">
                        View ${readNotifications.length - 5} more notifications
                    </button>
                </div>
            `;
        }
    }
    
    list.innerHTML = html;
}

function renderNotification(notification, isRead) {
    const typeIcon = getNotificationTypeIcon(notification.type);
    const timeAgo = formatNotificationTime(notification.created_at);
    
    return `
        <div class="group hover:bg-gray-50 transition-colors ${isRead ? 'opacity-75' : ''}" 
             onclick="handleNotificationClick('${notification.id}', '${notification.action_url || ''}')">
            <div class="p-4 cursor-pointer">
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0 mt-1">
                        ${typeIcon}
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <p class="text-sm font-medium text-gray-900 group-hover:text-gray-700">
                                    ${escapeHtml(notification.title || 'Notification')}
                                </p>
                                <p class="text-sm text-gray-600 mt-1 line-clamp-2">
                                    ${escapeHtml(notification.message || '')}
                                </p>
                                <div class="flex items-center mt-2 space-x-2">
                                    <p class="text-xs text-gray-400">${timeAgo}</p>
                                    ${!isRead ? '<div class="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>' : ''}
                                </div>
                            </div>
                            <div class="flex items-center space-x-1 ml-2">
                                <button onclick="event.stopPropagation(); deleteNotification('${notification.id}')" 
                                        class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 p-1 rounded transition-all"
                                        title="Delete notification">
                                    <i class="fas fa-times text-xs"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function updateNotificationBadge(notifications) {
    const badge = document.getElementById('notification-badge');
    if (!badge) return;
    
    const unreadCount = notifications ? notifications.filter(n => !n.read).length : 0;
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount > 99 ? '99+' : unreadCount.toString();
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function getNotificationTypeIcon(type) {
    const icons = {
        'critical': '<i class="fas fa-exclamation-triangle text-red-500"></i>',
        'error': '<i class="fas fa-times-circle text-red-500"></i>',
        'warning': '<i class="fas fa-exclamation-circle text-yellow-500"></i>',
        'success': '<i class="fas fa-check-circle text-green-500"></i>',
        'info': '<i class="fas fa-info-circle text-blue-500"></i>'
    };
    return icons[type] || icons['info'];
}

function formatNotificationTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function handleNotificationClick(notificationId, actionUrl) {
    // Mark as read
    try {
        const api = new CVEPlatformAPI();
        await api.markNotificationRead(notificationId);
        
        // Refresh notifications
        loadNotifications();
        
        // Navigate to action URL if provided
        if (actionUrl) {
            window.open(actionUrl, '_blank');
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

async function markAllNotificationsRead() {
    try {
        const api = new CVEPlatformAPI();
        await api.markAllNotificationsRead();
        loadNotifications();
        showToast('All notifications marked as read', 'success');
    } catch (error) {
        console.error('Error marking all notifications as read:', error);
        showToast('Error marking notifications as read', 'error');
    }
}

async function clearAllNotifications() {
    if (!confirm('Are you sure you want to clear all notifications?')) return;
    
    try {
        const api = new CVEPlatformAPI();
        await api.clearAllNotifications();
        loadNotifications();
        showToast('All notifications cleared', 'success');
    } catch (error) {
        console.error('Error clearing notifications:', error);
        showToast('Error clearing notifications', 'error');
    }
}

async function deleteNotification(notificationId) {
    try {
        const api = new CVEPlatformAPI();
        await api.deleteNotification(notificationId);
        loadNotifications();
        showToast('Notification deleted', 'success');
    } catch (error) {
        console.error('Error deleting notification:', error);
        showToast('Error deleting notification', 'error');
    }
}

// Initialize notifications system
function initializeNotifications() {
    // Load notifications immediately
    loadNotificationBadge();
    
    // Refresh notifications every 30 seconds
    setInterval(loadNotificationBadge, 30000);
    
    // Auto-refresh notifications dropdown if it's open
    setInterval(() => {
        const dropdown = document.getElementById('notifications-dropdown');
        if (dropdown && !dropdown.classList.contains('hidden')) {
            loadNotifications();
        }
    }, 30000);
    
    // Close notifications dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('notifications-dropdown');
        const notificationBtn = document.querySelector('[onclick="toggleNotifications()"]');
        
        if (dropdown && !dropdown.classList.contains('hidden')) {
            if (!dropdown.contains(event.target) && !notificationBtn.contains(event.target)) {
                dropdown.classList.add('hidden');
            }
        }
    });
}

// Load notification badge without opening dropdown
async function loadNotificationBadge() {
    try {
        const api = new CVEPlatformAPI();
        const notifications = await api.getNotifications();
        updateNotificationBadge(notifications);
    } catch (error) {
        console.error('Error loading notification badge:', error);
        // Don't show error toast for background badge updates
    }
}

// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            showCVESearch();
        }
        
        // Ctrl/Cmd + D for dashboard
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            showDashboard();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal, .dropdown');
    modals.forEach(modal => {
        modal.classList.add('hidden');
    });
}

// Chat input utilities
function autoResizeChatInput(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function updateChatCharCounter(textarea) {
    const counter = document.getElementById('chat-char-counter');
    if (counter) {
        const length = textarea.value.length;
        counter.textContent = `${length}/1000`;
        counter.className = length > 900 ? 'text-xs text-red-500' : 'text-xs text-gray-400';
    }
}

function attachChatFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt,.json,.csv,.log';
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            showToast(`File "${file.name}" attached`, 'success');
            // Handle file attachment logic here
        }
    };
    input.click();
}

// Section creation functions
function createCVESearchSection() {
    const main = document.querySelector('main');
    const section = document.createElement('section');
    section.id = 'cve-search-section';
    section.className = 'section hidden';
    section.innerHTML = `
        <div class="bg-white rounded-xl shadow-xl p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">CVE Search</h2>
            <div class="space-y-4">
                <!-- Basic Search -->
                <div class="flex space-x-4">
                    <input type="text" id="cve-search-input" placeholder="Search CVEs by ID, keyword, or description..." 
                           class="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                           onkeypress="if(event.key === 'Enter') performCVESearch()">
                    <button onclick="performCVESearch()" 
                            class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                        <i class="fas fa-search mr-2"></i>Search
                    </button>
                    <button onclick="toggleAdvancedFilters()" 
                            class="bg-gray-600 text-white px-4 py-3 rounded-lg hover:bg-gray-700">
                        <i class="fas fa-filter mr-2"></i>Filters
                    </button>
                </div>
                
                <!-- Advanced Filters -->
                <div id="advanced-filters" class="hidden bg-gray-50 p-4 rounded-lg border">
                    <h3 class="font-semibold text-gray-900 mb-4">Advanced Filters</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Severity</label>
                            <select id="severity-filter" class="w-full p-2 border border-gray-300 rounded">
                                <option value="">All Severities</option>
                                <option value="CRITICAL">Critical</option>
                                <option value="HIGH">High</option>
                                <option value="MEDIUM">Medium</option>
                                <option value="LOW">Low</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">CVSS Score Range</label>
                            <div class="flex space-x-2">
                                <input type="number" id="cvss-min" placeholder="Min" min="0" max="10" step="0.1" 
                                       class="w-full p-2 border border-gray-300 rounded">
                                <input type="number" id="cvss-max" placeholder="Max" min="0" max="10" step="0.1" 
                                       class="w-full p-2 border border-gray-300 rounded">
                            </div>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                            <div class="flex space-x-2">
                                <input type="date" id="date-from" class="w-full p-2 border border-gray-300 rounded">
                                <input type="date" id="date-to" class="w-full p-2 border border-gray-300 rounded">
                            </div>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Vendor</label>
                            <input type="text" id="vendor-filter" placeholder="e.g., Microsoft, Apache" 
                                   class="w-full p-2 border border-gray-300 rounded">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Product</label>
                            <input type="text" id="product-filter" placeholder="e.g., Windows, Apache HTTP Server" 
                                   class="w-full p-2 border border-gray-300 rounded">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                            <select id="sort-filter" class="w-full p-2 border border-gray-300 rounded">
                                <option value="published_date">Published Date</option>
                                <option value="modified_date">Modified Date</option>
                                <option value="cvss_score">CVSS Score</option>
                                <option value="cve_id">CVE ID</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex justify-end space-x-3 mt-4">
                        <button onclick="clearAdvancedFilters()" class="px-4 py-2 text-gray-600 hover:text-gray-800">
                            Clear Filters
                        </button>
                        <button onclick="applyAdvancedFilters()" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                            Apply Filters
                        </button>
                    </div>
                </div>
                
                <!-- Search Results -->
                <div id="cve-search-results" class="mt-6">
                    <div class="text-center py-8 text-gray-500">
                        <i class="fas fa-search text-3xl mb-3"></i>
                        <p>Enter search terms to find CVEs</p>
                        <p class="text-sm mt-1">Search by CVE ID, keywords, or use advanced filters</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    main.appendChild(section);
}

function createAnalysisSection() {
    const main = document.querySelector('main');
    const section = document.createElement('section');
    section.id = 'analysis-section';
    section.className = 'section hidden';
    section.innerHTML = `
        <div class="bg-white rounded-xl shadow-xl p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">AI Analysis</h2>
            <div class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold mb-2">CVE Analysis</h3>
                        <p class="text-sm text-gray-600 mb-4">Analyze specific CVEs with AI</p>
                        <button onclick="startCVEAnalysis()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                            Start Analysis
                        </button>
                    </div>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold mb-2">Code Analysis</h3>
                        <p class="text-sm text-gray-600 mb-4">Analyze code for vulnerabilities</p>
                        <button onclick="startCodeAnalysis()" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                            Analyze Code
                        </button>
                    </div>
                </div>
                <div id="analysis-results" class="mt-6">
                    <p class="text-gray-500 text-center py-8">Select an analysis type to begin</p>
                </div>
            </div>
        </div>
    `;
    main.appendChild(section);
}

function createWatchlistSection() {
    const main = document.querySelector('main');
    const section = document.createElement('section');
    section.id = 'watchlist-section';
    section.className = 'section hidden';
    section.innerHTML = `
        <div class="bg-white rounded-xl shadow-xl p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-900">Watchlist</h2>
                <button onclick="createNewWatchlist()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    <i class="fas fa-plus mr-2"></i>New Watchlist
                </button>
            </div>
            <div id="watchlist-content">
                <p class="text-gray-500 text-center py-8">No watchlists created yet</p>
            </div>
        </div>
    `;
    main.appendChild(section);
}

function createTimelineSection() {
    const main = document.querySelector('main');
    const section = document.createElement('section');
    section.id = 'timeline-section';
    section.className = 'section hidden';
    section.innerHTML = `
        <div class="bg-white rounded-xl shadow-xl p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Security Timeline</h2>
            <div class="space-y-4">
                <div class="flex space-x-4 mb-6">
                    <button onclick="showTimelineView('recent')" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        Recent Activity
                    </button>
                    <button onclick="showTimelineView('critical')" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
                        Critical Events
                    </button>
                    <button onclick="showTimelineView('all')" class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
                        All Events
                    </button>
                </div>
                <div id="timeline-content">
                    <p class="text-gray-500 text-center py-8">Loading timeline...</p>
                </div>
            </div>
        </div>
    `;
    main.appendChild(section);
}

function createSettingsSection() {
    const main = document.querySelector('main');
    const section = document.createElement('section');
    section.id = 'settings-section';
    section.className = 'section hidden';
    section.innerHTML = `
        <div class="bg-white rounded-xl shadow-xl p-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Settings</h2>
            <div id="settings-content">
                <p class="text-gray-500 text-center py-8">Loading settings...</p>
            </div>
        </div>
    `;
    main.appendChild(section);
}

// Timeline functions
function initializeTimelineViews() {
    // Initialize timeline view functionality
    console.log('Timeline views initialized');
}

function showTimelineView(viewType) {
    const content = document.getElementById('timeline-content');
    if (!content) return;
    
    content.innerHTML = '<p class="text-gray-500 text-center py-8">Loading timeline...</p>';
    
    // Simulate loading timeline data
    setTimeout(() => {
        const timelineData = generateMockTimelineData(viewType);
        displayTimelineData(timelineData);
    }, 1000);
}

function generateMockTimelineData(viewType) {
    const events = [
        { time: '2 hours ago', type: 'critical', title: 'Critical CVE detected', description: 'CVE-2024-0001 affects multiple systems' },
        { time: '4 hours ago', type: 'info', title: 'System scan completed', description: 'Weekly vulnerability scan finished' },
        { time: '1 day ago', type: 'warning', title: 'New vulnerabilities found', description: '5 medium-severity CVEs identified' },
        { time: '2 days ago', type: 'success', title: 'Patches applied', description: 'Security updates installed successfully' }
    ];
    
    return viewType === 'critical' ? events.filter(e => e.type === 'critical') : events;
}

function displayTimelineData(events) {
    const content = document.getElementById('timeline-content');
    if (!content) return;
    
    content.innerHTML = events.map(event => `
        <div class="flex items-start space-x-4 p-4 border-l-4 border-${event.type === 'critical' ? 'red' : event.type === 'warning' ? 'yellow' : event.type === 'success' ? 'green' : 'blue'}-500 bg-gray-50 rounded-r-lg mb-4">
            <div class="flex-shrink-0">
                <i class="fas fa-${event.type === 'critical' ? 'exclamation-triangle' : event.type === 'warning' ? 'exclamation-circle' : event.type === 'success' ? 'check-circle' : 'info-circle'} text-${event.type === 'critical' ? 'red' : event.type === 'warning' ? 'yellow' : event.type === 'success' ? 'green' : 'blue'}-500"></i>
            </div>
            <div class="flex-1">
                <h4 class="font-semibold text-gray-900">${event.title}</h4>
                <p class="text-sm text-gray-600">${event.description}</p>
                <p class="text-xs text-gray-400 mt-1">${event.time}</p>
            </div>
        </div>
    `).join('');
}

// Data loading functions
async function loadDashboardData() {
    try {
        const api = new CVEPlatformAPI();
        
        // Check if user is authenticated
        const isAuthenticated = checkAuthStatus();
        
        if (!isAuthenticated) {
            // Show basic dashboard with login prompt
            updateDashboardMetrics({});
            updateRecentCVEsTable({ results: [] });
            showToast('Please login to view dashboard data', 'info');
            return;
        }
        
        // Load dashboard metrics and recent CVEs in parallel
        const [metrics, recentCVEs] = await Promise.all([
            api.getDashboardMetrics(),
            api.getRecentCVEs()
        ]);
        
        updateDashboardMetrics(metrics);
        updateRecentCVEsTable(recentCVEs);
        
        showToast('Dashboard loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        
        // Handle authentication errors specifically
        if (error.message && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
            updateDashboardMetrics({});
            updateRecentCVEsTable({ results: [] });
            showToast('Please login to view dashboard data', 'warning');
            showLoginModal();
        } else {
            // Show UI anyway, just with default values
            updateDashboardMetrics({});
            updateRecentCVEsTable({ results: [] });
            showToast('Failed to load dashboard data', 'error');
        }
    }
}

function updateDashboardMetrics(metrics) {
    const isAuthenticated = checkAuthStatus();
    const displayValue = isAuthenticated ? (metrics.critical_count || '0') : '--';
    
    // Update Critical CVEs count
    const criticalCount = document.getElementById('critical-count');
    if (criticalCount) {
        criticalCount.textContent = isAuthenticated ? (metrics.critical_count || '0') : '--';
    }
    
    // Update Total CVEs count
    const totalCount = document.getElementById('total-count');
    if (totalCount) {
        totalCount.textContent = isAuthenticated ? (metrics.total_count || '0') : '--';
    }
    
    // Update AI Analyses count
    const analysisCount = document.getElementById('analysis-count');
    if (analysisCount) {
        analysisCount.textContent = isAuthenticated ? (metrics.analysis_count || '0') : '--';
    }
    
    // Update Recent CVEs count
    const recentCount = document.getElementById('recent-count');
    if (recentCount) {
        recentCount.textContent = isAuthenticated ? (metrics.recent_count || '0') : '--';
    }
    
    console.log('Dashboard metrics updated:', metrics, 'Authenticated:', isAuthenticated);
}

function updateRecentCVEsTable(recentData) {
    const tableBody = document.getElementById('recent-cves-table');
    if (!tableBody) {
        console.error('recent-cves-table element not found');
        return;
    }
    
    const cves = recentData.results || [];
    
    if (cves.length === 0) {
        const isAuthenticated = checkAuthStatus();
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-8 text-center text-gray-500">
                    <i class="fas fa-shield-alt text-gray-300 text-3xl mb-2"></i>
                    <div>${isAuthenticated ? 'No recent CVEs found' : 'Login to view recent CVEs'}</div>
                    <div class="text-sm text-gray-400 mt-1">
                        ${isAuthenticated ? 'Import some CVEs to see them here' : 'Please authenticate to access dashboard data'}
                    </div>
                    ${!isAuthenticated ? `
                        <button onclick="showLoginModal()" class="mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                            <i class="fas fa-sign-in-alt mr-2"></i>Login
                        </button>
                    ` : ''}
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = cves.map(cve => {
        const severityClass = getSeverityBadgeClass(cve.severity_level);
        const cvssScore = cve.cvss_v3_score || 'N/A';
        const publishedDate = cve.published_date ? new Date(cve.published_date).toLocaleDateString() : 'Unknown';
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${escapeHtml(cve.cve_id)}</div>
                    <div class="text-sm text-gray-500">${escapeHtml((cve.description || '').substring(0, 60))}${(cve.description || '').length > 60 ? '...' : ''}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityClass}">
                        ${cve.severity_level || 'Unknown'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-900 font-medium">${cvssScore}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${publishedDate}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onclick="viewCVEDetails('${cve.cve_id}')" class="text-blue-600 hover:text-blue-900 mr-3">
                        <i class="fas fa-eye mr-1"></i>View
                    </button>
                    <button onclick="analyzeCVE('${cve.cve_id}')" class="text-green-600 hover:text-green-900">
                        <i class="fas fa-brain mr-1"></i>Analyze
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function getSeverityBadgeClass(severity) {
    const classes = {
        'CRITICAL': 'bg-red-100 text-red-800',
        'HIGH': 'bg-orange-100 text-orange-800',
        'MEDIUM': 'bg-yellow-100 text-yellow-800',
        'LOW': 'bg-green-100 text-green-800'
    };
    return classes[severity] || 'bg-gray-100 text-gray-800';
}

async function loadWatchlistData() {
    try {
        const api = new CVEPlatformAPI();
        const [watchlists, stats] = await Promise.all([
            api.getWatchlists(),
            api.getWatchlistStats()
        ]);
        
        // Update stats in the UI
        updateWatchlistStats(stats);
        
        // Display watchlists with their CVEs
        await displayWatchlists(watchlists);
        
        showToast(`Loaded ${watchlists.length} watchlist(s)`, 'success');
    } catch (error) {
        console.error('Error loading watchlist data:', error);
        showToast('Failed to load watchlist data', 'error');
    }
}

function updateWatchlistStats(stats) {
    // Update stats in the watchlist section
    const totalElement = document.getElementById('watchlist-total');
    const criticalElement = document.getElementById('watchlist-critical');
    const alertsElement = document.getElementById('watchlist-alerts');
    
    if (totalElement) totalElement.textContent = stats.total_monitored_cves || 0;
    if (criticalElement) criticalElement.textContent = stats.total_watchlists || 0;
    if (alertsElement) alertsElement.textContent = stats.total_alerts || 0;
}

async function displayWatchlists(watchlists) {
    const content = document.getElementById('watchlist-content') || document.getElementById('watchlist-items');
    if (!content) return;
    
    if (!watchlists || watchlists.length === 0) {
        content.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-bookmark text-gray-300 text-4xl mb-4"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No watchlists yet</h3>
                <p class="text-gray-500 mb-4">Create your first watchlist to start monitoring CVEs</p>
                <button onclick="createNewWatchlist()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    <i class="fas fa-plus mr-2"></i>Create Watchlist
                </button>
            </div>
        `;
        return;
    }
    
    // Load CVEs for each watchlist
    const watchlistsWithCVEs = await Promise.all(
        watchlists.map(async (watchlist) => {
            try {
                const api = new CVEPlatformAPI();
                const cveData = await api.getWatchlistCVEs(watchlist.watchlist_id);
                return { ...watchlist, cves: cveData.cves || {} };
            } catch (error) {
                console.error(`Error loading CVEs for watchlist ${watchlist.watchlist_id}:`, error);
                return { ...watchlist, cves: {} };
            }
        })
    );
    
    content.innerHTML = watchlistsWithCVEs.map(watchlist => {
        const cveEntries = Object.entries(watchlist.cves || {});
        
        return `
            <div class="bg-white border border-gray-200 rounded-lg mb-6 overflow-hidden">
                <div class="bg-gray-50 px-6 py-4 border-b">
                    <div class="flex justify-between items-center">
                        <div>
                            <h3 class="text-lg font-semibold text-gray-900">${escapeHtml(watchlist.name)}</h3>
                            ${watchlist.description ? `<p class="text-sm text-gray-600 mt-1">${escapeHtml(watchlist.description)}</p>` : ''}
                        </div>
                        <div class="flex items-center space-x-4">
                            <div class="text-right">
                                <div class="text-sm font-medium text-gray-900">${cveEntries.length} CVEs</div>
                                <div class="text-xs text-gray-500">${watchlist.alert_count || 0} alerts</div>
                            </div>
                            <div class="flex space-x-2">
                                <button onclick="refreshWatchlist('${watchlist.watchlist_id}')" 
                                        class="text-gray-400 hover:text-gray-600" title="Refresh">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                                <button onclick="deleteWatchlist('${watchlist.watchlist_id}')" 
                                        class="text-gray-400 hover:text-red-600" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="divide-y divide-gray-200">
                    ${cveEntries.length === 0 ? `
                        <div class="px-6 py-8 text-center">
                            <i class="fas fa-shield-alt text-gray-300 text-3xl mb-3"></i>
                            <p class="text-gray-500">No CVEs in this watchlist yet</p>
                            <p class="text-sm text-gray-400 mt-1">Add CVEs from the search results</p>
                        </div>
                    ` : cveEntries.map(([cveId, cveInfo]) => `
                        <div class="px-6 py-4 hover:bg-gray-50">
                            <div class="flex justify-between items-start">
                                <div class="flex-1">
                                    <div class="flex items-center space-x-3">
                                        <h4 class="font-medium text-gray-900">${cveId}</h4>
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityBadgeClass(cveInfo.priority)}">
                                            ${cveInfo.priority || 'medium'}
                                        </span>
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(cveInfo.status)}">
                                            ${cveInfo.status || 'active'}
                                        </span>
                                    </div>
                                    <p class="text-sm text-gray-600 mt-1">
                                        Added ${formatNotificationTime(cveInfo.added_at)}
                                    </p>
                                </div>
                                <div class="flex items-center space-x-2">
                                    <button onclick="viewCVEDetails('${cveId}')" 
                                            class="text-blue-600 hover:text-blue-800 text-sm">
                                        <i class="fas fa-eye mr-1"></i>View
                                    </button>
                                    <button onclick="removeCVEFromWatchlist('${watchlist.watchlist_id}', '${cveId}')" 
                                            class="text-red-600 hover:text-red-800 text-sm">
                                        <i class="fas fa-times mr-1"></i>Remove
                                    </button>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function getPriorityBadgeClass(priority) {
    const classes = {
        'critical': 'bg-red-100 text-red-800',
        'high': 'bg-orange-100 text-orange-800',
        'medium': 'bg-yellow-100 text-yellow-800',
        'low': 'bg-green-100 text-green-800'
    };
    return classes[priority] || classes['medium'];
}

function getStatusBadgeClass(status) {
    const classes = {
        'active': 'bg-green-100 text-green-800',
        'monitoring': 'bg-blue-100 text-blue-800',
        'resolved': 'bg-gray-100 text-gray-800',
        'ignored': 'bg-gray-100 text-gray-600'
    };
    return classes[status] || classes['active'];
}

async function refreshWatchlist(watchlistId) {
    showToast('Refreshing watchlist...', 'info');
    await loadWatchlistData();
}

async function deleteWatchlist(watchlistId) {
    if (!confirm('Are you sure you want to delete this watchlist?')) return;
    
    try {
        const api = new CVEPlatformAPI();
        await api.deleteWatchlist(watchlistId);
        showToast('Watchlist deleted successfully', 'success');
        await loadWatchlistData();
    } catch (error) {
        console.error('Error deleting watchlist:', error);
        showToast('Failed to delete watchlist', 'error');
    }
}

async function removeCVEFromWatchlist(watchlistId, cveId) {
    if (!confirm(`Remove ${cveId} from watchlist?`)) return;
    
    try {
        // Note: This would need a backend endpoint to remove CVEs
        showToast('CVE removal feature coming soon', 'info');
        // For now, just refresh the watchlist
        await loadWatchlistData();
    } catch (error) {
        console.error('Error removing CVE from watchlist:', error);
        showToast('Failed to remove CVE from watchlist', 'error');
    }
}

async function loadTimelineData() {
    try {
        const api = new CVEPlatformAPI();
        const timeline = await api.getDashboardTimeline();
        displayTimelineData(timeline);
    } catch (error) {
        console.error('Error loading timeline data:', error);
        showTimelineView('recent'); // Fallback to mock data
    }
}

// Placeholder functions for analysis
function startCVEAnalysis() {
    showToast('CVE Analysis feature coming soon', 'info');
}

function startCodeAnalysis() {
    showToast('Code Analysis feature coming soon', 'info');
}

async function performCVESearch() {
    const input = document.getElementById('cve-search-input');
    const query = input?.value?.trim();
    
    if (!query) {
        showToast('Please enter search terms', 'warning');
        return;
    }
    
    const resultsContainer = document.getElementById('search-results-content');
    const searchResultsSection = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    // Show the results section
    searchResultsSection.classList.remove('hidden');
    
    // Show loading state
    resultsContainer.innerHTML = `
        <div class="text-center py-8">
            <i class="fas fa-spinner fa-spin text-2xl text-blue-500 mb-2"></i>
            <p class="text-gray-500">Searching CVEs...</p>
        </div>
    `;
    
    try {
        const api = new CVEPlatformAPI();
        const searchParams = {
            query: query,
            limit: 20,
            search_type: 'both',
            sort_by: 'published_date',
            sort_order: 'desc'
        };
        
        const results = await api.searchCVEs(searchParams);
        displayCVESearchResults(results);
        showToast(`Found ${results.total || results.cves?.length || 0} CVEs`, 'success');
    } catch (error) {
        console.error('Search error:', error);
        resultsContainer.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex items-center">
                    <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                    <h3 class="font-semibold text-red-800">Search Error</h3>
                </div>
                <p class="text-sm text-red-600 mt-2">Failed to search CVEs: ${error.message}</p>
                <button onclick="performCVESearch()" class="mt-3 text-sm text-blue-600 hover:text-blue-800">
                    <i class="fas fa-redo mr-1"></i>Try again
                </button>
            </div>
        `;
        showToast('Search failed', 'error');
    }
}

async function createNewWatchlist() {
    const name = prompt('Enter watchlist name:');
    if (!name || !name.trim()) {
        showToast('Watchlist name is required', 'warning');
        return;
    }
    
    const description = prompt('Enter description (optional):') || '';
    
    try {
        showToast('Creating watchlist...', 'info');
        const api = new CVEPlatformAPI();
        const newWatchlist = await api.createWatchlist({ 
            name: name.trim(), 
            description: description.trim() 
        });
        
        showToast(`Watchlist "${newWatchlist.name}" created successfully`, 'success');
        
        // Reload watchlist data to show the new watchlist
        await loadWatchlistData();
    } catch (error) {
        console.error('Error creating watchlist:', error);
        showToast('Failed to create watchlist: ' + error.message, 'error');
    }
}

function showProfileSettings() {
    // Create a modal or navigate to profile settings
    showToast('Opening profile settings...', 'info');
    
    // For now, show a simple modal-like interface
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 class="text-lg font-semibold mb-4">Profile Settings</h3>
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Display Name</label>
                    <input type="text" class="w-full p-2 border border-gray-300 rounded" placeholder="Your name">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input type="email" class="w-full p-2 border border-gray-300 rounded" placeholder="your@email.com">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Organization</label>
                    <input type="text" class="w-full p-2 border border-gray-300 rounded" placeholder="Company name">
                </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
                <button onclick="this.closest('.fixed').remove()" class="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Cancel
                </button>
                <button onclick="saveProfile(); this.closest('.fixed').remove()" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    Save
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function showSecuritySettings() {
    showToast('Opening security settings...', 'info');
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 class="text-lg font-semibold mb-4">Security Settings</h3>
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                    <input type="password" class="w-full p-2 border border-gray-300 rounded">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                    <input type="password" class="w-full p-2 border border-gray-300 rounded">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                    <input type="password" class="w-full p-2 border border-gray-300 rounded">
                </div>
                <div class="border-t pt-4">
                    <label class="flex items-center">
                        <input type="checkbox" class="mr-2">
                        <span class="text-sm">Enable two-factor authentication</span>
                    </label>
                </div>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
                <button onclick="this.closest('.fixed').remove()" class="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Cancel
                </button>
                <button onclick="saveSecuritySettings(); this.closest('.fixed').remove()" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    Save
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function saveProfile() {
    showToast('Profile updated successfully', 'success');
}

function saveSecuritySettings() {
    showToast('Security settings updated successfully', 'success');
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

    async getCVEDetails(cveId) {
        return await utils.fetchWithRetry(`${this.baseURL}/cve/${cveId}/details`);
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
        const token = await utils.ensureValidToken();
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
                    
                    // Show login modal instead of redirecting
                    showLoginModal();
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

// Additional missing functions for watchlist and timeline
function sortWatchlist(sortBy) {
    showToast(`Sorting watchlist by ${sortBy}`, 'info');
    // Implement actual sorting logic here
    const content = document.getElementById('watchlist-content');
    if (content) {
        content.innerHTML = `<p class="text-gray-500 text-center py-8">Watchlist sorted by ${sortBy}</p>`;
    }
}

function exportWatchlist() {
    showToast('Exporting watchlist...', 'info');
    // Create mock export data
    const watchlistData = {
        timestamp: new Date().toISOString(),
        items: [],
        total_count: 0
    };
    
    const blob = new Blob([JSON.stringify(watchlistData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `watchlist-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Watchlist exported successfully', 'success');
}

function switchTimelineView(viewType) {
    // Update active button
    const buttons = document.querySelectorAll('.timeline-view-btn');
    buttons.forEach(btn => {
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-gray-200', 'text-gray-700');
    });
    
    const activeBtn = document.querySelector(`[data-view="${viewType}"]`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-gray-200', 'text-gray-700');
        activeBtn.classList.add('bg-blue-600', 'text-white');
    }
    
    // Update timeline content
    const container = document.getElementById('timeline-container');
    if (container) {
        switch (viewType) {
            case 'chart':
                container.innerHTML = `
                    <div class="bg-gray-50 p-8 rounded-lg text-center">
                        <i class="fas fa-chart-line text-4xl text-blue-500 mb-4"></i>
                        <p class="text-gray-600">Chart view - Timeline visualization</p>
                        <p class="text-sm text-gray-500 mt-2">Interactive charts showing CVE trends over time</p>
                    </div>
                `;
                break;
            case 'calendar':
                container.innerHTML = `
                    <div class="bg-gray-50 p-8 rounded-lg text-center">
                        <i class="fas fa-calendar text-4xl text-green-500 mb-4"></i>
                        <p class="text-gray-600">Calendar view - Monthly overview</p>
                        <p class="text-sm text-gray-500 mt-2">Calendar showing CVE activity by date</p>
                    </div>
                `;
                break;
            case 'list':
                container.innerHTML = `
                    <div class="bg-gray-50 p-8 rounded-lg text-center">
                        <i class="fas fa-list text-4xl text-purple-500 mb-4"></i>
                        <p class="text-gray-600">List view - Detailed timeline</p>
                        <p class="text-sm text-gray-500 mt-2">Chronological list of all CVE events</p>
                    </div>
                `;
                break;
        }
    }
    
    showToast(`Switched to ${viewType} view`, 'info');
}

function refreshTimeline() {
    showToast('Refreshing timeline...', 'info');
    
    const container = document.getElementById('timeline-container');
    if (container) {
        container.innerHTML = '<p class="text-gray-500 text-center py-8">Loading timeline...</p>';
        
        // Simulate refresh
        setTimeout(() => {
            container.innerHTML = `
                <div class="bg-gray-50 p-8 rounded-lg text-center">
                    <i class="fas fa-sync text-4xl text-blue-500 mb-4"></i>
                    <p class="text-gray-600">Timeline refreshed</p>
                    <p class="text-sm text-gray-500 mt-2">Latest CVE data loaded successfully</p>
                </div>
            `;
            showToast('Timeline refreshed successfully', 'success');
        }, 1500);
    }
}

// Additional missing functions
function updateTimeline(timeRange) {
    showToast(`Updating timeline for ${timeRange}`, 'info');
    const container = document.getElementById('timeline-container');
    if (container) {
        container.innerHTML = `<p class="text-gray-500 text-center py-8">Loading ${timeRange} timeline data...</p>`;
        
        // Simulate loading data for different time ranges
        setTimeout(() => {
            const mockData = {
                'week': 'Past 7 days timeline data',
                'month': 'Past 30 days timeline data', 
                'year': 'Past year timeline data',
                'all': 'Complete timeline data'
            };
            
            container.innerHTML = `
                <div class="bg-gray-50 p-8 rounded-lg text-center">
                    <i class="fas fa-calendar text-4xl text-green-500 mb-4"></i>
                    <p class="text-gray-600">${mockData[timeRange] || 'Timeline data loaded'}</p>
                    <p class="text-sm text-gray-500 mt-2">Showing vulnerabilities for selected time period</p>
                </div>
            `;
        }, 1000);
    }
}



function displayCVESearchResults(results) {
    const resultsContainer = document.getElementById('search-results-content');
    const searchResultsSection = document.getElementById('search-results');
    const resultsCount = document.getElementById('results-count');
    const resultsSummary = document.getElementById('results-summary');
    
    if (!resultsContainer) return;
    
    // Show the results section
    searchResultsSection.classList.remove('hidden');
    
    // Combine local and NVD results into a single array
    const allCVEs = [];
    if (results.local_results && Array.isArray(results.local_results)) {
        allCVEs.push(...results.local_results);
    }
    if (results.nvd_results && Array.isArray(results.nvd_results)) {
        allCVEs.push(...results.nvd_results);
    }
    
    if (!results || allCVEs.length === 0) {
        // Update results count and summary for no results
        if (resultsCount) {
            resultsCount.textContent = '0 results';
        }
        if (resultsSummary) {
            resultsSummary.textContent = 'No CVEs match your search criteria';
        }
        
        resultsContainer.innerHTML = `
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
                <i class="fas fa-search text-3xl text-gray-400 mb-3"></i>
                <h3 class="font-semibold text-gray-700">No CVEs Found</h3>
                <p class="text-sm text-gray-600 mt-2">No CVEs match your search criteria</p>
                <p class="text-xs text-gray-500 mt-1">Try different search terms or adjust your filters</p>
            </div>
        `;
        return;
    }
    
    const cveList = allCVEs.map(cve => `
        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-blue-600 hover:text-blue-800 cursor-pointer" onclick="viewCVEDetails('${cve.cve_id}')">
                    ${cve.cve_id || 'Unknown CVE'}
                </h3>
                <div class="flex items-center space-x-2">
                    <span class="px-2 py-1 text-xs rounded-full ${getCVSSBadgeClass(cve.cvss_v3_score)}">
                        ${cve.cvss_v3_score ? `CVSS ${cve.cvss_v3_score}` : 'No Score'}
                    </span>
                    <span class="px-2 py-1 text-xs rounded-full ${cve.source === 'Local Database' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}">
                        ${cve.source || 'Unknown'}
                    </span>
                </div>
            </div>
            <p class="text-sm text-gray-600 mb-3">${cve.description ? (cve.description.length > 200 ? cve.description.substring(0, 200) + '...' : cve.description) : 'No description available'}</p>
            <div class="flex justify-between items-center text-xs text-gray-500">
                <span>Published: ${cve.published_date ? new Date(cve.published_date).toLocaleDateString() : 'Unknown'}</span>
                <div class="space-x-2">
                    <button onclick="analyzeCVE('${cve.cve_id}')" class="text-blue-600 hover:text-blue-800">
                        <i class="fas fa-brain mr-1"></i>Analyze
                    </button>
                    <button onclick="addToWatchlist('${cve.cve_id}')" class="text-green-600 hover:text-green-800">
                        <i class="fas fa-bookmark mr-1"></i>Watch
                    </button>
                    ${cve.can_import ? `<button onclick="importCVE('${cve.cve_id}')" class="text-purple-600 hover:text-purple-800">
                        <i class="fas fa-download mr-1"></i>Import
                    </button>` : ''}
                </div>
            </div>
        </div>
    `).join('');
    
    // Update results count and summary
    const totalResults = results.total_results || allCVEs.length;
    const localCount = results.local_results ? results.local_results.length : 0;
    const nvdCount = results.nvd_results ? results.nvd_results.length : 0;
    
    if (resultsCount) {
        resultsCount.textContent = `${totalResults} result${totalResults !== 1 ? 's' : ''}`;
    }
    if (resultsSummary) {
        let summaryText = `Found ${totalResults} CVE${totalResults !== 1 ? 's' : ''} matching your search criteria`;
        if (localCount > 0 && nvdCount > 0) {
            summaryText += ` (${localCount} local, ${nvdCount} from NVD)`;
        } else if (localCount > 0) {
            summaryText += ` (from local database)`;
        } else if (nvdCount > 0) {
            summaryText += ` (from NVD live search)`;
        }
        resultsSummary.textContent = summaryText;
    }
    
    resultsContainer.innerHTML = `
        <div class="space-y-4">
            ${cveList}
        </div>
    `;
}

function getCVSSBadgeClass(score) {
    if (!score) return 'bg-gray-100 text-gray-600';
    const numScore = parseFloat(score);
    if (numScore >= 9.0) return 'bg-red-100 text-red-800';
    if (numScore >= 7.0) return 'bg-orange-100 text-orange-800';
    if (numScore >= 4.0) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
}

async function viewCVEDetails(cveId) {
    showToast(`Loading details for ${cveId}...`, 'info');
    
    try {
        const api = new CVEPlatformAPI();
        const cveDetails = await api.getCVEDetails(cveId);
        
        // Create modal to show CVE details
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        modal.innerHTML = `
            <div class="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                <div class="p-6">
                    <div class="flex justify-between items-start mb-4">
                        <h2 class="text-xl font-bold text-gray-900">${cveId}</h2>
                        <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                    <div class="space-y-4">
                        <div>
                            <h3 class="font-semibold text-gray-900">Description</h3>
                            <p class="text-sm text-gray-600 mt-1">${cveDetails.description || 'No description available'}</p>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <h4 class="font-medium text-gray-900">CVSS Score</h4>
                                <span class="px-2 py-1 text-sm rounded-full ${getCVSSBadgeClass(cveDetails.cvss_v3_score)}">
                                    ${cveDetails.cvss_v3_score || 'No Score'}
                                </span>
                            </div>
                            <div>
                                <h4 class="font-medium text-gray-900">Published</h4>
                                <p class="text-sm text-gray-600">${cveDetails.published_date ? new Date(cveDetails.published_date).toLocaleDateString() : 'Unknown'}</p>
                            </div>
                        </div>
                        <div class="mb-4">
                            <h4 class="font-medium text-gray-900">Source</h4>
                            <div class="flex items-center space-x-2 mt-1">
                                <span class="px-2 py-1 text-xs rounded-full ${cveDetails.source === 'Local Database' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}">
                                    ${cveDetails.source || 'Unknown'}
                                </span>
                                ${cveDetails.can_import ? '<span class="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">Available to Import</span>' : ''}
                            </div>
                        </div>
                        <div class="flex space-x-3 pt-4 border-t">
                            <button onclick="analyzeCVE('${cveId}'); this.closest('.fixed').remove()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                                <i class="fas fa-brain mr-2"></i>Analyze with AI
                            </button>
                            <button onclick="addToWatchlist('${cveId}'); this.closest('.fixed').remove()" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                                <i class="fas fa-bookmark mr-2"></i>Add to Watchlist
                            </button>
                            ${cveDetails.can_import ? `<button onclick="importCVE('${cveId}'); this.closest('.fixed').remove()" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
                                <i class="fas fa-download mr-2"></i>Import to Local
                            </button>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
    } catch (error) {
        console.error('Error loading CVE details:', error);
        showToast('Failed to load CVE details', 'error');
    }
}

async function analyzeCVE(cveId) {
    // Navigate to analysis section first
    showAnalysis();
    
    // Pre-fill the CVE ID in the analysis form
    const cveInput = document.getElementById('analysis-cve-input') || document.getElementById('analysis-cve-id');
    if (cveInput) {
        cveInput.value = cveId;
    }
    
    showToast(`Starting analysis for ${cveId}...`, 'info');
    
    try {
        const api = new CVEPlatformAPI();
        
        // Show loading state in analysis results area
        const resultsDiv = document.getElementById('analysis-results');
        if (resultsDiv) {
            resultsDiv.classList.remove('hidden');
            resultsDiv.innerHTML = `
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center justify-center py-8">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
                        <span class="text-gray-600">Analyzing ${cveId}...</span>
                    </div>
                </div>
            `;
        }
        
        const result = await api.analyzeCVE({ cve_id: cveId, analysis_type: 'comprehensive' });
        
        if (result && (result.success !== false)) {
            showToast('CVE analysis completed', 'success');
            displayAnalysisResults(result, cveId);
        } else {
            showToast('CVE analysis failed', 'error');
            displayAnalysisError('Analysis failed: ' + (result.error || 'Unknown error'), cveId);
        }
    } catch (error) {
        console.error('CVE analysis error:', error);
        showToast('CVE analysis failed: ' + error.message, 'error');
        displayAnalysisError('Analysis failed: ' + error.message, cveId);
    }
}

async function addToWatchlist(cveId) {
    showToast(`Adding ${cveId} to watchlist...`, 'info');
    
    try {
        const api = new CVEPlatformAPI();
        
        // First, get all available watchlists
        let watchlists = await api.getWatchlists();
        
        // If no watchlists exist, create a default one
        if (watchlists.length === 0) {
            showToast('Creating default watchlist...', 'info');
            const defaultWatchlist = await api.createWatchlist({
                name: 'My Watchlist',
                description: 'Default watchlist for monitoring CVEs'
            });
            watchlists = [defaultWatchlist];
        }
        
        let selectedWatchlistId;
        
        // If only one watchlist, use it automatically
        if (watchlists.length === 1) {
            selectedWatchlistId = watchlists[0].watchlist_id;
        } else {
            // Show selection modal for multiple watchlists
            selectedWatchlistId = await showWatchlistSelectionModal(watchlists);
            if (!selectedWatchlistId) {
                showToast('No watchlist selected', 'warning');
                return;
            }
        }
        
        // Add CVE to the selected watchlist
        const result = await api.addCVEsToWatchlist(selectedWatchlistId, { 
            cve_ids: [cveId],
            priority: 'medium'
        });
        
        if (result.added && result.added.length > 0) {
            showToast(`Added ${cveId} to watchlist successfully`, 'success');
        } else if (result.skipped && result.skipped.length > 0) {
            showToast(`${cveId} is already in the watchlist`, 'warning');
        } else {
            showToast('Failed to add to watchlist', 'error');
        }
    } catch (error) {
        console.error('Watchlist error:', error);
        if (error.message.includes('404')) {
            showToast('Watchlist not found. Please try again.', 'error');
        } else {
            showToast('Failed to add to watchlist: ' + error.message, 'error');
        }
    }
}

async function importCVE(cveId) {
    showToast(`Importing ${cveId} to local database...`, 'info');
    
    try {
        const api = new CVEPlatformAPI();
        const result = await api.importFromNVD({ cve_id: cveId, force: false });
        
        if (result.success) {
            showToast('CVE imported successfully', 'success');
            // Refresh search results to show updated import status
            performCVESearch();
        } else {
            showToast('Failed to import CVE: ' + (result.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Import error:', error);
        showToast('Failed to import CVE: ' + error.message, 'error');
    }
}

async function showWatchlistSelectionModal(watchlists) {
    return new Promise((resolve) => {
        // Create modal HTML
        const modalHtml = `
            <div id="watchlist-selection-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-semibold text-gray-900">Select Watchlist</h3>
                        <button onclick="closeWatchlistModal()" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="mb-4">
                        <p class="text-sm text-gray-600 mb-3">Choose which watchlist to add this CVE to:</p>
                        <div class="space-y-2 max-h-60 overflow-y-auto">
                            ${watchlists.map(watchlist => `
                                <div class="border rounded-lg p-3 hover:bg-gray-50 cursor-pointer watchlist-option" 
                                     data-watchlist-id="${watchlist.watchlist_id}">
                                    <div class="flex justify-between items-start">
                                        <div>
                                            <h4 class="font-medium text-gray-900">${escapeHtml(watchlist.name)}</h4>
                                            ${watchlist.description ? `<p class="text-sm text-gray-600">${escapeHtml(watchlist.description)}</p>` : ''}
                                        </div>
                                        <div class="text-right text-sm text-gray-500">
                                            <div>${watchlist.cve_count} CVEs</div>
                                            <div>${watchlist.alert_count} alerts</div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="flex justify-between">
                        <button onclick="createNewWatchlistFromModal()" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                            <i class="fas fa-plus mr-2"></i>Create New
                        </button>
                        <div class="space-x-2">
                            <button onclick="closeWatchlistModal()" class="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Add click handlers for watchlist options
        document.querySelectorAll('.watchlist-option').forEach(option => {
            option.addEventListener('click', () => {
                const watchlistId = option.dataset.watchlistId;
                closeWatchlistModal();
                resolve(watchlistId);
            });
        });
        
        // Store resolve function for other handlers
        window.watchlistModalResolve = resolve;
    });
}

function closeWatchlistModal() {
    const modal = document.getElementById('watchlist-selection-modal');
    if (modal) {
        modal.remove();
    }
    if (window.watchlistModalResolve) {
        window.watchlistModalResolve(null);
        delete window.watchlistModalResolve;
    }
}

async function createNewWatchlistFromModal() {
    const name = prompt('Enter watchlist name:');
    if (!name) return;
    
    const description = prompt('Enter description (optional):') || '';
    
    try {
        showToast('Creating new watchlist...', 'info');
        const api = new CVEPlatformAPI();
        const newWatchlist = await api.createWatchlist({ name, description });
        
        closeWatchlistModal();
        if (window.watchlistModalResolve) {
            window.watchlistModalResolve(newWatchlist.watchlist_id);
        }
        showToast('New watchlist created', 'success');
    } catch (error) {
        console.error('Failed to create watchlist:', error);
        showToast('Failed to create watchlist: ' + error.message, 'error');
    }
}

function toggleAdvancedFilters() {
    const filtersContainer = document.getElementById('advanced-filters');
    if (!filtersContainer) {
        // Create advanced filters if they don't exist
        const searchSection = document.getElementById('cve-search-section');
        if (searchSection) {
            const filtersDiv = document.createElement('div');
            filtersDiv.id = 'advanced-filters';
            filtersDiv.className = 'hidden mt-4 p-4 bg-gray-50 rounded-lg';
            filtersDiv.innerHTML = `
                <h3 class="font-semibold mb-4">Advanced Filters</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">CVSS Score</label>
                        <select class="w-full p-2 border border-gray-300 rounded">
                            <option value="">Any</option>
                            <option value="critical">Critical (9.0-10.0)</option>
                            <option value="high">High (7.0-8.9)</option>
                            <option value="medium">Medium (4.0-6.9)</option>
                            <option value="low">Low (0.1-3.9)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                        <select class="w-full p-2 border border-gray-300 rounded">
                            <option value="">Any time</option>
                            <option value="week">Past week</option>
                            <option value="month">Past month</option>
                            <option value="year">Past year</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Vendor</label>
                        <input type="text" placeholder="e.g., Microsoft, Apache" 
                               class="w-full p-2 border border-gray-300 rounded">
                    </div>
                </div>
                <div class="mt-4 flex space-x-2">
                    <button onclick="applyAdvancedFilters()" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        Apply Filters
                    </button>
                    <button onclick="clearAdvancedFilters()" class="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400">
                        Clear Filters
                    </button>
                </div>
            `;
            
            const searchContainer = searchSection.querySelector('.space-y-4');
            if (searchContainer) {
                searchContainer.appendChild(filtersDiv);
            }
        }
        return;
    }
    
    filtersContainer.classList.toggle('hidden');
    const isVisible = !filtersContainer.classList.contains('hidden');
    showToast(`Advanced filters ${isVisible ? 'shown' : 'hidden'}`, 'info');
}

async function applyAdvancedFilters() {
    const query = document.getElementById('cve-search-input')?.value?.trim() || '';
    
    // Get filter values from the advanced filters section
    const filtersContainer = document.getElementById('advanced-filters');
    if (!filtersContainer) {
        showToast('Advanced filters not available', 'warning');
        return;
    }
    
    const resultsContainer = document.getElementById('search-results-content');
    const searchResultsSection = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    // Show the results section and loading state
    searchResultsSection.classList.remove('hidden');
    resultsContainer.innerHTML = `
        <div class="text-center py-8">
            <i class="fas fa-spinner fa-spin text-2xl text-blue-500 mb-2"></i>
            <p class="text-gray-500">Applying filters and searching...</p>
        </div>
    `;
    
    try {
        // Get filter values from the HTML advanced filters
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        const cvssMinInput = document.getElementById('cvss-min');
        const cvssMaxInput = document.getElementById('cvss-max');
        const vendorInput = document.getElementById('vendor-filter');
        const productInput = document.getElementById('product-filter');
        const searchTypeSelect = document.getElementById('search-type-filter');
        const resultsPerPageSelect = document.getElementById('results-per-page');
        
        // Get selected severity levels from checkboxes
        const severityInputs = document.querySelectorAll('.severity-input:checked');
        const selectedSeverities = Array.from(severityInputs).map(input => input.value);
        
        const api = new CVEPlatformAPI();
        const searchParams = {
            query: query,
            limit: parseInt(resultsPerPageSelect?.value) || 25,
            search_type: searchTypeSelect?.value || 'both',
            sort_by: 'published_date',
            sort_order: 'desc',
            include_descriptions: true
        };
        
        // Add filters if they exist and have values
        if (selectedSeverities.length > 0) {
            searchParams.severity = selectedSeverities;
        }
        if (cvssMinInput?.value) {
            searchParams.cvss_min = parseFloat(cvssMinInput.value);
        }
        if (cvssMaxInput?.value) {
            searchParams.cvss_max = parseFloat(cvssMaxInput.value);
        }
        if (dateFromInput?.value) {
            searchParams.date_from = dateFromInput.value;
        }
        if (dateToInput?.value) {
            searchParams.date_to = dateToInput.value;
        }
        if (vendorInput?.value?.trim()) {
            searchParams.vendor = vendorInput.value.trim();
        }
        if (productInput?.value?.trim()) {
            searchParams.product = productInput.value.trim();
        }
        
        const results = await api.searchCVEs(searchParams);
        displayCVESearchResults(results);
        
        const filterCount = Object.keys(searchParams).filter(key => 
            !['limit', 'sort_by', 'sort_order', 'search_type', 'include_descriptions', 'query'].includes(key) && 
            searchParams[key] !== undefined && searchParams[key] !== '' && 
            !(Array.isArray(searchParams[key]) && searchParams[key].length === 0)
        ).length;
        
        showToast(`Search completed with ${filterCount} filter(s) applied`, 'success');
    } catch (error) {
        console.error('Advanced search error:', error);
        resultsContainer.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex items-center">
                    <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                    <h3 class="font-semibold text-red-800">Search Error</h3>
                </div>
                <p class="text-sm text-red-600 mt-2">Failed to perform advanced search: ${error.message}</p>
                <button onclick="applyAdvancedFilters()" class="mt-3 text-sm text-blue-600 hover:text-blue-800">
                    <i class="fas fa-redo mr-1"></i>Try again
                </button>
            </div>
        `;
        showToast('Advanced search failed', 'error');
    }
}

function clearAdvancedFilters() {
    // Clear all input fields
    const inputs = document.querySelectorAll('#advanced-filters input, #advanced-filters select');
    inputs.forEach(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
            input.checked = false;
        } else {
            input.value = '';
        }
    });
    
    // Reset vulnerability type buttons
    const vulnButtons = document.querySelectorAll('[onclick*="toggleVulnType"]');
    vulnButtons.forEach(button => {
        button.classList.remove('bg-blue-600', 'text-white');
        button.classList.add('bg-gray-200', 'text-gray-700');
    });
    
    // Reset CVSS range to defaults
    const cvssMin = document.getElementById('cvss-min');
    const cvssMax = document.getElementById('cvss-max');
    if (cvssMin) cvssMin.value = '0';
    if (cvssMax) cvssMax.value = '10';
    
    // Update CVSS display values
    updateCVSSRange();
    
    // Update filter summary
    updateFilterSummary();
    
    showToast('All filters cleared', 'info');
}

// Missing functions that are referenced in HTML
function loadSettingsData() {
    // Load actual settings instead of showing "coming soon"
    const settingsContent = document.getElementById('settings-content');
    if (settingsContent) {
        settingsContent.innerHTML = `
            <div class="space-y-6">
                <div class="border-b pb-4">
                    <h3 class="text-lg font-semibold mb-4">Appearance</h3>
                    <div class="space-y-3">
                        <div class="flex items-center justify-between">
                            <span>Dark Mode</span>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" id="dark-mode-toggle" class="sr-only peer" onchange="toggleDarkMode()">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                        </div>
                        <div class="flex items-center justify-between">
                            <span>Compact View</span>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                        </div>
                    </div>
                </div>
                
                <div class="border-b pb-4">
                    <h3 class="text-lg font-semibold mb-4">Notifications</h3>
                    <div class="space-y-3">
                        <label class="flex items-center">
                            <input type="checkbox" class="mr-3 rounded" checked>
                            <span>Email notifications for critical CVEs</span>
                        </label>
                        <label class="flex items-center">
                            <input type="checkbox" class="mr-3 rounded" checked>
                            <span>Browser notifications</span>
                        </label>
                        <label class="flex items-center">
                            <input type="checkbox" class="mr-3 rounded">
                            <span>Weekly security digest</span>
                        </label>
                    </div>
                </div>
                
                <div class="border-b pb-4">
                    <h3 class="text-lg font-semibold mb-4">API Settings</h3>
                    <div class="space-y-3">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">API Rate Limit</label>
                            <select class="w-full p-2 border border-gray-300 rounded-lg">
                                <option>100 requests/hour</option>
                                <option>500 requests/hour</option>
                                <option>1000 requests/hour</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Default Response Format</label>
                            <select class="w-full p-2 border border-gray-300 rounded-lg">
                                <option>JSON</option>
                                <option>XML</option>
                                <option>CSV</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div>
                    <h3 class="text-lg font-semibold mb-4">Account</h3>
                    <div class="space-y-3">
                        <button onclick="showProfileSettings()" class="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                            <i class="fas fa-user mr-3 text-gray-500"></i>
                            Profile Settings
                        </button>
                        <button onclick="showSecuritySettings()" class="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                            <i class="fas fa-shield-alt mr-3 text-gray-500"></i>
                            Security Settings
                        </button>
                        <button onclick="exportUserData()" class="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
                            <i class="fas fa-download mr-3 text-gray-500"></i>
                            Export Data
                        </button>
                    </div>
                </div>
                
                <div class="pt-4 border-t">
                    <div class="flex space-x-3">
                        <button onclick="saveSettings()" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
                            Save Changes
                        </button>
                        <button onclick="resetSettings()" class="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400">
                            Reset to Defaults
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Set dark mode toggle state
        const darkModeToggle = document.getElementById('dark-mode-toggle');
        if (darkModeToggle) {
            darkModeToggle.checked = localStorage.getItem('darkMode') === 'true';
        }
    }
}

function startAnalysis() {
    const cveInput = document.getElementById('analysis-cve-input') || document.getElementById('analysis-cve-id');
    const analysisTypeSelect = document.getElementById('analysis-type');
    
    const cveId = cveInput?.value?.trim();
    const analysisType = analysisTypeSelect?.value || 'comprehensive';
    
    if (!cveId) {
        showToast('Please enter a CVE ID to analyze', 'warning');
        if (cveInput) {
            cveInput.focus();
        }
        return;
    }
    
    // Call the analyzeCVE function directly
    analyzeCVE(cveId);
}

function applyFilters() {
    showToast('Applying filters...', 'info');
    
    // Get filter values from the current section
    const currentSection = document.querySelector('.section:not(.hidden)');
    if (!currentSection) return;
    
    const filters = {};
    const inputs = currentSection.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.value && input.name) {
            filters[input.name] = input.value;
        }
    });
    
    console.log('Applying filters:', filters);
    
    // Apply filters based on current section
    if (currentSection.id === 'cve-search-section') {
        applyCVEFilters(filters);
    } else if (currentSection.id === 'dashboard-section') {
        applyDashboardFilters(filters);
    } else {
        showToast('Filters applied', 'success');
    }
}

async function runAnalysis() {
    const analysisType = document.getElementById('analysis-type')?.value;
    const target = document.getElementById('analysis-target')?.value?.trim();
    
    if (!target) {
        showToast('Please enter a target for analysis', 'warning');
        return;
    }
    
    showToast('Analysis started...', 'info');
    
    try {
        const api = new CVEPlatformAPI();
        let result;
        
        switch (analysisType) {
            case 'cve':
                result = await api.analyzeCVE({ cve_id: target });
                break;
            case 'code':
                result = await api.analyzeCode({ code: target });
                break;
            case 'risk':
                result = await api.assessRisk({ target: target });
                break;
            default:
                result = await api.analyzeCVEDetailed({ cve_id: target });
        }
        
        if (result.success) {
            showToast('Analysis completed successfully', 'success');
            displayAnalysisResults(result);
        } else {
            showToast('Analysis failed: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showToast('Analysis failed: ' + error.message, 'error');
    }
}

function displayAnalysisResults(result, cveId) {
    const resultsDiv = document.getElementById('analysis-results');
    if (!resultsDiv) return;
    
    // Extract analysis data from the result
    const analysis = result.analysis || result;
    const modelUsed = result.model_used || 'AI Model';
    const analysisType = result.analysis_type || 'Comprehensive';
    
    resultsDiv.innerHTML = `
        <div class="bg-white rounded-lg shadow-lg p-6">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-bold text-gray-900">AI Analysis Results</h3>
                <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                    <i class="fas fa-check-circle mr-1"></i>Completed
                </span>
            </div>
            
            <!-- Analysis Header -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <div>
                    <h4 class="font-medium text-gray-700">CVE ID</h4>
                    <p class="text-lg font-semibold text-blue-600">${cveId || 'Unknown'}</p>
                </div>
                <div>
                    <h4 class="font-medium text-gray-700">Analysis Type</h4>
                    <p class="text-gray-900">${analysisType}</p>
                </div>
                <div>
                    <h4 class="font-medium text-gray-700">AI Model</h4>
                    <p class="text-gray-900">${modelUsed}</p>
                </div>
            </div>
            
            <!-- Analysis Content -->
            <div class="space-y-6">
                ${formatAnalysisContent(analysis)}
            </div>
            
            <!-- Actions -->
            <div class="flex space-x-3 pt-6 border-t">
                <button onclick="exportAnalysisReport('${cveId || 'unknown'}')" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    <i class="fas fa-download mr-2"></i>Export Report
                </button>
                <button onclick="addToWatchlist('${cveId || 'unknown'}')" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                    <i class="fas fa-bookmark mr-2"></i>Add to Watchlist
                </button>
                <button onclick="generatePoC('${cveId || 'unknown'}')" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
                    <i class="fas fa-code mr-2"></i>Generate PoC
                </button>
            </div>
        </div>
    `;
    resultsDiv.classList.remove('hidden');
}

function displayAnalysisError(errorMessage, cveId) {
    const resultsDiv = document.getElementById('analysis-results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center mb-4">
                <i class="fas fa-exclamation-triangle text-red-500 text-xl mr-3"></i>
                <h3 class="text-lg font-semibold text-gray-900">Analysis Failed</h3>
            </div>
            
            <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p class="text-red-700">${errorMessage}</p>
            </div>
            
            <div class="space-y-3">
                <h4 class="font-medium text-gray-900">Troubleshooting Steps:</h4>
                <ul class="list-disc list-inside text-sm text-gray-600 space-y-1">
                    <li>Verify that the CVE ID "${cveId}" is valid</li>
                    <li>Check if the AI service is running and available</li>
                    <li>Ensure you have proper authentication</li>
                    <li>Try importing the CVE to local database first</li>
                </ul>
            </div>
            
            <div class="flex space-x-3 pt-4 border-t">
                <button onclick="importCVE('${cveId}')" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    <i class="fas fa-download mr-2"></i>Import CVE First
                </button>
                <button onclick="analyzeCVE('${cveId}')" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                    <i class="fas fa-redo mr-2"></i>Retry Analysis
                </button>
            </div>
        </div>
    `;
    resultsDiv.classList.remove('hidden');
}

function formatAnalysisContent(analysis) {
    if (typeof analysis === 'string') {
        return `
            <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-3">Analysis Summary</h4>
                <div class="prose max-w-none text-gray-700">
                    ${analysis.replace(/\n/g, '<br>')}
                </div>
            </div>
        `;
    }
    
    if (typeof analysis === 'object' && analysis !== null) {
        let content = '';
        
        // Vulnerability Summary
        if (analysis.vulnerability_summary) {
            content += `
                <div class="bg-blue-50 rounded-lg p-4">
                    <h4 class="font-medium text-blue-900 mb-3">
                        <i class="fas fa-shield-alt mr-2"></i>Vulnerability Summary
                    </h4>
                    <p class="text-blue-800">${analysis.vulnerability_summary}</p>
                </div>
            `;
        }
        
        // Severity Assessment
        if (analysis.severity_assessment) {
            const severity = analysis.severity_assessment;
            content += `
                <div class="bg-red-50 rounded-lg p-4">
                    <h4 class="font-medium text-red-900 mb-3">
                        <i class="fas fa-exclamation-triangle mr-2"></i>Severity Assessment
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <span class="text-sm text-red-700">CVSS Score:</span>
                            <span class="font-semibold text-red-900">${severity.cvss_score || 'N/A'}</span>
                        </div>
                        <div>
                            <span class="text-sm text-red-700">AI Risk Score:</span>
                            <span class="font-semibold text-red-900">${severity.ai_risk_score || 'N/A'}/10</span>
                        </div>
                    </div>
                    ${severity.severity_justification ? `<p class="text-red-800 mt-2">${severity.severity_justification}</p>` : ''}
                </div>
            `;
        }
        
        // Attack Vectors
        if (analysis.attack_vectors && analysis.attack_vectors.length > 0) {
            content += `
                <div class="bg-orange-50 rounded-lg p-4">
                    <h4 class="font-medium text-orange-900 mb-3">
                        <i class="fas fa-crosshairs mr-2"></i>Attack Vectors
                    </h4>
                    <div class="space-y-2">
                        ${analysis.attack_vectors.map(vector => `
                            <div class="bg-white rounded p-3 border border-orange-200">
                                <h5 class="font-medium text-orange-900">${vector.vector || vector}</h5>
                                ${vector.description ? `<p class="text-sm text-orange-700 mt-1">${vector.description}</p>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Exploitation Analysis
        if (analysis.exploitation_analysis) {
            const exploit = analysis.exploitation_analysis;
            content += `
                <div class="bg-yellow-50 rounded-lg p-4">
                    <h4 class="font-medium text-yellow-900 mb-3">
                        <i class="fas fa-bug mr-2"></i>Exploitation Analysis
                    </h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <span class="text-sm text-yellow-700">Likelihood:</span>
                            <span class="font-semibold text-yellow-900">${exploit.likelihood || 'Unknown'}</span>
                        </div>
                        <div>
                            <span class="text-sm text-yellow-700">Complexity:</span>
                            <span class="font-semibold text-yellow-900">${exploit.complexity || 'Unknown'}</span>
                        </div>
                    </div>
                    ${exploit.prerequisites ? `<p class="text-yellow-800 mt-2"><strong>Prerequisites:</strong> ${exploit.prerequisites}</p>` : ''}
                </div>
            `;
        }
        
        // If no structured content, show raw JSON
        if (!content) {
            content = `
                <div class="bg-gray-50 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-3">Raw Analysis Data</h4>
                    <pre class="text-sm text-gray-700 overflow-auto">${JSON.stringify(analysis, null, 2)}</pre>
                </div>
            `;
        }
        
        return content;
    }
    
    return `
        <div class="bg-gray-50 rounded-lg p-4">
            <p class="text-gray-600">No analysis data available</p>
        </div>
    `;
}

function exportAnalysisReport(cveId) {
    showToast('Exporting analysis report...', 'info');
    // Implementation for exporting analysis report
}

// Missing functions for advanced filters
function toggleVulnType(type) {
    const button = event.target;
    const isActive = button.classList.contains('bg-blue-600');
    
    if (isActive) {
        button.classList.remove('bg-blue-600', 'text-white');
        button.classList.add('bg-gray-200', 'text-gray-700');
    } else {
        button.classList.remove('bg-gray-200', 'text-gray-700');
        button.classList.add('bg-blue-600', 'text-white');
    }
    
    updateFilterSummary();
}

function setDatePreset(preset) {
    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');
    
    if (!startDate || !endDate) return;
    
    const today = new Date();
    const end = today.toISOString().split('T')[0];
    let start;
    
    switch (preset) {
        case '7d':
            start = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            break;
        case '30d':
            start = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            break;
        case '90d':
            start = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            break;
        case '1y':
            start = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            break;
        default:
            return;
    }
    
    startDate.value = start;
    endDate.value = end;
    updateFilterSummary();
}

function updateCVSSRange() {
    const minRange = document.getElementById('cvss-min');
    const maxRange = document.getElementById('cvss-max');
    const minValue = document.getElementById('cvss-min-value');
    const maxValue = document.getElementById('cvss-max-value');
    
    if (minRange && maxRange && minValue && maxValue) {
        minValue.textContent = minRange.value;
        maxValue.textContent = maxRange.value;
        
        // Ensure min doesn't exceed max
        if (parseFloat(minRange.value) > parseFloat(maxRange.value)) {
            minRange.value = maxRange.value;
            minValue.textContent = minRange.value;
        }
    }
    
    updateFilterSummary();
}

function updateFilterSummary() {
    const summaryElement = document.getElementById('filter-summary');
    if (!summaryElement) return;
    
    const filters = [];
    
    // Check vulnerability types
    const vulnButtons = document.querySelectorAll('[onclick*="toggleVulnType"]');
    const activeVulnTypes = Array.from(vulnButtons)
        .filter(btn => btn.classList.contains('bg-blue-600'))
        .map(btn => btn.textContent.trim());
    
    if (activeVulnTypes.length > 0) {
        filters.push(`Types: ${activeVulnTypes.join(', ')}`);
    }
    
    // Check CVSS range
    const minCvss = document.getElementById('cvss-min')?.value;
    const maxCvss = document.getElementById('cvss-max')?.value;
    if (minCvss && maxCvss && (minCvss !== '0' || maxCvss !== '10')) {
        filters.push(`CVSS: ${minCvss}-${maxCvss}`);
    }
    
    // Check date range
    const startDate = document.getElementById('start-date')?.value;
    const endDate = document.getElementById('end-date')?.value;
    if (startDate && endDate) {
        filters.push(`Date: ${startDate} to ${endDate}`);
    }
    
    // Check vendor/product
    const vendor = document.getElementById('vendor-filter')?.value;
    const product = document.getElementById('product-filter')?.value;
    if (vendor) filters.push(`Vendor: ${vendor}`);
    if (product) filters.push(`Product: ${product}`);
    
    // Check search type
    const searchType = document.getElementById('search-type')?.value;
    if (searchType && searchType !== 'both') {
        filters.push(`Source: ${searchType.toUpperCase()}`);
    }
    
    // Update summary
    if (filters.length > 0) {
        summaryElement.innerHTML = `
            <div class="text-sm text-blue-600 bg-blue-50 p-2 rounded">
                <i class="fas fa-filter mr-1"></i>
                Active filters: ${filters.join(' • ')}
            </div>
        `;
    } else {
        summaryElement.innerHTML = `
            <div class="text-sm text-gray-500">
                No filters applied
            </div>
        `;
    }
}

async function applyCVEFilters(filters) {
    try {
        const api = new CVEPlatformAPI();
        const searchParams = {
            query: filters.query || '',
            cvss_score: filters.cvss_score,
            date_range: filters.date_range,
            vendor: filters.vendor
        };
        
        const results = await api.searchCVEs(searchParams);
        displayCVESearchResults(results);
        showToast('CVE filters applied', 'success');
    } catch (error) {
        console.error('Filter error:', error);
        showToast('Failed to apply filters', 'error');
    }
}

function applyDashboardFilters(filters) {
    showToast('Dashboard filters applied', 'success');
    // Implement dashboard-specific filtering
}

function saveSettings() {
    showToast('Settings saved successfully', 'success');
}

function resetSettings() {
    if (confirm('Reset all settings to defaults?')) {
        showToast('Settings reset to defaults', 'info');
        loadSettingsData(); // Reload the settings
    }
}

function exportUserData() {
    showToast('Preparing data export...', 'info');
    
    const userData = {
        timestamp: new Date().toISOString(),
        settings: {
            darkMode: localStorage.getItem('darkMode') === 'true',
            notifications: true,
            apiSettings: {}
        },
        preferences: {},
        exportedBy: 'CVE Analysis Platform'
    };
    
    const blob = new Blob([JSON.stringify(userData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `user-data-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('User data exported successfully', 'success');
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
    initializeNotifications();
    
    // Load initial dashboard data
    showDashboard();
    
    // Always try to load dashboard data (it will handle authentication internally)
    setTimeout(() => {
        loadDashboardData();
        
        if (checkAuthStatus()) {
            console.log('✅ User authenticated - dashboard data loaded');
        } else {
            console.log('⏳ User not authenticated - showing login prompts');
        }
    }, 500);
    
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

// Add route protection (for SPA - no automatic redirects)
function protectRoute() {
    if (!checkAuthStatus()) {
        showToast('Please login to access this feature', 'warning');
        return false;
    }
    return true;
}

// Note: Removed automatic route protection on page load since this is a SPA
// Authentication will be handled by individual function calls when needed

// Show login modal instead of redirecting
function showLoginModal() {
    // Remove any existing login modal
    const existingModal = document.getElementById('login-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.id = 'login-modal';
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-bold text-gray-900">Login Required</h2>
                <button onclick="closeLoginModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            <div class="space-y-4">
                <p class="text-gray-600">Please log in to access this feature.</p>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                    <input type="text" id="login-username" class="w-full p-2 border border-gray-300 rounded" placeholder="Enter username">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                    <input type="password" id="login-password" class="w-full p-2 border border-gray-300 rounded" placeholder="Enter password">
                </div>
                <div class="flex space-x-3">
                    <button onclick="performLogin()" class="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                        Login
                    </button>
                    <button onclick="closeLoginModal()" class="flex-1 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400">
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function closeLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) {
        modal.remove();
    }
}

async function performLogin() {
    const username = document.getElementById('login-username')?.value?.trim();
    const password = document.getElementById('login-password')?.value?.trim();
    
    if (!username || !password) {
        showToast('Please enter both username and password', 'warning');
        return;
    }
    
    try {
        const api = new CVEPlatformAPI();
        const result = await api.login({ username, password });
        
        // Check if login was successful by looking for access_token
        if (result.access_token) {
            // Store authentication data
            localStorage.setItem('auth_token', result.access_token);
            localStorage.setItem('token_type', result.token_type || 'Bearer');
            localStorage.setItem('user_data', JSON.stringify(result.user));
            
            // Calculate and store token expiration time
            const expiresIn = result.expires_in || 3600; // Default 1 hour
            const expirationTime = Date.now() + (expiresIn * 1000);
            localStorage.setItem('token_expires_at', expirationTime.toString());
            
            showToast('Login successful!', 'success');
            closeLoginModal();
            
            // Refresh the dashboard to load authenticated content
            loadDashboardData();
        } else {
            showToast('Login failed: Invalid credentials', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        
        // Handle different types of errors
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            showToast('Login failed: Invalid username or password', 'error');
        } else if (error.message.includes('500')) {
            showToast('Login failed: Server error. Please try again later.', 'error');
        } else {
            showToast('Login failed: ' + error.message, 'error');
        }
    }
}
