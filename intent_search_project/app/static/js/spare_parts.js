// Spare Parts functionality
async function searchSpareParts() {
    const brand = document.getElementById('brand-select').value;
    const deviceModel = document.getElementById('device-model').value;
    const issueDescription = document.getElementById('issue-description').value;
    const maxResults = document.getElementById('max-results').value;

    if (!brand || !deviceModel || !issueDescription) {
        alert('Please fill in all required fields');
        return;
    }

    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('spare-parts-results');
    
    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';

    try {
        const response = await fetch('/api/spare-parts/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                brand: brand,
                device_model: deviceModel,
                issue_description: issueDescription,
                max_results: parseInt(maxResults)
            })
        });

        const data = await response.json();
        loadingDiv.style.display = 'none';

        if (response.ok) {
            displaySparePartsResults(data);
        } else {
            resultsDiv.innerHTML = `<div class="error">Error: ${data.detail}</div>`;
        }
    } catch (error) {
        loadingDiv.style.display = 'none';
        resultsDiv.innerHTML = `<div class="error">Network error: ${error.message}</div>`;
    }
}

function displaySparePartsResults(spareParts) {
    const resultsDiv = document.getElementById('spare-parts-results');
    
    if (spareParts.length === 0) {
        resultsDiv.innerHTML = '<div class="no-results">No spare parts found for your query.</div>';
        return;
    }

    let html = `<h3>Found ${spareParts.length} spare parts:</h3><div class="spare-parts-grid">`;
    
    spareParts.forEach(part => {
        html += `
            <div class="spare-part-card">
                ${part.image_url ? `<img src="${part.image_url}" alt="${part.part_name}" class="part-image">` : ''}
                <div class="part-info">
                    <h4>${part.part_name}</h4>
                    <p class="part-number">Part #: ${part.part_number}</p>
                    <p class="part-price">₹${part.price}</p>
                    <p class="part-availability">${part.availability}</p>
                    <div class="compatibility-score">
                        Compatibility: ${(part.compatibility_score * 100).toFixed(0)}%
                    </div>
                    ${part.description ? `<p class="part-description">${part.description}</p>` : ''}
                    <div class="part-actions">
                        <button class="btn-primary" onclick="addToCart('${part.part_number}')">Add to Cart</button>
                        <button class="btn-secondary" onclick="viewDetails('${part.part_number}')">View Details</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    resultsDiv.innerHTML = html;
}

async function loadDeviceModels() {
    const brand = document.getElementById('brand-select').value;
    if (!brand) return;

    try {
        const response = await fetch(`/api/spare-parts/models/${brand}`);
        const models = await response.json();
        
        // You can populate a dropdown with available models if needed
        console.log('Available models for', brand, ':', models);
    } catch (error) {
        console.error('Error loading device models:', error);
    }
}

function addToCart(partNumber) {
    // Implement add to cart functionality
    alert(`Added part ${partNumber} to cart!`);
}

function viewDetails(partNumber) {
    // Implement view details functionality
    alert(`Viewing details for part ${partNumber}`);
}