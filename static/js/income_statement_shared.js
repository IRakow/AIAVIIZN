
// SHARED ELEMENTS MANAGEMENT - NO DUPLICATION
const sharedElements = [];

// PLAYWRIGHT-CAPTURED API ENDPOINTS
const playwrightApiEndpoints = [
  {
    "url": "https://celticprop.appfolio.com/buffered_reports/income_statement/api/reports/data",
    "method": "GET",
    "status": 200,
    "response_size": 15420,
    "timing": 245,
    "content_type": "application/json"
  },
  {
    "url": "https://celticprop.appfolio.com/buffered_reports/income_statement/api/calculations/rent_roll",
    "method": "POST",
    "status": 200,
    "response_size": 8765,
    "timing": 156,
    "content_type": "application/json"
  }
];

// Enhanced API loading using captured endpoints
function loadFromPlaywrightEndpoints() {
    playwrightApiEndpoints.forEach(endpoint => {
        if (endpoint.method === 'GET' && endpoint.url.includes('/api/')) {
            // Use actual captured API endpoint
            fetch(endpoint.url)
                .then(response => response.json())
                .then(data => updateSharedElementsFromApi(data))
                .catch(error => console.log('API call failed:', error));
        }
    });
}


// Load shared element values
function loadSharedElementValues() {
    sharedElements.forEach(element => {
        const elementId = element.element_id;
        const elementContainer = document.querySelector(`[data-element-id="${elementId}"]`);
        
        if (elementContainer) {
            // Load from API or shared data store
            loadElementValue(elementId, element).then(value => {
                updateElementDisplay(elementContainer, value);
            });
        }
    });
    
    // ENHANCED: Load from Playwright endpoints if available
    if (typeof loadFromPlaywrightEndpoints === 'function') {
        loadFromPlaywrightEndpoints();
    }
}

// Update element display
function updateElementDisplay(container, value) {
    const valueElement = container.querySelector('.element-value');
    if (valueElement) {
        valueElement.textContent = formatElementValue(value);
    }
}

// Format element value based on type
function formatElementValue(value) {
    if (typeof value === 'object' && value.amount && value.currency) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: value.currency
        }).format(value.amount);
    }
    return value;
}

// ENHANCED: Update shared elements from API data
function updateSharedElementsFromApi(apiData) {
    // Process API data and update shared elements
    Object.keys(apiData).forEach(key => {
        const element = sharedElements.find(el => el.element_name === key);
        if (element) {
            const container = document.querySelector(`[data-element-id="${element.element_id}"]`);
            if (container) {
                updateElementDisplay(container, apiData[key]);
            }
        }
    });
}

// Load on document ready
document.addEventListener('DOMContentLoaded', loadSharedElementValues);

{"shared_elements": [{"element_name": "total_monthly_rent", "element_type": "calculation", "data_category": "financial", "current_value": {"amount": 12500, "currency": "USD"}, "formula_expression": "SUM(unit_rent_amounts)", "display_label": "Total Monthly Rent"}]}
