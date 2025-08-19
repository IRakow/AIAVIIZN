-- AIVIIZN Maintenance System Database Schema
-- Run this in your Supabase SQL Editor

-- Create maintenance system tables for AIVIIZN

-- Properties table (for reference)
CREATE TABLE IF NOT EXISTS properties (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    unit_count INTEGER DEFAULT 0,
    property_type VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Units table
CREATE TABLE IF NOT EXISTS units (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    unit_number VARCHAR(50) NOT NULL,
    tenant_name VARCHAR(255),
    tenant_email VARCHAR(255),
    tenant_phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'occupied', -- occupied, vacant, maintenance
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(property_id, unit_number)
);

-- Vendors/Staff table
CREATE TABLE IF NOT EXISTS vendors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100), -- vendor, staff, contractor
    specialty VARCHAR(255), -- plumbing, electrical, hvac, etc.
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Work Orders table
CREATE TABLE IF NOT EXISTS work_orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    work_order_number VARCHAR(50) UNIQUE NOT NULL,
    property_id UUID REFERENCES properties(id),
    unit_id UUID REFERENCES units(id),
    request_type VARCHAR(100) NOT NULL, -- resident, internal, unit-turn, emergency
    category VARCHAR(100) NOT NULL, -- plumbing, electrical, hvac, etc.
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, emergency
    status VARCHAR(50) DEFAULT 'new', -- new, assigned, in-progress, work-done, closed
    title VARCHAR(255),
    description TEXT NOT NULL,
    vendor_id UUID REFERENCES vendors(id),
    assigned_to VARCHAR(255),
    scheduled_date DATE,
    scheduled_time TIME,
    completed_date TIMESTAMPTZ,
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    entry_permission BOOLEAN DEFAULT false,
    notify_tenant BOOLEAN DEFAULT false,
    allow_key_access BOOLEAN DEFAULT false,
    entry_instructions TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Work Order Photos table
CREATE TABLE IF NOT EXISTS work_order_photos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    work_order_id UUID REFERENCES work_orders(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recurring Work Order Templates table
CREATE TABLE IF NOT EXISTS recurring_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    frequency VARCHAR(50) NOT NULL, -- daily, weekly, monthly, quarterly, annually
    interval_value INTEGER DEFAULT 1, -- every X periods
    schedule_details JSONB, -- day of week, day of month, etc.
    category VARCHAR(100) NOT NULL,
    priority VARCHAR(50) DEFAULT 'medium',
    description TEXT NOT NULL,
    vendor_id UUID REFERENCES vendors(id),
    auto_assign BOOLEAN DEFAULT false,
    notify_tenants BOOLEAN DEFAULT false,
    require_entry_permission BOOLEAN DEFAULT false,
    special_instructions TEXT,
    status VARCHAR(50) DEFAULT 'active', -- active, paused, draft
    next_generation_date DATE,
    last_generated_date DATE,
    generation_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Template Properties (many-to-many relationship)
CREATE TABLE IF NOT EXISTS template_properties (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    template_id UUID REFERENCES recurring_templates(id) ON DELETE CASCADE,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    UNIQUE(template_id, property_id)
);

-- Inspections table
CREATE TABLE IF NOT EXISTS inspections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    inspection_number VARCHAR(50) UNIQUE NOT NULL,
    property_id UUID REFERENCES properties(id),
    unit_id UUID REFERENCES units(id),
    inspection_type VARCHAR(100) NOT NULL, -- move-in, move-out, routine, annual, maintenance, safety
    template_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in-progress, completed, cancelled
    inspector_name VARCHAR(255) NOT NULL,
    inspector_type VARCHAR(100), -- staff, vendor
    scheduled_date DATE NOT NULL,
    scheduled_time TIME,
    completed_date TIMESTAMPTZ,
    purpose TEXT,
    access_instructions TEXT,
    notify_tenant BOOLEAN DEFAULT false,
    require_permission BOOLEAN DEFAULT false,
    photo_documentation BOOLEAN DEFAULT true,
    auto_create_work_orders BOOLEAN DEFAULT false,
    overall_rating VARCHAR(50), -- excellent, good, fair, poor
    inspector_notes TEXT,
    items_passed INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    work_orders_created INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inspection Checklist Items table
CREATE TABLE IF NOT EXISTS inspection_checklist_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    inspection_id UUID REFERENCES inspections(id) ON DELETE CASCADE,
    section VARCHAR(100) NOT NULL, -- kitchen, bathroom, living, hvac, etc.
    item_title VARCHAR(255) NOT NULL,
    item_description TEXT,
    status VARCHAR(50), -- passed, failed, n/a
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inspection Photos table
CREATE TABLE IF NOT EXISTS inspection_photos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    inspection_id UUID REFERENCES inspections(id) ON DELETE CASCADE,
    checklist_item_id UUID REFERENCES inspection_checklist_items(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_work_orders_property_id ON work_orders(property_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_created_at ON work_orders(created_at);
CREATE INDEX IF NOT EXISTS idx_work_orders_number ON work_orders(work_order_number);

CREATE INDEX IF NOT EXISTS idx_units_property_id ON units(property_id);
CREATE INDEX IF NOT EXISTS idx_units_status ON units(status);

CREATE INDEX IF NOT EXISTS idx_inspections_property_id ON inspections(property_id);
CREATE INDEX IF NOT EXISTS idx_inspections_status ON inspections(status);
CREATE INDEX IF NOT EXISTS idx_inspections_scheduled_date ON inspections(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_inspections_number ON inspections(inspection_number);

CREATE INDEX IF NOT EXISTS idx_recurring_templates_status ON recurring_templates(status);
CREATE INDEX IF NOT EXISTS idx_recurring_templates_next_generation ON recurring_templates(next_generation_date);

-- Create auto-increment functions for work order and inspection numbers
CREATE OR REPLACE FUNCTION generate_work_order_number() RETURNS TRIGGER AS $$
BEGIN
    NEW.work_order_number := 'WO-' || EXTRACT(YEAR FROM NOW())::TEXT || '-' || 
                              LPAD(nextval('work_order_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_inspection_number() RETURNS TRIGGER AS $$
BEGIN
    NEW.inspection_number := 'INS-' || EXTRACT(YEAR FROM NOW())::TEXT || '-' || 
                             LPAD(nextval('inspection_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequences for numbering
CREATE SEQUENCE IF NOT EXISTS work_order_seq START 1;
CREATE SEQUENCE IF NOT EXISTS inspection_seq START 1;

-- Create triggers
DROP TRIGGER IF EXISTS set_work_order_number ON work_orders;
CREATE TRIGGER set_work_order_number 
    BEFORE INSERT ON work_orders 
    FOR EACH ROW 
    EXECUTE FUNCTION generate_work_order_number();

DROP TRIGGER IF EXISTS set_inspection_number ON inspections;
CREATE TRIGGER set_inspection_number 
    BEFORE INSERT ON inspections 
    FOR EACH ROW 
    EXECUTE FUNCTION generate_inspection_number();

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_units_updated_at BEFORE UPDATE ON units FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vendors_updated_at BEFORE UPDATE ON vendors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_work_orders_updated_at BEFORE UPDATE ON work_orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_recurring_templates_updated_at BEFORE UPDATE ON recurring_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inspections_updated_at BEFORE UPDATE ON inspections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
INSERT INTO properties (name, address, unit_count, property_type) VALUES
('West Plaza', '123 West Plaza Ave, Phoenix, AZ', 45, 'apartment'),
('Longmeadow Apartments', '456 Longmeadow Dr, Phoenix, AZ', 32, 'apartment'),
('Norclay Apartments', '789 Norclay St, Phoenix, AZ', 28, 'apartment'),
('Brentwood Park', '321 Brentwood Blvd, Phoenix, AZ', 67, 'apartment'),
('Randall Court Ventures', '654 Randall Ct, Phoenix, AZ', 22, 'apartment')
ON CONFLICT DO NOTHING;

INSERT INTO vendors (name, type, specialty, contact_email, contact_phone, is_active) VALUES
('John Smith', 'staff', 'maintenance', 'john.smith@aiviizn.com', '(555) 123-4567', true),
('Sarah Johnson', 'staff', 'maintenance', 'sarah.johnson@aiviizn.com', '(555) 234-5678', true),
('Mike Davis', 'staff', 'inspector', 'mike.davis@aiviizn.com', '(555) 345-6789', true),
('ABC Plumbing', 'vendor', 'plumbing', 'contact@abcplumbing.com', '(555) 456-7890', true),
('XYZ Electric', 'vendor', 'electrical', 'service@xyzelectric.com', '(555) 567-8901', true),
('HVAC Pros', 'vendor', 'hvac', 'info@hvacpros.com', '(555) 678-9012', true),
('Quality Painting', 'vendor', 'painting', 'paint@qualitypainting.com', '(555) 789-0123', true),
('Elite Cleaning Service', 'vendor', 'cleaning', 'clean@elitecleaning.com', '(555) 890-1234', true),
('ABC Inspection Services', 'vendor', 'inspection', 'inspect@abcinspections.com', '(555) 901-2345', true),
('Quality Landscaping', 'vendor', 'landscaping', 'green@qualitylandscaping.com', '(555) 012-3456', true)
ON CONFLICT DO NOTHING;

-- Create some sample units for each property
INSERT INTO units (property_id, unit_number, tenant_name, tenant_email, status)
SELECT 
    p.id,
    CASE 
        WHEN p.name = 'West Plaza' THEN UNNEST(ARRAY['1705', '1707', '1201', '1202', '1203'])
        WHEN p.name = 'Longmeadow Apartments' THEN UNNEST(ARRAY['19A', '19B', '20A', '20B', '21A'])
        WHEN p.name = 'Norclay Apartments' THEN UNNEST(ARRAY['4655-1', '4655-2', '4656-1', '4656-2', '4657-1'])
        WHEN p.name = 'Brentwood Park' THEN UNNEST(ARRAY['3617-01', '3605-04', '3618-01', '3619-01', '3620-01'])
        WHEN p.name = 'Randall Court Ventures' THEN UNNEST(ARRAY['6724-9', '6724-10', '6725-1', '6725-2', '6726-1'])
    END,
    CASE 
        WHEN p.name = 'West Plaza' THEN UNNEST(ARRAY['Yarn Social, LLC', 'Tech Startup Inc', 'Smith Family', 'Johnson Enterprises', 'Davis Holdings'])
        WHEN p.name = 'Longmeadow Apartments' THEN UNNEST(ARRAY['Larry Davis', 'Maria Rodriguez', 'Kevin Chen', 'Jennifer Wilson', 'Robert Taylor'])
        WHEN p.name = 'Norclay Apartments' THEN UNNEST(ARRAY['Amy L. Lutgen', 'Michael Brown', 'Sarah White', 'David Miller', 'Lisa Anderson'])
        WHEN p.name = 'Brentwood Park' THEN UNNEST(ARRAY['Vacant', 'Vacant', 'Thompson Family', 'Garcia Household', 'Williams Estate'])
        WHEN p.name = 'Randall Court Ventures' THEN UNNEST(ARRAY['Kayeson O. Slayden', 'Martinez Family', 'Jackson Residence', 'Lee Household', 'Moore Family'])
    END,
    CASE 
        WHEN p.name = 'West Plaza' THEN UNNEST(ARRAY['contact@yarnsocial.com', 'info@techstartup.com', 'smith.family@email.com', 'johnson.ent@email.com', 'davis.holdings@email.com'])
        ELSE UNNEST(ARRAY['tenant1@email.com', 'tenant2@email.com', 'tenant3@email.com', 'tenant4@email.com', 'tenant5@email.com'])
    END,
    CASE 
        WHEN p.name = 'Brentwood Park' AND UNNEST(ARRAY['3617-01', '3605-04', '3618-01', '3619-01', '3620-01']) IN ('3617-01', '3605-04') THEN 'vacant'
        ELSE 'occupied'
    END
FROM properties p
ON CONFLICT DO NOTHING;

-- Enable Row Level Security (but no authentication required - open access)
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE units ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_order_photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE recurring_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspections ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspection_checklist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspection_photos ENABLE ROW LEVEL SECURITY;

-- Create policies for anonymous access (no authentication required)
CREATE POLICY "Allow anonymous read access on properties" ON properties FOR SELECT USING (true);
CREATE POLICY "Allow anonymous read access on units" ON units FOR SELECT USING (true);
CREATE POLICY "Allow anonymous read access on vendors" ON vendors FOR SELECT USING (true);
CREATE POLICY "Allow anonymous full access on work_orders" ON work_orders FOR ALL USING (true);
CREATE POLICY "Allow anonymous full access on work_order_photos" ON work_order_photos FOR ALL USING (true);
CREATE POLICY "Allow anonymous full access on recurring_templates" ON recurring_templates FOR ALL USING (true);
CREATE POLICY "Allow anonymous full access on template_properties" ON template_properties FOR ALL USING (true);
CREATE POLICY "Allow anonymous full access on inspections" ON inspections FOR ALL USING (true);
CREATE POLICY "Allow anonymous full access on inspection_checklist_items" ON inspection_checklist_items FOR ALL USING (true);
CREATE POLICY "Allow anonymous full access on inspection_photos" ON inspection_photos FOR ALL USING (true);

-- Create views for easier data access
CREATE OR REPLACE VIEW work_orders_with_details AS
SELECT 
    wo.*,
    p.name as property_name,
    u.unit_number,
    u.tenant_name,
    v.name as vendor_name,
    v.type as vendor_type
FROM work_orders wo
LEFT JOIN properties p ON wo.property_id = p.id
LEFT JOIN units u ON wo.unit_id = u.id
LEFT JOIN vendors v ON wo.vendor_id = v.id;

CREATE OR REPLACE VIEW inspections_with_details AS
SELECT 
    i.*,
    p.name as property_name,
    u.unit_number,
    u.tenant_name
FROM inspections i
LEFT JOIN properties p ON i.property_id = p.id
LEFT JOIN units u ON i.unit_id = u.id;

CREATE OR REPLACE VIEW recurring_templates_with_details AS
SELECT 
    rt.*,
    COUNT(tp.property_id) as property_count,
    ARRAY_AGG(p.name) FILTER (WHERE p.name IS NOT NULL) as property_names
FROM recurring_templates rt
LEFT JOIN template_properties tp ON rt.id = tp.template_id
LEFT JOIN properties p ON tp.property_id = p.id
GROUP BY rt.id;

-- Grant permissions for anonymous access
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT INSERT, UPDATE, DELETE ON work_orders, work_order_photos, recurring_templates, template_properties, inspections, inspection_checklist_items, inspection_photos TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;