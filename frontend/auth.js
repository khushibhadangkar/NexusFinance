// auth.js

class AuthManager {
    constructor() {
        this.tokenKey = 'jwt_token'; // ✅ THE CORRECT KEY
        this.user = this.getUserFromToken();
    }

    /**
     * Saves the token to localStorage.
     */
    login(token) {
        localStorage.setItem(this.tokenKey, token);
        this.user = this.getUserFromToken();
    }

    /**
     * Removes the token from localStorage.
     */
    logout() {
        localStorage.removeItem(this.tokenKey);
        this.user = null;
    }

    /**
     * Checks if a token exists.
     */
    isAuthenticated() {
        const token = this.getToken();
        return !!token && !this.isTokenExpired(token);
    }

    /**
     * Gets the token from localStorage.
     */
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    /**
     * Tries to parse the user info from the token payload.
     */
    getUserFromToken() {
        const token = this.getToken();
        if (!token) return null;

        try {
            // A token is in three parts: header.payload.signature
            const payload = JSON.parse(atob(token.split('.')[1]));
            // Check if it's expired
            if (payload.exp && Date.now() >= payload.exp * 1000) {
                this.logout();
                return null;
            }
            return payload; // The payload *is* the user info
        } catch (e) {
            console.error("Error parsing token:", e);
            this.logout(); // The token is malformed
            return null;
        }
    }

    /**
     * Checks if the token is expired.
     */
    isTokenExpired(token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return (payload.exp && Date.now() >= payload.exp * 1000);
        } catch (e) {
            return true;
        }
    }

    /**
     * Gets the current user.
     */
    getUser() {
        return this.user;
    }

    /**
     * Updates the UI with user info.
     */
    updateUI() {
        if (this.user) {
            const userNameElement = document.querySelector('.user-name');
            const userEmailElement = document.querySelector('.user-email');
            const userAvatarElement = document.querySelector('.user-avatar');

            if (userNameElement) userNameElement.textContent = this.user.name || 'User';
            if (userEmailElement) userEmailElement.textContent = this.user.email || '';
            if (userAvatarElement && this.user.name) {
                userAvatarElement.textContent = this.user.name.charAt(0).toUpperCase();
            }
        }
    }
}

// Create a global instance
window.authManager = new AuthManager();