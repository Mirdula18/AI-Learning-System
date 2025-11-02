/**
 * Authentication utilities
 */

class AuthManager {
    constructor() {
        this.token = localStorage.getItem('token');
        this.userId = localStorage.getItem('user_id');
    }

    isAuthenticated() {
        return !!this.token;
    }

    getToken() {
        return this.token;
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    setUserId(userId) {
        this.userId = userId;
        localStorage.setItem('user_id', userId);
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        this.token = null;
        this.userId = null;
        window.location.href = '/login/';
    }

    async makeRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (this.token) {
            defaultOptions.headers['Authorization'] = `Token ${this.token}`;
        }

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, mergedOptions);

            if (response.status === 401) {
                this.logout();
                return null;
            }

            return response;
        } catch (error) {
            console.error('Request error:', error);
            throw error;
        }
    }
}

// Create global instance
const authManager = new AuthManager();

// Check authentication on page load
function checkAuthentication(requireAuth = true) {
    if (requireAuth && !authManager.isAuthenticated()) {
        window.location.href = '/login/';
        return false;
    }
    return true;
}
