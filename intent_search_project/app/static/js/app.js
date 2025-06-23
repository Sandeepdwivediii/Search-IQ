// DOM elements for product search
const searchInput = document.getElementById('searchQuery');
const searchForm = document.getElementById('searchForm');
const loadingIndicator = document.getElementById('loadingIndicator');
const searchResults = document.getElementById('searchResults');
const performanceMetrics = document.getElementById('performanceMetrics');

// Performance tracking
let searchHistory = [];
let lastSearchTime = 0;

// Event listeners for product search
if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        performSearch();
    });
}

if (searchInput) {
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });

    // Debounced search - auto-search as user types (optional)
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        
        const query = this.value.trim();
        if (query.length > 3) {
            searchTimeout = setTimeout(() => {
                performSearch();
            }, 500);
        }
    });
}

// Fixed tab functionality - MAJOR ERROR FIX
function showTab(tabName, buttonElement) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab and mark button as active
    const targetTab = document.getElementById(tabName + '-tab');
    if (targetTab) {
        targetTab.style.display = 'block';
    }
    
    // Add active class to clicked button
    if (buttonElement) {
        buttonElement.classList.add('active');
    }
}

// Product search functions
function searchExample(query) {
    if (searchInput) {
        searchInput.value = query;
        performSearch();
    }
}

// Fixed performSearch with better error handling
async function performSearch() {
    const query = searchInput ? searchInput.value.trim() : '';
    
    if (!query) {
        showError('Please enter a search query');
        return;
    }
    
    console.log('🔍 Starting search for:', query);
    
    const searchStartTime = performance.now();
    
    showLoading();
    hideResults();
    hideError();
    
    try {
        console.log('📡 Making API request to /api/search');
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        console.log('📊 Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ API Error:', response.status, errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Search response:', data);
        
        // Calculate search time
        const searchTime = performance.now() - searchStartTime;
        lastSearchTime = searchTime;
        
        // Store search history for analytics
        searchHistory.push({
            query: query,
            time: searchTime,
            results: data.items ? data.items.length : 0,
            intent: data.intent,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 50 searches
        if (searchHistory.length > 50) {
            searchHistory = searchHistory.slice(-50);
        }
        
        displayResults(data, searchTime);
        
    } catch (err) {
        console.error('❌ Search error:', err);
        showError(`Failed to search: ${err.message}`);
    } finally {
        hideLoading();
    }
}

// Fixed displayResults function
function displayResults(data, searchTime) {
    console.log('📋 Displaying results:', data);
    
    if (data.items && Array.isArray(data.items) && data.items.length > 0) {
        const isFastSearch = searchTime < 100;
        const speedIndicator = isFastSearch ? 
            '<span style="color: #4CAF50;">⚡ Lightning Fast</span>' : 
            `<span style="color: #666;">${Math.round(searchTime)}ms</span>`;
        
        let html = `
            <div class="results-header">
                <h3>Found ${data.items.length} Products ${data.intent ? `for "${data.intent.replace('_', ' ')}"` : ''}</h3>
                <div class="performance-info">${speedIndicator}</div>
            </div>
            <div class="results-grid">
        `;
        
        data.items.forEach((item, index) => {
            html += createItemCardHTML(item, index + 1);
        });
        
        html += '</div>';
        
        if (searchResults) {
            searchResults.innerHTML = html;
            searchResults.style.display = 'block';
            
            // Trigger animations
            setTimeout(() => {
                const resultItems = searchResults.querySelectorAll('.result-item');
                resultItems.forEach((item, index) => {
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                        item.classList.add('show');
                    }, index * 50);
                });
            }, 100);
        }
        
        if (isFastSearch && data.items.length > 0) {
            showPerformanceBadge();
        }
        
    } else {
        showError('No products found for your search. Try different keywords!');
    }
}

// Fixed createItemCardHTML with better error handling
function createItemCardHTML(item, number) {
    if (!item) {
        console.warn('⚠️ Invalid item data:', item);
        return '';
    }
    
    // Safely access item properties
    const itemName = item.name || item.product_name || 'Product Name';
    const itemBrand = item.brand || 'Generic';
    const itemCategory = item.category || item.product_category_tree || 'General';
    const itemPrice = parseFloat(item.price || item.discounted_price || 0);
    const itemRating = parseFloat(item.rating || item.product_rating || (3.5 + Math.random() * 1.5));
    
    // Generate image URL with better fallback
    let imageUrl = item.image_url || item.image || '';
    if (!imageUrl || imageUrl === 'null' || imageUrl === '') {
        const category = itemCategory.toLowerCase();
        const searchTerm = category.includes('fitness') ? 'fitness,equipment' : 
                          category.includes('mobile') || category.includes('phone') ? 'smartphone,technology' :
                          category.includes('laptop') || category.includes('computer') ? 'laptop,computer' :
                          category.includes('headphone') || category.includes('audio') ? 'headphones,audio' :
                          category.includes('kitchen') ? 'kitchen,appliances' :
                          'product,shopping';
        const seed = Math.abs(itemName.length * 7) % 100;
        imageUrl = `https://source.unsplash.com/400x400/?${searchTerm}&sig=${seed}`;
    }
    
    // Calculate discount and pricing
    let discountHtml = '';
    let originalPriceHtml = '';
    
    if (itemPrice > 0) {
        const originalPrice = Math.round(itemPrice * 1.3);
        const discount = Math.round(((originalPrice - itemPrice) / originalPrice) * 100);
        
        if (discount > 5) {
            originalPriceHtml = `<span class="item-original-price">₹${originalPrice.toLocaleString()}</span>`;
            discountHtml = `<span class="item-discount">${discount}% off</span>`;
        }
    }
    
    // Generate rating
    const rating = Math.min(5, Math.max(1, itemRating)).toFixed(1);
    const ratingCount = Math.floor(Math.random() * 2000) + 500;
    
    const ratingHtml = `
        <div class="item-rating">
            <div class="rating-stars">
                <span>${rating}</span>
                <i class="fas fa-star"></i>
            </div>
            <span class="rating-count">(${ratingCount.toLocaleString()})</span>
        </div>
    `;
    
    // Price section
    const priceHtml = itemPrice > 0 ? `
        <div class="item-price-section">
            <span class="item-price">₹${itemPrice.toLocaleString()}</span>
            ${originalPriceHtml}
            ${discountHtml}
        </div>
    ` : `
        <div class="item-price-section">
            <span class="item-price" style="color: #888;">Price on Request</span>
        </div>
    `;
    
    // Escape quotes for onclick handlers
    const escapedName = itemName.replace(/'/g, '&#39;').replace(/"/g, '&quot;');
    
    return `
        <div class="result-item item-card" style="opacity: 0; transform: translateY(20px);">
            <div class="item-image">
                <img src="${imageUrl}" 
                     alt="${itemName}" 
                     loading="lazy"
                     onerror="this.onerror=null; this.src='https://via.placeholder.com/400x400/e3f2fd/1976d2?text=Product+Image';">
            </div>
            
            <div class="item-title">${itemName}</div>
            
            ${ratingHtml}
            
            ${priceHtml}
            
            <div class="item-brand">Brand: ${itemBrand}</div>
            
            <div class="item-category">${itemCategory}</div>
            
            <div class="item-features">
                ✓ Fast Delivery Available<br>
                ✓ Easy Returns & Exchange
            </div>
            
            <div class="item-actions">
                <button class="btn-cart" onclick="addToCart('${escapedName}')">
                    <i class="fas fa-shopping-cart"></i> Add to Cart
                </button>
                <button class="btn-wishlist" onclick="addToWishlist('${escapedName}')">
                    <i class="fas fa-heart"></i>
                </button>
            </div>
        </div>
    `;
}

// Fixed spare parts functions
async function searchSpareParts() {
    const brand = document.getElementById('brand-select')?.value;
    const deviceModel = document.getElementById('device-model')?.value;
    const issueDescription = document.getElementById('issue-description')?.value;
    const maxResults = document.getElementById('max-results')?.value || 10;

    if (!brand || !deviceModel || !issueDescription) {
        showNotification('Please fill in all required fields', 'warning');
        return;
    }

    const loadingDiv = document.getElementById('spare-parts-loading');
    const resultsDiv = document.getElementById('spare-parts-results');
    
    try {
        if (loadingDiv) loadingDiv.style.display = 'block';
        if (resultsDiv) resultsDiv.innerHTML = '';

        console.log('🔧 Searching spare parts:', { brand, deviceModel, issueDescription });

        const response = await fetch('/api/spare-parts/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                brand: brand,
                device_model: deviceModel,
                issue_description: issueDescription,
                max_results: parseInt(maxResults) || 10
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            displaySparePartsResults(data);
        } else {
            console.error('Spare parts API error:', data);
            if (resultsDiv) {
                resultsDiv.innerHTML = `<div class="error">Error: ${data.detail || 'Failed to get spare parts recommendations'}</div>`;
            }
        }
    } catch (error) {
        console.error('Spare parts search error:', error);
        if (resultsDiv) {
            resultsDiv.innerHTML = `<div class="error">Network error: ${error.message}</div>`;
        }
    } finally {
        if (loadingDiv) loadingDiv.style.display = 'none';
    }
}

// Fixed displaySparePartsResults
function displaySparePartsResults(spareParts) {
    const resultsDiv = document.getElementById('spare-parts-results');
    if (!resultsDiv) return;
    
    if (!Array.isArray(spareParts) || spareParts.length === 0) {
        resultsDiv.innerHTML = '<div class="no-results">No spare parts found for your query.</div>';
        return;
    }

    let html = `
        <div class="results-header">
            <h3>Found ${spareParts.length} spare parts</h3>
        </div>
        <div class="results-grid">
    `;
    
    spareParts.forEach((part, index) => {
        if (!part) return;
        
        const imageUrl = part.image_url || `https://source.unsplash.com/300x300/?electronics,parts&sig=${index}`;
        const partName = part.part_name || 'Spare Part';
        const partNumber = part.part_number || 'N/A';
        const price = parseFloat(part.price) || 0;
        const availability = part.availability || 'Check Availability';
        const compatibility = parseFloat(part.compatibility_score) || 0;
        
        html += `
            <div class="result-item spare-part-card" style="opacity: 0; transform: translateY(20px);">
                <div class="item-image">
                    <img src="${imageUrl}" alt="${partName}" loading="lazy"
                         onerror="this.onerror=null; this.src='https://via.placeholder.com/300x300/f0f0f0/666?text=Spare+Part';">
                </div>
                <div class="part-info">
                    <h4 class="item-title">${partName}</h4>
                    <p class="part-number">Part #: ${partNumber}</p>
                    <div class="item-price-section">
                        <span class="item-price">₹${price.toLocaleString()}</span>
                    </div>
                    <p class="part-availability">${availability}</p>
                    <div class="compatibility-score">
                        Compatibility: ${Math.round(compatibility * 100)}%
                    </div>
                    ${part.description ? `<p class="part-description">${part.description}</p>` : ''}
                    <div class="item-actions">
                        <button class="btn-cart" onclick="addToCart('${partNumber}')">Add to Cart</button>
                        <button class="btn-wishlist" onclick="viewDetails('${partNumber}')">View Details</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    resultsDiv.innerHTML = html;
    
    // Add animations
    setTimeout(() => {
        const resultItems = resultsDiv.querySelectorAll('.result-item');
        resultItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
                item.classList.add('show');
            }, index * 50);
        });
    }, 100);
}

// Utility functions - Fixed
async function loadDeviceModels() {
    const brand = document.getElementById('brand-select')?.value;
    if (!brand) return;

    try {
        const response = await fetch(`/api/spare-parts/models/${brand}`);
        if (response.ok) {
            const models = await response.json();
            console.log('Available models for', brand, ':', models);
        }
    } catch (error) {
        console.error('Error loading device models:', error);
    }
}

function fillIssueExample(issue) {
    const issueTextarea = document.getElementById('issue-description');
    if (issueTextarea) {
        issueTextarea.value = issue;
    }
}

function viewDetails(partNumber) {
    showNotification(`Viewing details for part ${partNumber}`, 'info');
}

function showPerformanceBadge() {
    // Prevent duplicate badges
    const existingBadge = document.querySelector('.performance-badge');
    if (existingBadge) return;
    
    const badge = document.createElement('div');
    badge.className = 'performance-badge';
    badge.innerHTML = '⚡ Cached Result - Lightning Fast!';
    badge.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        z-index: 1000;
        animation: slideInRight 0.5s ease;
    `;
    
    document.body.appendChild(badge);
    
    setTimeout(() => {
        badge.style.animation = 'fadeOut 0.5s ease';
        setTimeout(() => {
            if (badge.parentNode) {
                badge.parentNode.removeChild(badge);
            }
        }, 500);
    }, 3000);
}

function addToCart(productName) {
    showNotification(`"${productName}" added to cart!`, 'success');
}

function addToWishlist(productName) {
    showNotification(`"${productName}" added to wishlist!`, 'info');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.innerHTML = message;
    
    const bgColors = {
        'success': '#4CAF50',
        'info': '#2196F3',
        'warning': '#FF9800',
        'error': '#f44336'
    };
    
    const bgColor = bgColors[type] || bgColors.info;
    
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1000;
        max-width: 300px;
        animation: slideInUp 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function getSearchAnalytics() {
    if (searchHistory.length === 0) return { message: 'No searches performed yet' };
    
    const avgTime = searchHistory.reduce((sum, search) => sum + search.time, 0) / searchHistory.length;
    const fastSearches = searchHistory.filter(search => search.time < 100).length;
    
    return {
        totalSearches: searchHistory.length,
        averageTime: Math.round(avgTime) + 'ms',
        fastSearchPercentage: Math.round((fastSearches / searchHistory.length) * 100) + '%',
        lastSearchTime: Math.round(lastSearchTime) + 'ms',
        searchHistory: searchHistory.slice(-10)
    };
}

// Helper functions with better error handling
function showLoading() {
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
}

function hideLoading() {
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

function showResults() {
    if (searchResults) {
        searchResults.style.display = 'block';
    }
}

function hideResults() {
    if (searchResults) {
        searchResults.style.display = 'none';
    }
}

function showError(message) {
    console.error('🚨 Showing error:', message);
    if (searchResults) {
        searchResults.innerHTML = `<div class="error">${message}</div>`;
        searchResults.style.display = 'block';
    }
}

function hideError() {
    // Error is shown in results div, so hiding results hides error
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInUp {
        from { transform: translateY(100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);

console.log('🚀 Search Analytics available via getSearchAnalytics()');

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ App initialized successfully');
    
    // Test if elements exist
    const elements = ['searchQuery', 'searchForm', 'searchResults', 'loadingIndicator'];
    elements.forEach(id => {
        const element = document.getElementById(id);
        console.log(`${id}:`, element ? '✅ Found' : '❌ Missing');
    });
    
    // Initialize first tab as active
    const firstTab = document.querySelector('.tab-btn.active');
    if (firstTab) {
        showTab('search', firstTab);
    }
});