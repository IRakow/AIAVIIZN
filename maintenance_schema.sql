-- Unit Turns and Projects Supabase Schema
-- This file contains the table definitions needed for the Unit Turns and Projects pages

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Properties table (if not exists)
CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    property_type VARCHAR(100),
    units_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vendors table (if not exists) 
CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    vendor_type VARCHAR(100),
    specialty VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects table (enhanced version)
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    property_id UUID REFERENCES properties(id),
    status VARCHAR(50) NOT NULL DEFAULT 'planning',
    priority VARCHAR(50) DEFAULT 'medium',
    category VARCHAR(100),
    budget DECIMAL(10,2) DEFAULT 0,
    actuals DECIMAL(10,2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    target_completion_date DATE,
    manager VARCHAR(255),
    vendor_id UUID REFERENCES vendors(id),
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT projects_status_check CHECK (status IN ('planning', 'in-progress', 'on-hold', 'completed', 'cancelled')),
    CONSTRAINT projects_priority_check CHECK (priority IN ('low', 'medium', 'high', 'critical'))
);

-- Unit Turns table
CREATE TABLE IF NOT EXISTS unit_turns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id),
    unit VARCHAR(100) NOT NULL,
    move_out_date DATE NOT NULL,
    move_in_date DATE,
    target_date DATE,
    actual_completion_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'in-progress',
    reference_user VARCHAR(255),
    estimated_cost DECIMAL(10,2) DEFAULT 0,
    actual_cost DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    days_vacant INTEGER GENERATED ALWAYS AS (
        CASE 
            WHEN move_in_date IS NOT NULL THEN 
                EXTRACT(DAY FROM move_in_date - move_out_date)
            ELSE 
                EXTRACT(DAY FROM CURRENT_DATE - move_out_date)
        END
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unit_turns_status_check CHECK (status IN ('in-progress', 'ready', 'completed', 'on-hold'))
);

-- Unit Turn Tasks table (for the 7-category task system)
CREATE TABLE IF NOT EXISTS unit_turn_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_turn_id UUID NOT NULL REFERENCES unit_turns(id) ON DELETE CASCADE,
    task_category VARCHAR(50) NOT NULL,
    is_completed BOOLEAN DEFAULT false,
    assigned_to VARCHAR(255),
    vendor_id UUID REFERENCES vendors(id),
    scheduled_date DATE,
    completed_date DATE,
    estimated_cost DECIMAL(10,2) DEFAULT 0,
    actual_cost DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unit_turn_tasks_category_check CHECK (task_category IN (
        'maintenance', 'paint', 'appliances', 'floors', 'other', 'housekeeping', 'keys'
    )),
    
    -- Ensure only one task per category per unit turn
    UNIQUE(unit_turn_id, task_category)
);

-- Project Expenses table (for tracking project costs)
CREATE TABLE IF NOT EXISTS project_expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    expense_date DATE NOT NULL,
    description VARCHAR(500) NOT NULL,
    vendor VARCHAR(255),
    vendor_id UUID REFERENCES vendors(id),
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    receipt_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_unit_turns_property_id ON unit_turns(property_id);
CREATE INDEX IF NOT EXISTS idx_unit_turns_status ON unit_turns(status);
CREATE INDEX IF NOT EXISTS idx_unit_turns_move_out_date ON unit_turns(move_out_date);
CREATE INDEX IF NOT EXISTS idx_unit_turn_tasks_unit_turn_id ON unit_turn_tasks(unit_turn_id);
CREATE INDEX IF NOT EXISTS idx_unit_turn_tasks_category ON unit_turn_tasks(task_category);
CREATE INDEX IF NOT EXISTS idx_projects_property_id ON projects(property_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_start_date ON projects(start_date);
CREATE INDEX IF NOT EXISTS idx_project_expenses_project_id ON project_expenses(project_id);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables
DROP TRIGGER IF EXISTS update_properties_updated_at ON properties;
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_vendors_updated_at ON vendors;
CREATE TRIGGER update_vendors_updated_at BEFORE UPDATE ON vendors 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_unit_turns_updated_at ON unit_turns;
CREATE TRIGGER update_unit_turns_updated_at BEFORE UPDATE ON unit_turns 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_unit_turn_tasks_updated_at ON unit_turn_tasks;
CREATE TRIGGER update_unit_turn_tasks_updated_at BEFORE UPDATE ON unit_turn_tasks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_project_expenses_updated_at ON project_expenses;
CREATE TRIGGER update_project_expenses_updated_at BEFORE UPDATE ON project_expenses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing

-- Sample Properties
INSERT INTO properties (name, address, city, state, zip_code, property_type, units_count) 
VALUES 
    ('West Plaza', '123 West Plaza Dr', 'Phoenix', 'AZ', '85001', 'Apartment Complex', 45),
    ('Longmeadow Apartments', '456 Longmeadow Ave', 'Phoenix', 'AZ', '85002', 'Apartment Complex', 32),
    ('Brentwood Park', '789 Brentwood Pkwy', 'Phoenix', 'AZ', '85003', 'Apartment Complex', 28),
    ('Rock Ridge Ranch Apartments', '321 Rock Ridge Dr', 'Phoenix', 'AZ', '85004', 'Apartment Complex', 55),
    ('Blue Ridge Manor', '654 Blue Ridge Blvd', 'Phoenix', 'AZ', '85005', 'Apartment Complex', 38)
ON CONFLICT (name) DO NOTHING;

-- Sample Vendors
INSERT INTO vendors (name, contact_person, email, phone, vendor_type, specialty, is_active)
VALUES 
    ('ABC Construction', 'John Smith', 'john@abcconstruction.com', '(555) 123-4567', 'Contractor', 'General Construction', true),
    ('XYZ Roofing', 'Jane Doe', 'jane@xyzroofing.com', '(555) 234-5678', 'Contractor', 'Roofing', true),
    ('Quality Painting', 'Mike Wilson', 'mike@qualitypainting.com', '(555) 345-6789', 'Contractor', 'Painting', true),
    ('Pro HVAC Services', 'Sarah Johnson', 'sarah@prohvac.com', '(555) 456-7890', 'Contractor', 'HVAC', true),
    ('Elite Plumbing', 'Bob Anderson', 'bob@eliteplumbing.com', '(555) 567-8901', 'Contractor', 'Plumbing', true)
ON CONFLICT (name) DO NOTHING;

-- Sample Projects
INSERT INTO projects (name, description, property_id, status, priority, category, budget, actuals, start_date, end_date, manager)
SELECT 
    'Roof Replacement - Building A',
    'Complete roof replacement for Building A including new shingles and underlayment',
    p.id,
    'in-progress',
    'high',
    'capital-improvement',
    45000.00,
    32500.00,
    '2025-01-15',
    '2025-03-15',
    'John Smith'
FROM properties p WHERE p.name = 'West Plaza'
ON CONFLICT DO NOTHING;

INSERT INTO projects (name, description, property_id, status, priority, category, budget, actuals, start_date, end_date, manager)
SELECT 
    'Parking Lot Resurfacing',
    'Resurface main parking lot and repaint lines',
    p.id,
    'planning',
    'medium',
    'maintenance',
    28000.00,
    0.00,
    '2025-03-01',
    '2025-03-30',
    'Jane Doe'
FROM properties p WHERE p.name = 'Longmeadow Apartments'
ON CONFLICT DO NOTHING;

-- Sample Unit Turns
INSERT INTO unit_turns (property_id, unit, move_out_date, target_date, status, reference_user, estimated_cost, notes)
SELECT 
    p.id,
    '4231 C',
    '2021-05-31',
    '2021-06-10',
    'in-progress',
    NULL,
    2500.00,
    'Standard unit turn - tenant moved out on schedule'
FROM properties p WHERE p.name = 'West Plaza'
ON CONFLICT DO NOTHING;

INSERT INTO unit_turns (property_id, unit, move_out_date, target_date, status, reference_user, estimated_cost, notes)
SELECT 
    p.id,
    '4239 D',
    '2021-05-31',
    '2021-06-10',
    'in-progress',
    NULL,
    2200.00,
    'Needs paint and carpet cleaning'
FROM properties p WHERE p.name = 'West Plaza'
ON CONFLICT DO NOTHING;

-- Sample Unit Turn Tasks (for first unit turn)
WITH unit_turn_data AS (
    SELECT ut.id as unit_turn_id
    FROM unit_turns ut
    JOIN properties p ON ut.property_id = p.id
    WHERE p.name = 'West Plaza' AND ut.unit = '4231 C'
    LIMIT 1
)
INSERT INTO unit_turn_tasks (unit_turn_id, task_category, is_completed, estimated_cost)
SELECT 
    utd.unit_turn_id,
    category,
    false,
    cost
FROM unit_turn_data utd
CROSS JOIN (
    VALUES 
        ('maintenance', 400.00),
        ('paint', 300.00),
        ('appliances', 200.00),
        ('floors', 800.00),
        ('other', 100.00),
        ('housekeeping', 150.00),
        ('keys', 50.00)
) AS tasks(category, cost)
ON CONFLICT (unit_turn_id, task_category) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE unit_turns IS 'Tracks unit turnover process from move-out to move-in ready';
COMMENT ON TABLE unit_turn_tasks IS 'Tracks the 7 standard task categories for each unit turn';
COMMENT ON TABLE projects IS 'Tracks maintenance and capital improvement projects';
COMMENT ON TABLE project_expenses IS 'Tracks expenses and costs for each project';

COMMENT ON COLUMN unit_turns.days_vacant IS 'Calculated field showing days between move-out and move-in (or current date)';
COMMENT ON COLUMN unit_turn_tasks.task_category IS 'Standard categories: maintenance, paint, appliances, floors, other, housekeeping, keys';
