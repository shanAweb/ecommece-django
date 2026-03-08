/**
 * Authentication utility for managing user sessions and JWT tokens
 */

// Token management - Check if Auth already exists to avoid duplicate declaration
if (typeof window.Auth === 'undefined') {
    window.Auth = {
    // Get access token from localStorage
    getAccessToken: function() {
        return localStorage.getItem('access_token');
    },
    
    // Get refresh token from localStorage
    getRefreshToken: function() {
        return localStorage.getItem('refresh_token');
    },
    
    // Store tokens
    setTokens: function(accessToken, refreshToken, skipUIUpdate = false) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        if (!skipUIUpdate) {
            this.updateUI();
        }
    },
    
    // Clear tokens (logout)
    clearTokens: function() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        this.updateUI();
    },
    
    // Check if user is authenticated
    isAuthenticated: function() {
        return !!this.getAccessToken();
    },
    
    // Get authenticated fetch headers
    getAuthHeaders: function() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        const token = this.getAccessToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    },
    
    // Make authenticated fetch request
    fetch: async function(url, options = {}) {
        const headers = this.getAuthHeaders();
        const mergedOptions = {
            ...options,
            headers: {
                ...headers,
                ...(options.headers || {})
            }
        };
        
        let response = await window.fetch(url, mergedOptions);
        
        // If 401, try to refresh token
        if (response.status === 401 && this.getRefreshToken()) {
            const refreshed = await this.refreshToken();
            if (refreshed) {
                // Retry original request with new token
                mergedOptions.headers['Authorization'] = `Bearer ${this.getAccessToken()}`;
                response = await window.fetch(url, mergedOptions);
            }
        }
        
        return response;
    },
    
    // Refresh access token
    refreshToken: async function() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;
        
        try {
            const response = await window.fetch('/api/users/token/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access, refreshToken);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }
        
        // Refresh failed, clear tokens
        this.clearTokens();
        return false;
    },
    
    // Get user profile data
    getUserData: async function() {
        if (!this.isAuthenticated()) return null;
        
        try {
            const response = await this.fetch('/api/users/profile/');
            if (response.ok) {
                const userData = await response.json();
                localStorage.setItem('user_data', JSON.stringify(userData));
                
                // Update navbar avatar after fetching user data
                const navbarAvatarContainer = document.getElementById('navbarAvatarContainer');
                if (navbarAvatarContainer && userData.avatar) {
                    navbarAvatarContainer.style.border = '2px solid #e74c3c';
                    navbarAvatarContainer.innerHTML = `<img src="${userData.avatar}" alt="Profile" style="width: 100%; height: 100%; object-fit: cover;">`;
                }
                
                return userData;
            }
        } catch (error) {
            console.error('Failed to get user data:', error);
        }
        
        return null;
    },
    
    // Update UI based on auth state
    updateUI: function() {
        const isAuth = this.isAuthenticated();
        const userMenu = document.getElementById('userMenuDropdown');
        const ordersNavItem = document.getElementById('ordersNavItem');
        const navbarAvatarContainer = document.getElementById('navbarAvatarContainer');
        
        if (isAuth) {
            // Update menu to show user options
            const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
            const userName = userData.first_name || userData.email || 'User';
            
            if (userMenu) {
                userMenu.innerHTML = `
                    <li><a class="dropdown-item" href="/account/"><i class="bi bi-person me-2"></i>My Account</a></li>
                    <li><a class="dropdown-item" href="/orders/"><i class="bi bi-bag-check me-2"></i>My Orders</a></li>
                    <li><a class="dropdown-item" href="/wishlist/"><i class="bi bi-heart me-2"></i>Wishlist</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" onclick="Auth.logout(); return false;"><i class="bi bi-box-arrow-right me-2"></i>Logout</a></li>
                `;
            }
            
            // Update navbar avatar
            if (navbarAvatarContainer && userData.avatar) {
                navbarAvatarContainer.style.border = '2px solid #e74c3c';
                navbarAvatarContainer.innerHTML = `<img src="${userData.avatar}" alt="Profile" style="width: 100%; height: 100%; object-fit: cover;">`;
            }
            
            // Show orders link in navbar
            if (ordersNavItem) {
                ordersNavItem.classList.remove('d-none');
            }
            
            // Update cart count
            this.updateCartCount();
        } else {
            // Show login/register
            if (userMenu) {
                userMenu.innerHTML = `
                    <li><a class="dropdown-item" href="/login/"><i class="bi bi-box-arrow-in-right me-2"></i>Login</a></li>
                    <li><a class="dropdown-item" href="/register/"><i class="bi bi-person-plus me-2"></i>Register</a></li>
                `;
            }
            
            // Reset navbar avatar to default icon
            if (navbarAvatarContainer) {
                navbarAvatarContainer.style.border = 'none';
                navbarAvatarContainer.innerHTML = `<i class="bi bi-person-circle" style="font-size: 2rem; color: #e74c3c;"></i>`;
            }
            
            if (ordersNavItem) {
                ordersNavItem.classList.add('d-none');
            }
            
            // Clear cart count
            const cartBadge = document.getElementById('cartCount');
            if (cartBadge) cartBadge.textContent = '0';
        }
    },
    
    // Update cart count
    updateCartCount: async function() {
        if (!this.isAuthenticated()) return;
        
        try {
            const response = await this.fetch('/api/cart/');
            if (response.ok) {
                const cart = await response.json();
                const cartBadge = document.getElementById('cartCount');
                if (cartBadge) {
                    cartBadge.textContent = cart.total_items || 0;
                    cartBadge.style.display = (cart.total_items > 0) ? 'flex' : 'none';
                }
            }
        } catch (error) {
            console.error('Failed to update cart count:', error);
        }
    },
    
    // Login
    login: async function(email, password) {
        try {
            const response = await window.fetch('/api/users/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (data.access && data.refresh) {
                // Store tokens without updating UI yet
                this.setTokens(data.access, data.refresh, true);
                
                if (data.user) {
                    localStorage.setItem('user_data', JSON.stringify(data.user));
                }
                
                // Fetch complete user data including avatar
                await this.getUserData();
                
                // Now update UI with complete data
                this.updateUI();
                
                return { success: true, user: data.user };
            } else {
                return { success: false, error: data.detail || 'Login failed' };
            }
        } catch (error) {
            return { success: false, error: 'Network error. Please try again.' };
        }
    },
    
    // Logout
    logout: async function() {
        const refreshToken = this.getRefreshToken();
        
        if (refreshToken) {
            try {
                await window.fetch('/api/users/logout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ refresh_token: refreshToken })
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }
        
        this.clearTokens();
        window.location.href = '/';
    }
    };
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    if (typeof window.Auth !== 'undefined') {
        // First, try to get user data if authenticated (this will update the avatar)
        if (window.Auth.isAuthenticated()) {
            await window.Auth.getUserData();
        }
        
        // Then update the UI with all the menu items and cart count
        window.Auth.updateUI();
    }
});
