function $(id) { return document.getElementById(id); }

async function post(url, body) {
    const token = localStorage.getItem("token");

    const headers = {
        "Content-Type": "application/json"
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const r = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body)
    });

    if (!r.ok) {
        // To make debugging easier, show status text
        const errText = await r.text();
        throw new Error(`HTTP ${r.status} - ${errText}`);
    }

    return r.json();
}

// Show loading state
function showLoading(show = true) {
    const loadingHTML = `
        <div class="loading-container" style="text-align: center; padding: 60px 20px;">
            <div class="loading-spinner-large">
                <div class="spinner-ring ring-1"></div>
                <div class="spinner-ring ring-2"></div>
                <div class="spinner-ring ring-3"></div>
                <div class="spinner-center">
                    <i class="fas fa-brain"></i>
                </div>
            </div>
            <h3 style="color: #667eea; margin-top: 24px; font-size: 1.25rem;">AI is Analyzing...</h3>
            <p style="color: #718096; margin-top: 8px;">Finding the best parts for you</p>
        </div>
    `;
    
    const container = $("recommendations-container");
    if (container) {
        container.innerHTML = show ? loadingHTML : '';
        container.style.display = show ? 'block' : 'none';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = $("search-spare-parts-btn");
    const getPartsBtn = $("get-parts-btn");
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            const message = $("problem-description").value.trim();
            
            if (!message) {
                showNotification("Please describe the problem", "error");
                return;
            }
            
            // Show button loading state
            analyzeBtn.disabled = true;
            const originalText = analyzeBtn.querySelector('span').textContent;
            analyzeBtn.querySelector('span').textContent = 'Analyzing...';
            analyzeBtn.querySelector('i').className = 'fas fa-spinner fa-spin';
            
            try {
                const data = await post("/spare-parts/parse", { message });
                
                const sel = $("invoice-select");
                sel.innerHTML = '<option value="">-- select your order --</option>' + 
                    (data.candidates || []).map(c => {
                        const when = c.purchase_date ? new Date(c.purchase_date).toLocaleDateString() : "";
                        return `<option value="${c.invoice_number}">${c.invoice_number} — ${c.brand} ${c.product_model} ${when ? `(${when})` : ""}</option>`;
                    }).join("");
                
                const orderPicker = $("order-picker");
                if ((data.candidates || []).length) {
                    orderPicker.style.display = "block";
                    // Animate in
                    setTimeout(() => orderPicker.classList.add('fade-in'), 10);
                    showNotification(`Found ${data.candidates.length} matching order(s)`, "success");
                } else {
                    orderPicker.style.display = "none";
                    showNotification("No matching orders found", "warning");
                }
                
                sel.dataset.fault = (data.parsed && data.parsed.fault) ? data.parsed.fault : "fault";
                
            } catch (error) {
                showNotification("Error analyzing request: " + error.message, "error");
            } finally {
                // Restore button state
                analyzeBtn.disabled = false;
                analyzeBtn.querySelector('span').textContent = originalText;
                analyzeBtn.querySelector('i').className = 'fas fa-brain';
            }
        });
    }
    
    if (getPartsBtn) {
        getPartsBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            const sel = $("invoice-select");
            const inv = sel.value;
            
            if (!inv) {
                showNotification("Please select an order", "error");
                return;
            }
            
            const fault = sel.dataset.fault || "fault";
            
            // Show loading
            showLoading(true);
            
            // Show button loading state
            getPartsBtn.disabled = true;
            const originalText = getPartsBtn.querySelector('span').textContent;
            getPartsBtn.querySelector('span').textContent = 'Loading...';
            getPartsBtn.querySelector('i').className = 'fas fa-spinner fa-spin';
            
            try {
                const parts = await post("/spare-parts/recommend", {
                    invoice_number: inv,
                    fault_keyword: fault,
                    max_results: 6
                });
                
                showLoading(false);
                renderParts(parts);
                
                // Scroll to results
                setTimeout(() => {
                    $("recommendations-container")?.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'nearest' 
                    });
                }, 100);
                
            } catch (error) {
                showLoading(false);
                showNotification("Error fetching parts: " + error.message, "error");
            } finally {
                // Restore button state
                getPartsBtn.disabled = false;
                getPartsBtn.querySelector('span').textContent = originalText;
                getPartsBtn.querySelector('i').className = 'fas fa-tools';
            }
        });
    }
});

function renderParts(parts) {
    const cont = $("recommendations-container");
    if (!cont) return;
    
    if (!parts || !parts.length) {
        cont.innerHTML = `
            <div class="no-results" style="text-align: center; padding: 60px 20px; animation: fadeIn 0.5s ease;">
                <div style="width: 80px; height: 80px; margin: 0 auto 24px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center;">
                    <i class="fas fa-search" style="font-size: 36px; color: #667eea;"></i>
                </div>
                <h3 style="color: #1a202c; font-size: 1.5rem; margin-bottom: 12px;">No Parts Found</h3>
                <p style="color: #718096;">Try selecting a different order or describe your problem differently.</p>
            </div>
        `;
        cont.style.display = 'block';
        return;
    }
    
    // Results header with count
    const header = `
        <div class="results-header" style="margin-bottom: 32px; text-align: center; animation: fadeInUp 0.5s ease;">
            <div style="display: inline-flex; align-items: center; gap: 12px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); padding: 12px 24px; border-radius: 30px; margin-bottom: 16px;">
                <i class="fas fa-check-circle" style="color: #667eea; font-size: 20px;"></i>
                <span style="color: #667eea; font-weight: 600; font-size: 15px;">
                    ${parts.length} Compatible Part${parts.length > 1 ? 's' : ''} Found
                </span>
            </div>
            <h3 style="color: #1a202c; font-size: 1.75rem; font-weight: 700; margin-bottom: 8px;">
                Recommended Spare Parts
            </h3>
            <p style="color: #718096; font-size: 1rem;">
                AI-selected parts based on your device and problem description
            </p>
        </div>
    `;
    
    // Create beautiful cards for each part
    const cards = parts.map((p, index) => {
        const score = Math.round(p.compatibility_score * 100);
        const scoreColor = score >= 90 ? '#10b981' : score >= 70 ? '#f59e0b' : '#667eea';
        const scoreLabel = score >= 90 ? 'Excellent Match' : score >= 70 ? 'Good Match' : 'Compatible';
        
        return `
            <div class="part-card" style="animation: fadeInUp 0.5s ease ${index * 0.1}s both;">
                <div class="part-card-inner">
                    <!-- Match Badge -->
                    <div class="match-badge" style="position: absolute; top: 16px; right: 16px; z-index: 2;">
                        <div style="background: ${scoreColor}; color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 12px ${scoreColor}33;">
                            <i class="fas fa-bolt"></i>
                            <span>${score}%</span>
                        </div>
                    </div>
                    
                    <!-- Card Glow Effect -->
                    <div class="card-glow" style="position: absolute; inset: -2px; background: linear-gradient(135deg, ${scoreColor}33, transparent); border-radius: 18px; opacity: 0; transition: opacity 0.3s ease; pointer-events: none;"></div>
                    
                    <!-- Part Icon -->
                    <div class="part-icon" style="width: 80px; height: 80px; margin: 0 auto 20px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 16px; display: flex; align-items: center; justify-content: center; position: relative;">
                        <i class="fas fa-cog" style="font-size: 36px; color: #667eea;"></i>
                        <div style="position: absolute; inset: -4px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 18px; opacity: 0.2; filter: blur(8px);"></div>
                    </div>
                    
                    <!-- Part Info -->
                    <div style="text-align: center; margin-bottom: 20px;">
                        <h4 class="part-name" style="color: #1a202c; font-size: 1.125rem; font-weight: 600; margin-bottom: 8px; line-height: 1.4;">
                            ${p.part_name}
                        </h4>
                        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; color: #718096; font-size: 0.875rem; margin-bottom: 4px;">
                            <i class="fas fa-hashtag" style="font-size: 12px;"></i>
                            <span>${p.part_number}</span>
                        </div>
                        <div class="compatibility-label" style="display: inline-block; background: ${scoreColor}15; color: ${scoreColor}; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-top: 8px;">
                            <i class="fas fa-check-circle" style="font-size: 10px;"></i>
                            ${scoreLabel}
                        </div>
                    </div>
                    
                    <!-- Price Section -->
                    <div style="background: #f7fafc; padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <span style="color: #718096; font-size: 0.875rem; font-weight: 500;">Price</span>
                            <div style="display: flex; align-items: baseline; gap: 4px;">
                                <span style="color: #1a202c; font-size: 1.5rem; font-weight: 700;">₹${p.price}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div style="display: grid; grid-template-columns: 1fr auto; gap: 8px;">
                        <button class="btn-add-cart" onclick="addToCart('${p.part_number}', '${p.part_name}', ${p.price})" style="flex: 1; padding: 12px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; border-radius: 10px; color: white; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; gap: 8px;">
                            <i class="fas fa-cart-plus"></i>
                            <span>Add to Cart</span>
                        </button>
                        <button class="btn-view-details" onclick="viewPartDetails('${p.part_number}')" style="padding: 12px 16px; background: #f7fafc; border: 2px solid #e2e8f0; border-radius: 10px; color: #667eea; font-weight: 600; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center;">
                            <i class="fas fa-info-circle"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    cont.innerHTML = `
        ${header}
        <div class="results-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px;">
            ${cards}
        </div>
    `;
    cont.style.display = 'block';
}

// Helper function for notifications
function showNotification(message, type = 'info') {
    const colors = {
        success: { bg: '#10b981', icon: 'check-circle' },
        error: { bg: '#ef4444', icon: 'exclamation-circle' },
        warning: { bg: '#f59e0b', icon: 'exclamation-triangle' },
        info: { bg: '#667eea', icon: 'info-circle' }
    };
    
    const color = colors[type] || colors.info;
    
    // Remove existing notification
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

// Placeholder functions for cart and details (integrate with your backend)
function addToCart(partNumber, partName, price) {
    console.log('Adding to cart:', { partNumber, partName, price });
    showNotification(`${partName} added to cart!`, 'success');
    // Add your cart logic here
}

function viewPartDetails(partNumber) {
    console.log('Viewing details for:', partNumber);
    showNotification('Opening part details...', 'info');
    // Add your details modal/page logic here
}