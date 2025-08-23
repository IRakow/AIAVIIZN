
// SHARED ELEMENTS MANAGEMENT - NO DUPLICATION
const sharedElements = [];


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
