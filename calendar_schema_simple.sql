-- calendar_schema.sql
-- Supabase database schema for calendar events
-- Run this in your Supabase SQL editor to create the necessary tables

-- Create calendar_events table
CREATE TABLE IF NOT EXISTS calendar_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id TEXT NOT NULL,
    title TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('move_in', 'move_out', 'showing', 'maintenance', 'inspection', 'appointment')),
    start_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    end_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    all_day BOOLEAN DEFAULT FALSE,
    
    -- Property information
    property_id TEXT,
    property_name TEXT,
    unit_id TEXT,
    unit_number TEXT,
    
    -- Contact information
    tenant_id TEXT,
    tenant_name TEXT,
    tenant_email TEXT,
    tenant_phone TEXT,
    
    -- Vendor information (for maintenance)
    vendor_id TEXT,
    vendor_name TEXT,
    vendor_email TEXT,
    vendor_phone TEXT,
    
    -- Event details
    description TEXT,
    location TEXT,
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show', 'rescheduled')),
    
    -- Recurring event fields
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern TEXT CHECK (recurrence_pattern IN ('daily', 'weekly', 'monthly', 'yearly') OR recurrence_pattern IS NULL),
    recurrence_end_date DATE,
    parent_event_id UUID REFERENCES calendar_events(id) ON DELETE CASCADE,
    
    -- Reminder fields
    send_reminder BOOLEAN DEFAULT FALSE,
    reminder_minutes INTEGER DEFAULT 60,
    reminder_sent BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_by TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_calendar_events_company_id ON calendar_events(company_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_start_datetime ON calendar_events(start_datetime);
CREATE INDEX IF NOT EXISTS idx_calendar_events_event_type ON calendar_events(event_type);
CREATE INDEX IF NOT EXISTS idx_calendar_events_property_id ON calendar_events(property_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_unit_id ON calendar_events(unit_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_tenant_id ON calendar_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_vendor_id ON calendar_events(vendor_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_status ON calendar_events(status);

-- Create calendar_event_attendees table for multiple attendees
CREATE TABLE IF NOT EXISTS calendar_event_attendees (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    attendee_type TEXT NOT NULL CHECK (attendee_type IN ('tenant', 'owner', 'vendor', 'staff', 'other')),
    attendee_id TEXT,
    attendee_name TEXT NOT NULL,
    attendee_email TEXT,
    attendee_phone TEXT,
    response_status TEXT DEFAULT 'pending' CHECK (response_status IN ('pending', 'accepted', 'declined', 'tentative')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create calendar_event_attachments table for documents
CREATE TABLE IF NOT EXISTS calendar_event_attachments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_size INTEGER,
    file_type TEXT,
    uploaded_by TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create calendar_event_notes table for additional notes
CREATE TABLE IF NOT EXISTS calendar_event_notes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    note TEXT NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create calendar_event_conflicts table to track conflicts
CREATE TABLE IF NOT EXISTS calendar_event_conflicts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_id UUID NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    conflicting_event_id UUID NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    conflict_type TEXT CHECK (conflict_type IN ('time', 'resource', 'attendee')),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    UNIQUE(event_id, conflicting_event_id)
);

-- Row Level Security (RLS) Policies
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_event_attendees ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_event_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_event_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_event_conflicts ENABLE ROW LEVEL SECURITY;

-- Create policies for calendar_events with simple names
CREATE POLICY calendar_events_select_policy
    ON calendar_events
    FOR SELECT
    USING (true);  -- Temporarily allow all reads

CREATE POLICY calendar_events_insert_policy
    ON calendar_events
    FOR INSERT
    WITH CHECK (true);  -- Temporarily allow all inserts

CREATE POLICY calendar_events_update_policy
    ON calendar_events
    FOR UPDATE
    USING (true);  -- Temporarily allow all updates

CREATE POLICY calendar_events_delete_policy
    ON calendar_events
    FOR DELETE
    USING (true);  -- Temporarily allow all deletes

-- Create similar policies for related tables
CREATE POLICY calendar_event_attendees_policy
    ON calendar_event_attendees
    FOR ALL
    USING (true);  -- Temporarily allow all operations

CREATE POLICY calendar_event_attachments_policy
    ON calendar_event_attachments
    FOR ALL
    USING (true);  -- Temporarily allow all operations

CREATE POLICY calendar_event_notes_policy
    ON calendar_event_notes
    FOR ALL
    USING (true);  -- Temporarily allow all operations

CREATE POLICY calendar_event_conflicts_policy
    ON calendar_event_conflicts
    FOR ALL
    USING (true);  -- Temporarily allow all operations

-- Sample data for testing
INSERT INTO calendar_events (company_id, title, event_type, start_datetime, end_datetime, property_name, unit_number, tenant_name, status)
VALUES 
('demo-company', 'Move In: Unit 3745', 'move_in', NOW() + INTERVAL '1 day', NOW() + INTERVAL '1 day' + INTERVAL '2 hours', 'Rock Ridge Ranch', '3745', 'John Smith', 'scheduled'),
('demo-company', 'Showing: Unit 4407', 'showing', NOW() + INTERVAL '2 days', NOW() + INTERVAL '2 days' + INTERVAL '1 hour', 'Sunset Apartments', '4407', 'Jane Doe', 'scheduled'),
('demo-company', 'HVAC Maintenance', 'maintenance', NOW() + INTERVAL '3 days', NOW() + INTERVAL '3 days' + INTERVAL '2 hours', 'Building A', NULL, NULL, 'scheduled'),
('demo-company', 'Monthly Inspection', 'inspection', NOW() + INTERVAL '4 days', NOW() + INTERVAL '4 days' + INTERVAL '2 hours', 'Downtown Properties', '201', NULL, 'scheduled'),
('demo-company', 'Owner Meeting', 'appointment', NOW() + INTERVAL '5 days', NOW() + INTERVAL '5 days' + INTERVAL '1 hour', 'Main Office', NULL, 'Property Owner', 'scheduled');
