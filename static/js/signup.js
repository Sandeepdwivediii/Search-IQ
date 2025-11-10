// Password strength checker
function checkPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;
    
    return strength;
}

function updatePasswordStrength(password) {
    const strengthBar = document.querySelector('.strength-bar');
    if (!strengthBar) return;
    
    const strength = checkPasswordStrength(password);
    
    strengthBar.classList.remove('weak', 'medium', 'strong');
    
    if (strength <= 2) {
        strengthBar.classList.add('weak');
    } else if (strength <= 4) {
        strengthBar.classList.add('medium');
    } else {
        strengthBar.classList.add('strong');
    }
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling?.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        if (icon) icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        if (icon) icon.className = 'fas fa-eye';
    }
}

function showError(fieldId, message) {
    const errorElement = document.getElementById(`${fieldId}-error`);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
}

function clearError(fieldId) {
    const errorElement = document.getElementById(`${fieldId}-error`);
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('show');
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 24px;
        right: 24px;
        background: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideIn 0.4s ease;
        border-left: 4px solid ${type === 'success' ? '#10b981' : '#ef4444'};
    `;
    
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}" 
           style="color: ${type === 'success' ? '#10b981' : '#ef4444'}; font-size: 20px;"></i>
        <span style="color: #1a202c; font-weight: 500;">${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.4s ease';
        setTimeout(() => notification.remove(), 400);
    }, 3000);
}

// Password strength real-time check
document.getElementById('password')?.addEventListener('input', function() {
    updatePasswordStrength(this.value);
});

// Form submission
document.getElementById('signupForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Clear previous errors
    ['username', 'email', 'password', 'confirm-password'].forEach(clearError);
    
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // Client-side validation
    let hasError = false;
    
    if (username.length < 3) {
        showError('username', 'Username must be at least 3 characters');
        hasError = true;
    }
    
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showError('email', 'Please enter a valid email');
        hasError = true;
    }
    
    if (password.length < 8) {
        showError('password', 'Password must be at least 8 characters');
        hasError = true;
    }
    
    if (password !== confirmPassword) {
        showError('confirm-password', 'Passwords do not match');
        hasError = true;
    }
    
    if (hasError) return;
    
    // Show loading state
    const btn = document.getElementById('signup-btn');
    btn.disabled = true;
    btn.querySelector('span').textContent = 'Creating Account...';
    btn.querySelector('i').className = 'fas fa-spinner fa-spin';
    
    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            showNotification('Account created successfully!', 'success');
            
            // Redirect to home page
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showNotification(data.error || 'Failed to create account', 'error');
            
            // Show field-specific errors if available
            if (data.error.includes('Username')) {
                showError('username', data.error);
            } else if (data.error.includes('Email')) {
                showError('email', data.error);
            } else if (data.error.includes('Password')) {
                showError('password', data.error);
            }
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        btn.disabled = false;
        btn.querySelector('span').textContent = 'Create Account';
        btn.querySelector('i').className = 'fas fa-arrow-right';
    }
});

// Animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);