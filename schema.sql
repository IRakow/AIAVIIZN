-- Supabase Database Schema for Property Management System
-- Run these SQL commands in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Properties table
CREATE TABLE properties (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip VARCHAR(20) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'Multi-Family', 'Single-Family'
    units_count INTEGER DEFAULT 0,
    year_built INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Units table
CREATE TABLE units (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    unit_number VARCHAR(50) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms DECIMAL(3,1) NOT NULL,
    square_feet INTEGER,
    rent DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'vacant', -- 'vacant', 'occupied', 'maintenance'
    available_date DATE,
    days_vacant INTEGER DEFAULT 0,
    photos_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tenants table
CREATE TABLE tenants (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    ssn_last_four VARCHAR(4),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leases table
CREATE TABLE leases (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    rent_amount DECIMAL(10,2) NOT NULL,
    security_deposit DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'pending', 'executed', 'expired'
    lease_type VARCHAR(50) DEFAULT 'fixed', -- 'fixed', 'month-to-month'
    generated_date TIMESTAMPTZ DEFAULT NOW(),
    signed_date TIMESTAMPTZ,
    countersigned_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Guest Cards (Leads) table
CREATE TABLE guest_cards (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    unit_id UUID REFERENCES units(id) ON DELETE SET NULL,
    interested_in TEXT,
    source VARCHAR(100), -- 'Zillow', 'Apartments.com', 'Rent.', 'Zumper', 'call'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'inactive', 'waitlisted'
    latest_interest_date DATE,
    last_activity VARCHAR(255),
    last_activity_date TIMESTAMPTZ,
    assigned_to VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rental Applications table
CREATE TABLE rental_applications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    guest_card_id UUID REFERENCES guest_cards(id) ON DELETE SET NULL,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE,
    applicant_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    application_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'under_review', 'approved', 'denied', 'withdrawn'
    credit_score INTEGER,
    income_monthly DECIMAL(10,2),
    employment_status VARCHAR(100),
    employer_name VARCHAR(255),
    previous_landlord_name VARCHAR(255),
    previous_landlord_phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Move Ins table
CREATE TABLE move_ins (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    lease_id UUID REFERENCES leases(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    move_in_date DATE NOT NULL,
    lease_status VARCHAR(50),
    portal_status VARCHAR(50) DEFAULT 'inactive',
    balance DECIMAL(10,2) DEFAULT 0,
    insurance_status VARCHAR(50) DEFAULT 'not_covered', -- 'covered', 'not_covered', 'pending'
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Renewals table
CREATE TABLE renewals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    lease_id UUID REFERENCES leases(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE,
    current_rent DECIMAL(10,2) NOT NULL,
    proposed_rent DECIMAL(10,2),
    expiration_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'eligible', -- 'eligible', 'pending', 'sent', 'signed', 'declined'
    offer_sent_date DATE,
    response_date DATE,
    new_lease_id UUID REFERENCES leases(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alerts table
CREATE TABLE alerts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    link VARCHAR(500),
    active BOOLEAN DEFAULT TRUE,
    dismissible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Metrics table for tracking KPIs
CREATE TABLE metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    occupancy_rate DECIMAL(5,2),
    total_revenue DECIMAL(12,2),
    total_expenses DECIMAL(12,2),
    new_leases_count INTEGER DEFAULT 0,
    renewals_count INTEGER DEFAULT 0,
    vacancies_count INTEGER DEFAULT 0,
    average_days_vacant INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Signals/Notifications table
CREATE TABLE signals (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    signal_type VARCHAR(100) NOT NULL, -- 'high_vacancy', 'price_alert', 'high_demand', etc.
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    severity VARCHAR(50) DEFAULT 'info', -- 'info', 'warning', 'critical'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    action_required VARCHAR(255),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_units_property_id ON units(property_id);
CREATE INDEX idx_units_status ON units(status);
CREATE INDEX idx_leases_unit_id ON leases(unit_id);
CREATE INDEX idx_leases_tenant_id ON leases(tenant_id);
CREATE INDEX idx_leases_status ON leases(status);
CREATE INDEX idx_guest_cards_status ON guest_cards(status);
CREATE INDEX idx_guest_cards_property_id ON guest_cards(property_id);
CREATE INDEX idx_rental_applications_status ON rental_applications(status);
CREATE INDEX idx_move_ins_move_in_date ON move_ins(move_in_date);
CREATE INDEX idx_renewals_expiration_date ON renewals(expiration_date);

-- Insert sample data
INSERT INTO properties (name, address, city, state, zip, type, units_count) VALUES
('(BARR) Rock Ridge Ranch Apartments', '10561 Cypress Ave', 'Kansas City', 'MO', '64137', 'Multi-Family', 75),
('Gene Field Apts / DW Gene Field LLC', '3515 Gene Field Rd', 'St. Joseph', 'MO', '64506', 'Multi-Family', 12),
('Campbell Apartments', '3403 Campbell St', 'Kansas City', 'MO', '64109', 'Multi-Family', 8),
('Blue Ridge Manor', '3809 Blue Ridge Blvd', 'Kansas City', 'MO', '64133', 'Multi-Family', 6),
('3825 Baltimore', '3825 Baltimore Ave', 'Kansas City', 'MO', '64111', 'Multi-Family', 7);

-- Insert sample units
INSERT INTO units (property_id, unit_number, bedrooms, bathrooms, square_feet, rent, status, days_vacant) 
SELECT 
    p.id,
    '10-02',
    1,
    1,
    731,
    546,
    'vacant',
    1052
FROM properties p WHERE p.name LIKE 'Gene Field%' LIMIT 1;

INSERT INTO units (property_id, unit_number, bedrooms, bathrooms, square_feet, rent, status, days_vacant) 
SELECT 
    p.id,
    '10-04',
    1,
    1,
    731,
    546,
    'vacant',
    896
FROM properties p WHERE p.name LIKE 'Gene Field%' LIMIT 1;

-- Insert sample tenants
INSERT INTO tenants (first_name, last_name, email, phone) VALUES
('Samuel', 'Sainge', 'samuel.sainge@email.com', '555-0101'),
('Telia', 'Bell', 'telia.bell@email.com', '555-0102'),
('Eric', 'Carlson', 'eric.carlson@email.com', '555-0103'),
('Rachel', 'Stivers', 'rachel.stivers@email.com', '555-0104'),
('Julianna', 'Yoder', 'julianna.yoder@email.com', '555-0105');

-- Insert sample guest cards
INSERT INTO guest_cards (name, email, phone, interested_in, source, status, latest_interest_date, last_activity, last_activity_date) VALUES
('Mikayla Clark', 'mikayla.clark@email.com', '555-0201', 'Pearl St. Apts / GBA1947 LLC', 'Zillow Rental Network', 'active', '2025-08-06', 'Pre-qualification Form Submitted', '2025-08-06'),
('Collin Thomas', 'collin.thomas@email.com', '555-0202', 'Charlotte Park Apartments', 'Zillow Rental Network', 'active', '2025-08-06', 'Auto-Response Email Sent', '2025-08-06'),
('Felesha Washington', 'felesha.washington@email.com', '555-0203', 'Pearl St. Apts / GBA1947 LLC - 2807-3', 'Zumper', 'active', '2025-08-06', 'Auto-Response Email Sent', '2025-08-06'),
('Claudia Acosta', 'claudia.acosta@email.com', '555-0204', 'Blue Ridge Manor', 'Apartments.com', 'active', '2025-08-06', 'Pre-qualification Form Submitted', '2025-08-06');

-- Insert sample alert
INSERT INTO alerts (type, title, message, link, active) VALUES
('info', 'Financial Diagnostics Reminder', 'Have you checked your Financial Diagnostics Page recently?', '/financial-diagnostics', true);

-- Create views for common queries
CREATE VIEW vacant_units_summary AS
SELECT 
    p.name as property_name,
    u.unit_number,
    u.bedrooms,
    u.bathrooms,
    u.square_feet,
    u.rent,
    u.days_vacant,
    u.available_date,
    CONCAT(p.address, ', ', p.city, ', ', p.state, ' ', p.zip) as full_address
FROM units u
JOIN properties p ON u.property_id = p.id
WHERE u.status = 'vacant'
ORDER BY u.days_vacant DESC;

CREATE VIEW upcoming_renewals AS
SELECT 
    l.id as lease_id,
    t.first_name || ' ' || t.last_name as tenant_name,
    p.name as property_name,
    u.unit_number,
    l.end_date as expiration_date,
    u.rent as current_rent,
    l.status as lease_status
FROM leases l
JOIN tenants t ON l.tenant_id = t.id
JOIN units u ON l.unit_id = u.id
JOIN properties p ON u.property_id = p.id
WHERE l.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
ORDER BY l.end_date;