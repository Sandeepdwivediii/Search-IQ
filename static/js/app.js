// ============================================
// AUTHENTICATION UTILITIES
// ============================================

// Check if user is logged in
function isAuthenticated() {
    return localStorage.getItem('access_token') !== null;
}

// Get auth header
function getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// Enhanced post function with auth
async function authenticatedPost(url, body) {
    const headers = isAuthenticated() ? getAuthHeader() : {'Content-Type': 'application/json'};
    
    const r = await fetch(url, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(body)
    });
    
    if (r.status === 401) {
        // Token expired or invalid
        logout();
        return;
    }
    
    if (!r.ok) {
        throw new Error(await r.text());
    }
    return r.json();
}

// Check auth on protected pages (only for main app page)
if (window.location.pathname === '/' && !isAuthenticated()) {
    window.location.href = '/login';
}

// Display user info if logged in
if (isAuthenticated() && window.location.pathname === '/') {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    // Add logout button to navbar if it exists
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu && user.username) {
        // Remove the "Get Started" button
        const getStartedBtn = navMenu.querySelector('.nav-cta');
        if (getStartedBtn) {
            getStartedBtn.remove();
        }
        
        // Add user menu
        const userMenu = document.createElement('div');
        userMenu.style.cssText = 'display: flex; align-items: center; gap: 16px;';
        userMenu.innerHTML = `
            <span style="color: #4a5568; font-weight: 500; font-size: 14px;">
                <i class="fas fa-user-circle"></i> ${user.username}
            </span>
            <button onclick="logout()" style="padding: 8px 20px; background: #ef4444; border: none; border-radius: 8px; color: white; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.3s ease;">
                <i class="fas fa-sign-out-alt"></i> Logout
            </button>
        `;
        navMenu.appendChild(userMenu);
    }
}

// ============================================
// TAB SWITCHING
// ============================================

function showTab(name, button) {
    const hide = ['search-tab', 'spare-parts-tab'];
    hide.forEach(id => { 
        const el = document.getElementById(id); 
        if (el) {
            el.style.display = 'none';
            el.classList.remove('active');
        }
    });
    
    const active = document.getElementById(name);
    if (active) {
        active.style.display = 'block';
        active.classList.add('active');
    }
    
    // Update button states
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (button) {
        button.classList.add('active');
    }
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================

document.addEventListener("DOMContentLoaded", () => {
    // Show default tab
    showTab("search-tab");
    
    // Search form handler
    const searchForm = document.getElementById("searchForm");
    if (searchForm) {
        searchForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const q = document.getElementById("searchQuery").value.trim();
            if (!q) {
                showNotification("Please enter a search query", "error");
                return;
            }
            
            // Show loading state
            const resultsContainer = document.getElementById("searchResults");
            resultsContainer.style.display = "block";
            resultsContainer.innerHTML = `
                <div style="text-align: center; padding: 60px 20px;">
                    <div class="loading-spinner-large">
                        <div class="spinner-ring ring-1"></div>
                        <div class="spinner-ring ring-2"></div>
                        <div class="spinner-ring ring-3"></div>
                        <div class="spinner-center">
                            <i class="fas fa-search"></i>
                        </div>
                    </div>
                    <h3 style="color: #667eea; margin-top: 24px; font-size: 1.25rem;">Searching...</h3>
                    <p style="color: #718096; margin-top: 8px;">Finding the best products for you</p>
                </div>
            `;
            
            try {
                // Use authenticated post for API calls
                const data = await authenticatedPost("/api/search", {
                    query: q,
                    max_results: 10
                });
                
                renderSearchResults(data);
                
            } catch (error) {
                resultsContainer.innerHTML = `
                    <div style="text-align: center; padding: 60px 20px;">
                        <i class="fas fa-exclamation-circle" style="font-size: 48px; color: #ef4444; margin-bottom: 16px;"></i>
                        <h3 style="color: #1a202c; margin-bottom: 8px;">Search Failed</h3>
                        <p style="color: #718096;">${error.message}</p>
                    </div>
                `;
            }
        });
    }
});

// ============================================
// RENDER SEARCH RESULTS
// ============================================

function renderSearchResults(data) {
    const resultsContainer = document.getElementById("searchResults");
    
    if (!data || data.length === 0) {
        resultsContainer.innerHTML = `
            <div style="text-align: center; padding: 60px 20px;">
                <div style="width: 80px; height: 80px; margin: 0 auto 24px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center;">
                    <i class="fas fa-search" style="font-size: 36px; color: #667eea;"></i>
                </div>
                <h3 style="color: #1a202c; font-size: 1.5rem; margin-bottom: 12px;">No Results Found</h3>
                <p style="color: #718096;">Try different keywords or browse our categories.</p>
            </div>
        `;
        return;
    }
    
    const header = `
        <div class="results-header" style="margin-bottom: 32px; text-align: center; animation: fadeInUp 0.5s ease;">
            <div style="display: inline-flex; align-items: center; gap: 12px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); padding: 12px 24px; border-radius: 30px; margin-bottom: 16px;">
                <i class="fas fa-check-circle" style="color: #667eea; font-size: 20px;"></i>
                <span style="color: #667eea; font-weight: 600; font-size: 15px;">
                    ${data.length} Product${data.length > 1 ? 's' : ''} Found
                </span>
            </div>
        </div>
    `;
    
    const resultsHTML = data.map((item, index) => `
        <div class="result-item" style="animation: fadeInUp 0.5s ease ${index * 0.1}s both;">
            <div class="item-icon" style="width: 60px; height: 60px; margin: 0 auto 16px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <i class="fas fa-box" style="font-size: 28px; color: #667eea;"></i>
            </div>
            <div class="item-title" style="font-size: 1.125rem; font-weight: 600; color: #1a202c; margin-bottom: 8px; line-height: 1.4;">
                ${item.title}
            </div>
            <div class="item-brand" style="color: #718096; font-size: 0.875rem; margin-bottom: 12px;">
                ${item.brand} • ${item.category}
            </div>
            <div class="item-price" style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: #f7fafc; border-radius: 8px; margin-bottom: 16px;">
                <span style="color: #1a202c; font-size: 1.25rem; font-weight: 700;">₹${item.price}</span>
                <span style="color: #f59e0b; font-weight: 600; font-size: 0.875rem;">
                    ⭐ ${item.rating}
                </span>
            </div>
            <button onclick="viewProductDetails('${item.title}')" style="width: 100%; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 8px; color: white; font-weight: 600; cursor: pointer; transition: all 0.3s ease;">
                <i class="fas fa-eye"></i> View Details
            </button>
        </div>
    `).join('');
    
    resultsContainer.innerHTML = `
        ${header}
        <div class="results-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px;">
            ${resultsHTML}
        </div>
    `;
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function viewProductDetails(title) {
    showNotification(`Opening details for: ${title}`, 'info');
    // Add your product details logic here
}

function showNotification(message, type = 'info') {
    const colors = {
        success: { bg: '#10b981', icon: 'check-circle' },
        error: { bg: '#ef4444', icon: 'exclamation-circle' },
        warning: { bg: '#f59e0b', icon: 'exclamation-triangle' },
        info: { bg: '#667eea', icon: 'info-circle' }
    };
    
    const color = colors[type] || colors.info;
    
    const existing = document.querySelector('.notification-toast');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = 'notification-toast';
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 40px; height: 40px; background: ${color.bg}; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <i class="fas fa-${color.icon}" style="color: white; font-size: 18px;"></i>
            </div>
            <p style="color: #1a202c; font-weight: 500; margin: 0; flex: 1;">${message}</p>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 24px;
        right: 24px;
        background: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        min-width: 300px;
        max-width: 400px;
        animation: slideInRight 0.4s ease;
        border-left: 4px solid ${color.bg};
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.4s ease';
        setTimeout(() => notification.remove(), 400);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    .result-item {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .result-item:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .result-item button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
`;
document.head.appendChild(style);