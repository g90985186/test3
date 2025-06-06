// Authentication Manager for CVE Analysis Platform
// Handles JWT tokens, login/logout, and API authentication

class AuthManager {
    constructor() {
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('user_data') || 'null');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.apiKey = localStorage.getItem('api_key');
        this.initializeAuthState();
    }

    // Initialize authentication state on page load
    initializeAuthState() {
        if (this.isAuthenticated()) {
            this.updateUIForAuthenticatedUser();
        } else {
            this.showLoginModal();
        }
    }

    // Check if user is authenticated
    isAuthenticated() {
        const hasToken = !!this.token;
        const hasUser = !!this.user;
        const tokenExpired = this.isTokenExpired();
        const result = hasToken && hasUser && !tokenExpired;
        console.log(`Auth check: token=${hasToken}, user=${hasUser}, expired=${tokenExpired}, result=${result}`);
        return result;
    }

    // Check if token is expired
    isTokenExpired() {
        if (!this.token) {
            console.log('Token expired check: no token available');
            return true;
        }
        
        // Backend uses simple SHA-256 tokens, not JWT
        // Check if we have stored expiration info
        const tokenExp = localStorage.getItem('token_expires_at');
        if (!tokenExp) {
            console.log('Token expired check: no expiration info, assuming valid');
            return false; // If no expiration info, assume token is valid
        }
        
        try {
            const expirationTime = parseInt(tokenExp);
            const isExpired = Date.now() >= expirationTime;
            console.log(`Token expired check: exp=${new Date(expirationTime)}, now=${new Date()}, expired=${isExpired}`);
            return isExpired;
        } catch (error) {
            console.log('Token expired check: parsing failed', error);
            return false; // If we can't parse expiration, assume token is valid
        }
    }

    // Login with username/password
    async login(username, password) {
        try {
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            
            // Store authentication data
            this.token = data.access_token;
            this.user = data.user;
            
            // Calculate and store token expiration time
            const expirationTime = Date.now() + (data.expires_in * 1000);
            localStorage.setItem('token_expires_at', expirationTime.toString());
            
            localStorage.setItem('auth_token', this.token);
            localStorage.setItem('user_data', JSON.stringify(this.user));

            this.updateUIForAuthenticatedUser();
            this.hideLoginModal();
            
            showToast(`Welcome back, ${this.user.username}!`, 'success');
            
            // Reload dashboard data with small delay to ensure token is properly set
            setTimeout(() => {
                if (typeof loadDashboardData === 'function') {
                    loadDashboardData();
                }
                // Initialize ALL 92+ API endpoints after successful login
                // Just show welcome message - let user navigate to load specific data
                console.log('Login successful - user can now access all features');
                showToast('Login successful! Navigate to different sections to explore features.', 'success');
            }, 500);
            
            return true;
        } catch (error) {
            console.error('Login error:', error);
            showToast(error.message || 'Login failed', 'error');
            return false;
        }
    }

    // Logout user
    async logout() {
        try {
            // Call logout endpoint if available
            if (this.token) {
                await fetch('/api/v1/auth/logout', {
                    method: 'POST',
                    headers: this.getAuthHeaders()
                }).catch(() => {}); // Don't fail if endpoint doesn't exist
            }
        } catch (error) {
            console.warn('Logout endpoint error:', error);
        }

        // Clear local storage
        this.token = null;
        this.user = null;
        this.refreshToken = null;
        this.apiKey = null;
        
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('api_key');
        localStorage.removeItem('token_expires_at');

        this.updateUIForUnauthenticatedUser();
        this.showLoginModal();
        
        showToast('Successfully logged out', 'info');
    }

    // Get authentication headers for API requests
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
            console.log(`Auth headers: Bearer token added (length: ${this.token.length})`);
        } else if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
            console.log(`Auth headers: API key added`);
        } else {
            console.log(`Auth headers: No authentication token available`);
        }

        return headers;
    }

    // Handle authentication errors
    handleAuthError(error) {
        console.warn('Authentication error:', error);
        
        // Clear invalid tokens
        this.token = null;
        this.user = null;
        this.refreshToken = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token_expires_at');
        
        // Show error message
        const message = error.message || 'Authentication required';
        showToast(message, 'error');
        
        // Show login modal
        this.showLoginModal();
        
        // Update UI for unauthenticated state
        this.updateUIForUnauthenticatedUser();
    }

    // Make authenticated API request
    async authenticatedFetch(url, options = {}) {
        // Check authentication before making request
        if (!this.isAuthenticated()) {
            this.handleAuthError(new Error('Authentication required'));
            throw new Error('Authentication required');
        }

        // Add auth headers
        const authOptions = {
            ...options,
            headers: {
                ...this.getAuthHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, authOptions);
            
            // Handle authentication errors
            if (response.status === 401) {
                this.handleAuthError(new Error('Session expired. Please login again.'));
                throw new Error('Authentication failed');
            }
            
            if (response.status === 403) {
                this.handleAuthError(new Error('Access denied. Insufficient permissions.'));
                throw new Error('Access denied');
            }

            return response;
        } catch (error) {
            if (error.message === 'Authentication failed' || error.message === 'Access denied') {
                throw error;
            }
            // Handle other errors
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Update UI for authenticated user
    updateUIForAuthenticatedUser() {
        // Update navigation
        const userSection = document.getElementById('user-section');
        if (userSection) {
            userSection.innerHTML = `
                <div class="flex items-center space-x-3">
                    <div class="text-sm">
                        <div class="text-white font-medium">${this.user.username}</div>
                        <div class="text-blue-200 text-xs">${this.user.role}</div>
                    </div>
                    <button onclick="authManager.logout()" class="text-white hover:text-gray-200" title="Logout">
                        <i class="fas fa-sign-out-alt"></i>
                    </button>
                </div>
            `;
        }

        // Show main content
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.style.display = 'block';
        }

        // Enable navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
        });
    }

    // Update UI for unauthenticated user
    updateUIForUnauthenticatedUser() {
        // Update navigation
        const userSection = document.getElementById('user-section');
        if (userSection) {
            userSection.innerHTML = `
                <button onclick="authManager.showLoginModal()" class="text-white hover:text-gray-200">
                    <i class="fas fa-sign-in-alt mr-2"></i>Login
                </button>
            `;
        }

        // Hide main content
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.style.display = 'none';
        }

        // Disable navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.disabled = true;
            btn.classList.add('opacity-50', 'cursor-not-allowed');
        });
    }

    // Show login modal
    showLoginModal() {
        // Remove existing modal if any
        const existingModal = document.getElementById('login-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create login modal
        const modal = document.createElement('div');
        modal.id = 'login-modal';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center';
        modal.innerHTML = `
            <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
                <div class="p-6">
                    <div class="text-center mb-6">
                        <i class="fas fa-shield-alt text-blue-600 text-4xl mb-4"></i>
                        <h3 class="text-lg font-semibold text-gray-900">CVE Analysis Platform</h3>
                        <p class="text-gray-600">Please sign in to continue</p>
                    </div>
                    
                    <form id="login-form" onsubmit="return authManager.handleLoginSubmit(event)">
                        <div class="mb-4">
                            <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                                Username
                            </label>
                            <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500"
                                   id="username" type="text" placeholder="Username" required>
                        </div>
                        
                        <div class="mb-6">
                            <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                                Password
                            </label>
                            <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline focus:border-blue-500"
                                   id="password" type="password" placeholder="Password" required>
                        </div>
                        
                        <div class="flex items-center justify-between">
                            <button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
                                    type="submit" id="login-btn">
                                Sign In
                            </button>
                        </div>
                    </form>
                    
                    <div class="mt-4 text-center">
                        <div class="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                            <strong>Demo Credentials:</strong><br>
                            Username: <code>admin</code><br>
                            Password: <code>admin123</code>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Focus on username field
        setTimeout(() => {
            document.getElementById('username').focus();
        }, 100);
    }

    // Hide login modal
    hideLoginModal() {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.remove();
        }
    }

    // Handle login form submission
    async handleLoginSubmit(event) {
        event.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const loginBtn = document.getElementById('login-btn');
        
        // Show loading state
        loginBtn.disabled = true;
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Signing in...';
        
        try {
            const success = await this.login(username, password);
            if (!success) {
                // Reset button state on failure
                loginBtn.disabled = false;
                loginBtn.innerHTML = 'Sign In';
            }
        } catch (error) {
            console.error('Login error:', error);
            loginBtn.disabled = false;
            loginBtn.innerHTML = 'Sign In';
        }
        
        return false;
    }

    // Get current user info
    getCurrentUser() {
        return this.user;
    }

    // Check if user has admin role
    isAdmin() {
        return this.user && this.user.role === 'admin';
    }

    // Set API key for programmatic access
    setApiKey(apiKey) {
        this.apiKey = apiKey;
        localStorage.setItem('api_key', apiKey);
    }
}

// Initialize authentication manager
const authManager = new AuthManager();

// Override the global fetch for authenticated requests
const originalFetch = window.fetch;
window.authenticatedFetch = function(url, options = {}) {
    return authManager.authenticatedFetch(url, options);
};

// Export for use in other scripts
window.authManager = authManager;
