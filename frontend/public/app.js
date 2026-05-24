// MargIntel Frontend Logic
const API_BASE_URL = 'http://localhost:5000';

// Navigation Auth State Setup
document.addEventListener('DOMContentLoaded', () => {
    checkAuthState();
    setupFormListeners();
});

function checkAuthState() {
    const token = localStorage.getItem('margintel_token');
    const authLinks = document.querySelector('.nav-links');
    
    // Only process if we are on a page with a navbar
    if (authLinks) {
        if (token) {
            // If logged in, modify navbar
            authLinks.innerHTML = `
                <a href="dashboard.html">Dashboard</a>
                <a href="#" onclick="logout(event)" class="login-btn">Log Out</a>
            `;
        } else {
            // If NOT logged in, show default links
            authLinks.innerHTML = `
                <a href="login.html">Login</a>
                <a href="signup.html" class="signup-btn">Sign Up</a>
            `;
        }
    }
}

function logout(e) {
    if (e) e.preventDefault();
    localStorage.removeItem('margintel_token');
    localStorage.removeItem('margintel_user');
    window.location.href = 'landing.html';
}

function setupFormListeners() {
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const btn = document.getElementById('signupBtn');
    const errorMsg = document.getElementById('signupError');
    
    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (password !== confirmPassword) {
        errorMsg.textContent = "Passwords do not match.";
        return;
    }

    try {
        btn.textContent = 'Creating Account...';
        btn.disabled = true;
        errorMsg.textContent = '';

        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                full_name: fullName,
                email: email,
                password: password,
                confirm_password: confirmPassword
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Signup failed');
        }

        // Redirect to login page as requested instead of auto-logging in
        window.location.href = 'login.html';

    } catch (error) {
        errorMsg.textContent = error.message;
    } finally {
        btn.textContent = 'Sign Up';
        btn.disabled = false;
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('loginBtn');
    const errorMsg = document.getElementById('loginError');
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        btn.textContent = 'Logging In...';
        btn.disabled = true;
        errorMsg.textContent = '';

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Login failed');
        }

        // Store JWT
        localStorage.setItem('margintel_token', data.token);
        localStorage.setItem('margintel_user', JSON.stringify(data.user));
        
        window.location.href = 'dashboard.html';

    } catch (error) {
        errorMsg.textContent = error.message;
    } finally {
        btn.textContent = 'Log In';
        btn.disabled = false;
    }
}

// Utility: Fetch with Auth Header
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('margintel_token');
    if (!token) {
        logout();
        throw new Error('No authentication token found');
    }

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401) {
        logout();
        throw new Error('Session expired. Please strictly login again.');
    }

    return response;
}
