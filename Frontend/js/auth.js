/**
 * Authentication Service
 * Handles user registration, login, and session management
 */

// ===== MODAL MANAGEMENT =====

function openAuthModal() {
    const modal = document.getElementById('authModal');
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
    resetAuthForms();
}

function toggleAuthForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    loginForm.classList.toggle('active');
    registerForm.classList.toggle('active');
}

// ===== FORM HANDLING =====

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const spinner = submitBtn.querySelector('.spinner');

    try {
        submitBtn.disabled = true;
        spinner.classList.remove('hidden');

        Logger.log('Logging in...', { email });

        const response = await api.login(email, password);
        
        Logger.log('Login successful', response);
        
        // Get user data (for demo, we'll use email)
        localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify({
            email: email,
            token: response.access_token,
        }));

        showNotification('Login successful!', 'success');
        closeAuthModal();
        updateUIAfterAuth();

        // Redirect to dashboard after 1 second
        setTimeout(() => {
            document.getElementById('dashboard').classList.remove('hidden');
            document.getElementById('home').classList.add('hidden');
        }, 500);

    } catch (error) {
        Logger.error('Login error', error);
        showNotification('Login failed: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        spinner.classList.add('hidden');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const fullName = document.getElementById('regFullName').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const spinner = submitBtn.querySelector('.spinner');

    try {
        submitBtn.disabled = true;
        spinner.classList.remove('hidden');

        Logger.log('Registering user...', { email, username });

        const response = await api.register(email, username, password, fullName);
        
        Logger.log('Registration successful', response);
        
        showNotification('Registration successful! Please login.', 'success');
        
        // Switch to login form
        document.getElementById('registerForm').classList.remove('active');
        document.getElementById('loginForm').classList.add('active');
        
        // Prefill email
        document.getElementById('loginEmail').value = email;

    } catch (error) {
        Logger.error('Registration error', error);
        showNotification('Registration failed: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        spinner.classList.add('hidden');
    }
}

function handleLogout() {
    api.clearToken();
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    updateUIAfterLogout();
    showNotification('Logged out successfully', 'success');
    window.location.href = '#home';
}

// ===== UI UPDATES =====

function updateUIAfterAuth() {
    const userData = JSON.parse(localStorage.getItem(STORAGE_KEYS.USER_DATA) || '{}');
    
    // Hide auth button, show user menu
    document.getElementById('authBtn').classList.add('hidden');
    document.getElementById('userMenuBtn').classList.remove('hidden');
    
    // Set user email
    if (userData.email) {
        document.getElementById('userEmail').textContent = userData.email.split('@')[0];
    }

    // Hide home section, show dashboard
    document.getElementById('home').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
}

function updateUIAfterLogout() {
    // Show auth button, hide user menu
    document.getElementById('authBtn').classList.remove('hidden');
    document.getElementById('userMenuBtn').classList.add('hidden');
    document.getElementById('userMenu').classList.add('hidden');

    // Show home section, hide dashboard
    document.getElementById('home').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');
    
    // Clear all data
    clearAllData();
}

function toggleUserMenu() {
    const userMenu = document.getElementById('userMenu');
    userMenu.classList.toggle('hidden');
}

function resetAuthForms() {
    document.getElementById('loginForm').reset();
    document.getElementById('registerForm').reset();
    document.getElementById('registerForm').classList.remove('active');
    document.getElementById('loginForm').classList.add('active');
}

// ===== AUTHORIZATION CHECKS =====

function isAuthenticated() {
    return !!localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
}

function checkAuth() {
    if (!isAuthenticated()) {
        openAuthModal();
        return false;
    }
    return true;
}

function requireAuth(callback) {
    if (isAuthenticated()) {
        callback();
    } else {
        openAuthModal();
    }
}

// ===== INITIALIZATION =====

function initAuth() {
    Logger.log('Initializing authentication...');

    // Check if user is already authenticated
    if (isAuthenticated()) {
        updateUIAfterAuth();
    } else {
        updateUIAfterLogout();
    }

    // Close modal when clicking outside
    document.getElementById('authModal').addEventListener('click', (e) => {
        if (e.target.id === 'authModal') {
            closeAuthModal();
        }
    });

    // Close user menu when clicking outside
    document.addEventListener('click', (e) => {
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userMenu = document.getElementById('userMenu');
        
        if (!userMenuBtn.contains(e.target) && !userMenu.contains(e.target)) {
            userMenu.classList.add('hidden');
        }
    });
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuth);
} else {
    initAuth();
}

// Export for modular use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        openAuthModal,
        closeAuthModal,
        handleLogin,
        handleRegister,
        handleLogout,
        isAuthenticated,
        checkAuth,
    };
}