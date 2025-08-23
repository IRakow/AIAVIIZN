/**
 * AIVIIZN Rent Roll Calculations
 * Real calculation logic extracted from AppFolio Rent Roll report
 * Generated from: https://celticprop.appfolio.com/buffered_reports/rent_roll?customize=true
 */

// Core calculation functions extracted from AppFolio
function calculateTotalRent(rentData) {
    /**
     * Total Monthly Rent: SUM(Rent for all active units)
     * Formula extracted from AppFolio rent roll logic
     */
    return rentData
        .filter(unit => unit.status === 'Active')
        .reduce((sum, unit) => sum + parseFloat(unit.rent || 0), 0);
}

function calculateTotalDeposits(rentData) {
    /**
     * Total Security Deposits: SUM(Deposit for all active units)  
     * Formula extracted from AppFolio deposit calculations
     */
    return rentData
        .filter(unit => unit.status === 'Active')
        .reduce((sum, unit) => sum + parseFloat(unit.deposit || 0), 0);
}

function calculateTotalPastDue(rentData) {
    /**
     * Total Past Due Amount: SUM(Past Due for all tenants)
     * Formula extracted from AppFolio delinquency tracking
     */
    return rentData
        .reduce((sum, unit) => sum + parseFloat(unit.pastDue || 0), 0);
}

function calculateOccupancyRate(rentData) {
    /**
     * Occupancy Rate: (Active Units / Total Units) * 100
     * Formula extracted from AppFolio occupancy calculations
     */
    const totalUnits = rentData.length;
    const activeUnits = rentData.filter(unit => unit.status === 'Active').length;
    
    if (totalUnits === 0) return 0;
    return (activeUnits / totalUnits) * 100;
}

function calculateAverageRent(rentData) {
    /**
     * Average Rent per Unit: Total Rent / Number of Active Units
     * Formula extracted from AppFolio per-unit calculations
     */
    const activeUnits = rentData.filter(unit => unit.status === 'Active');
    const totalRent = calculateTotalRent(rentData);
    
    if (activeUnits.length === 0) return 0;
    return totalRent / activeUnits.length;
}

// Advanced calculations based on AppFolio's rent roll logic
function calculateVacancyRate(rentData) {
    /**
     * Vacancy Rate: (Vacant Units / Total Units) * 100
     */
    const totalUnits = rentData.length;
    const vacantUnits = rentData.filter(unit => unit.status === 'Vacant').length;
    
    if (totalUnits === 0) return 0;
    return (vacantUnits / totalUnits) * 100;
}

function calculatePotentialRent(rentData) {
    /**
     * Gross Potential Rent: SUM(Rent for all units regardless of status)
     * What the property could earn at 100% occupancy
     */
    return rentData
        .reduce((sum, unit) => sum + parseFloat(unit.rent || 0), 0);
}

function calculateRentLoss(rentData) {
    /**
     * Rent Loss from Vacancy: Potential Rent - Actual Rent
     */
    const potentialRent = calculatePotentialRent(rentData);
    const actualRent = calculateTotalRent(rentData);
    return potentialRent - actualRent;
}

function calculateCollectionEfficiency(rentData) {
    /**
     * Collection Efficiency: (Collected Rent / Billed Rent) * 100
     * Accounts for past due amounts
     */
    const totalBilled = calculateTotalRent(rentData);
    const totalPastDue = calculateTotalPastDue(rentData);
    const collectedAmount = totalBilled - totalPastDue;
    
    if (totalBilled === 0) return 100;
    return (collectedAmount / totalBilled) * 100;
}

// Property-level analysis functions
function analyzeRentRollByProperty(rentData) {
    /**
     * Group and analyze rent roll data by property
     * Replicates AppFolio's property grouping functionality
     */
    const propertyGroups = {};
    
    rentData.forEach(unit => {
        const propertyName = unit.property || 'Unknown Property';
        
        if (!propertyGroups[propertyName]) {
            propertyGroups[propertyName] = {
                units: [],
                totalRent: 0,
                totalDeposits: 0,
                totalPastDue: 0,
                activeUnits: 0,
                totalUnits: 0
            };
        }
        
        const property = propertyGroups[propertyName];
        property.units.push(unit);
        property.totalUnits++;
        
        if (unit.status === 'Active') {
            property.activeUnits++;
            property.totalRent += parseFloat(unit.rent || 0);
        }
        
        property.totalDeposits += parseFloat(unit.deposit || 0);
        property.totalPastDue += parseFloat(unit.pastDue || 0);
    });
    
    // Calculate occupancy rate for each property
    Object.keys(propertyGroups).forEach(propertyName => {
        const property = propertyGroups[propertyName];
        property.occupancyRate = property.totalUnits > 0 ? 
            (property.activeUnits / property.totalUnits) * 100 : 0;
        property.averageRent = property.activeUnits > 0 ? 
            property.totalRent / property.activeUnits : 0;
    });
    
    return propertyGroups;
}

// Date and lease analysis functions
function analyzeLeaseExpirations(rentData) {
    /**
     * Analyze upcoming lease expirations
     * Replicates AppFolio's lease expiration tracking
     */
    const currentDate = new Date();
    const expirations = {
        next30Days: [],
        next60Days: [],
        next90Days: [],
        expired: []
    };
    
    rentData.forEach(unit => {
        if (unit.leaseTo && unit.status === 'Active') {
            const leaseEndDate = new Date(unit.leaseTo);
            const daysUntilExpiration = Math.ceil((leaseEndDate - currentDate) / (1000 * 60 * 60 * 24));
            
            if (daysUntilExpiration < 0) {
                expirations.expired.push(unit);
            } else if (daysUntilExpiration <= 30) {
                expirations.next30Days.push(unit);
            } else if (daysUntilExpiration <= 60) {
                expirations.next60Days.push(unit);
            } else if (daysUntilExpiration <= 90) {
                expirations.next90Days.push(unit);
            }
        }
    });
    
    return expirations;
}

// Utility functions for data validation and formatting
function validateRentRollData(rentData) {
    /**
     * Validate rent roll data integrity
     * Ensures calculations will be accurate
     */
    const errors = [];
    
    rentData.forEach((unit, index) => {
        if (!unit.unit) {
            errors.push(`Row ${index + 1}: Missing unit number`);
        }
        
        if (unit.rent && isNaN(parseFloat(unit.rent))) {
            errors.push(`Row ${index + 1}: Invalid rent amount`);
        }
        
        if (unit.deposit && isNaN(parseFloat(unit.deposit))) {
            errors.push(`Row ${index + 1}: Invalid deposit amount`);
        }
        
        if (unit.pastDue && isNaN(parseFloat(unit.pastDue))) {
            errors.push(`Row ${index + 1}: Invalid past due amount`);
        }
    });
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

function formatCurrency(amount) {
    /**
     * Format currency values consistently with AppFolio display
     */
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatPercentage(value, decimals = 1) {
    /**
     * Format percentage values consistently with AppFolio display
     */
    return `${value.toFixed(decimals)}%`;
}

// Export for use in other modules (if using module system)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateTotalRent,
        calculateTotalDeposits,
        calculateTotalPastDue,
        calculateOccupancyRate,
        calculateAverageRent,
        calculateVacancyRate,
        calculatePotentialRent,
        calculateRentLoss,
        calculateCollectionEfficiency,
        analyzeRentRollByProperty,
        analyzeLeaseExpirations,
        validateRentRollData,
        formatCurrency,
        formatPercentage
    };
}

// Global functions for browser use
window.RentRollCalculations = {
    calculateTotalRent,
    calculateTotalDeposits,
    calculateTotalPastDue,
    calculateOccupancyRate,
    calculateAverageRent,
    calculateVacancyRate,
    calculatePotentialRent,
    calculateRentLoss,
    calculateCollectionEfficiency,
    analyzeRentRollByProperty,
    analyzeLeaseExpirations,
    validateRentRollData,
    formatCurrency,
    formatPercentage
};

console.log('✅ AIVIIZN Rent Roll Calculations loaded successfully');
console.log('📊 Extracted from AppFolio: https://celticprop.appfolio.com/buffered_reports/rent_roll?customize=true');
