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

// Form submission
document.getElementById('loginForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Clear previous errors
    ['email-username', 'password'].forEach(clearError);
    
    const emailOrUsername = document.getElementById('email-username').value.trim();
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('remember-me').checked;
    
    // Client-side validation
    if (!emailOrUsername || !password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    // Show loading state
    const btn = document.getElementById('login-btn');
    btn.disabled = true;
    btn.querySelector('span').textContent = 'Signing In...';
    btn.querySelector('i').className = 'fas fa-spinner fa-spin';
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email_or_username: emailOrUsername,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token
           localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));

    // Optional: keep compatibility (not necessary, but harmless)
    localStorage.setItem('access_token', data.access_token);
            
            if (rememberMe) {
                localStorage.setItem('remember_me', 'true');
            }
            
            showNotification('Login successful!', 'success');
            
            // Redirect to home page
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showNotification(data.error || 'Login failed', 'error');
            
            if (data.error.includes('credentials')) {
                showError('password', 'Invalid email/username or password');
            }
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        btn.disabled = false;
        btn.querySelector('span').textContent = 'Sign In';
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