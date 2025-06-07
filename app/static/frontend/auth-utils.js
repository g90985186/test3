// Authentication utilities for CVE Analysis Platform

// Show authentication error message and redirect
function handleAuthError(error) {
    console.warn('Authentication error:', error);
    
    // Clear authentication data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires_at');
    
    // Show error message
    const message = error.message || 'Authentication required';
    showToast(message, 'error');
    
    // Redirect to login page
    window.location.href = '/login';
}

// Check if user is authenticated
function isAuthenticated() {
    const token = localStorage.getItem('auth_token');
    if (!token) return false;
    
    try {
        const tokenExp = localStorage.getItem('token_expires_at');
        if (!tokenExp) return false;
        
        const expirationTime = parseInt(tokenExp);
        return Date.now() < expirationTime;
    } catch (error) {
        console.error('Error checking authentication:', error);
        return false;
    }
}

// Make authenticated API request
async function authenticatedFetch(url, options = {}) {
    if (!isAuthenticated()) {
        handleAuthError(new Error('Authentication required'));
        throw new Error('Authentication required');
    }
    
    const token = localStorage.getItem('auth_token');
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    
    try {
        const response = await fetch(url, { ...options, headers });
        
        if (response.status === 401) {
            handleAuthError(new Error('Session expired. Please login again.'));
            throw new Error('Authentication failed');
        }
        
        if (response.status === 403) {
            handleAuthError(new Error('Access denied. Insufficient permissions.'));
            throw new Error('Access denied');
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response;
    } catch (error) {
        if (error.message === 'Authentication failed' || error.message === 'Access denied') {
            throw error;
        }
        console.error('API request failed:', error);
        throw error;
    }
}

// Export utilities
window.authUtils = {
    handleAuthError,
    isAuthenticated,
    authenticatedFetch
}; 