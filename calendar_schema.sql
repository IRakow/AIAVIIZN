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

-- Create policies for calendar_events
CREATE POLICY "Users can view their company calendar events"
    ON calendar_events
    FOR SELECT
    USING (auth.jwt() ->> 'company_id' = company_id);

CREATE POLICY "Users can create calendar events for their company"
    ON calendar_events
    FOR INSERT
    WITH CHECK (auth.jwt() ->> 'company_id' = company_id);

CREATE POLICY "Users can update their company calendar events"
    ON calendar_events
    FOR UPDATE
    USING (auth.jwt() ->> 'company_id' = company_id);

CREATE POLICY "Users can delete their company calendar events"
    ON calendar_events
    FOR DELETE
    USING (auth.jwt() ->> 'company_id' = company_id);

-- Create similar policies for related tables
CREATE POLICY "Users can view attendees for their company events"
    ON calendar_event_attendees
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM calendar_events
            WHERE calendar_events.id = calendar_event_attendees.event_id
            AND calendar_events.company_id = auth.jwt() ->> 'company_id'
        )
    );

CREATE POLICY "Users can manage attendees for their company events"
    ON calendar_event_attendees
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM calendar_events
            WHERE calendar_events.id = calendar_event_attendees.event_id
            AND calendar_events.company_id = auth.jwt() ->> 'company_id'
        )
    );

-- Function to check for event conflicts
CREATE OR REPLACE FUNCTION check_event_conflicts(
    p_event_id UUID,
    p_start_datetime TIMESTAMP WITH TIME ZONE,
    p_end_datetime TIMESTAMP WITH TIME ZONE,
    p_unit_id TEXT,
    p_vendor_id TEXT
)
RETURNS TABLE (
    conflicting_event_id UUID,
    conflict_type TEXT,
    title TEXT,
    start_datetime TIMESTAMP WITH TIME ZONE,
    end_datetime TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.id AS conflicting_event_id,
        CASE 
            WHEN ce.unit_id = p_unit_id THEN 'unit'::TEXT
            WHEN ce.vendor_id = p_vendor_id THEN 'vendor'::TEXT
            ELSE 'time'::TEXT
        END AS conflict_type,
        ce.title,
        ce.start_datetime,
        ce.end_datetime
    FROM calendar_events ce
    WHERE ce.id != COALESCE(p_event_id, '00000000-0000-0000-0000-000000000000'::UUID)
        AND ce.status NOT IN ('cancelled', 'completed')
        AND (
            (p_unit_id IS NOT NULL AND ce.unit_id = p_unit_id)
            OR (p_vendor_id IS NOT NULL AND ce.vendor_id = p_vendor_id)
        )
        AND ce.start_datetime < p_end_datetime
        AND ce.end_datetime > p_start_datetime;
END;
$$;

-- Function to create recurring events
CREATE OR REPLACE FUNCTION create_recurring_events(
    p_event_id UUID,
    p_pattern TEXT,
    p_end_date DATE
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_event RECORD;
    v_current_date TIMESTAMP WITH TIME ZONE;
    v_interval INTERVAL;
    v_count INTEGER := 0;
BEGIN
    -- Get the original event
    SELECT * INTO v_event FROM calendar_events WHERE id = p_event_id;
    
    IF v_event IS NULL THEN
        RAISE EXCEPTION 'Event not found';
    END IF;
    
    -- Set the interval based on pattern
    CASE p_pattern
        WHEN 'daily' THEN v_interval := INTERVAL '1 day';
        WHEN 'weekly' THEN v_interval := INTERVAL '1 week';
        WHEN 'monthly' THEN v_interval := INTERVAL '1 month';
        WHEN 'yearly' THEN v_interval := INTERVAL '1 year';
        ELSE RAISE EXCEPTION 'Invalid recurrence pattern';
    END CASE;
    
    -- Start from the next occurrence
    v_current_date := v_event.start_datetime + v_interval;
    
    -- Create recurring events
    WHILE v_current_date <= p_end_date::TIMESTAMP WITH TIME ZONE LOOP
        INSERT INTO calendar_events (
            company_id, title, event_type, start_datetime, end_datetime,
            all_day, property_id, property_name, unit_id, unit_number,
            tenant_id, tenant_name, tenant_email, tenant_phone,
            vendor_id, vendor_name, vendor_email, vendor_phone,
            description, location, status, is_recurring, recurrence_pattern,
            parent_event_id, send_reminder, reminder_minutes,
            created_by, created_at
        )
        VALUES (
            v_event.company_id, v_event.title, v_event.event_type,
            v_current_date,
            v_current_date + (v_event.end_datetime - v_event.start_datetime),
            v_event.all_day, v_event.property_id, v_event.property_name,
            v_event.unit_id, v_event.unit_number,
            v_event.tenant_id, v_event.tenant_name, v_event.tenant_email, v_event.tenant_phone,
            v_event.vendor_id, v_event.vendor_name, v_event.vendor_email, v_event.vendor_phone,
            v_event.description, v_event.location, v_event.status,
            TRUE, p_pattern, p_event_id,
            v_event.send_reminder, v_event.reminder_minutes,
            v_event.created_by, NOW()
        );
        
        v_count := v_count + 1;
        v_current_date := v_current_date + v_interval;
    END LOOP;
    
    -- Update the original event
    UPDATE calendar_events
    SET is_recurring = TRUE,
        recurrence_pattern = p_pattern,
        recurrence_end_date = p_end_date
    WHERE id = p_event_id;
    
    RETURN v_count;
END;
$$;

-- Create view for upcoming events
CREATE OR REPLACE VIEW upcoming_events AS
SELECT 
    ce.*,
    CASE 
        WHEN ce.start_datetime::DATE = CURRENT_DATE THEN 'Today'
        WHEN ce.start_datetime::DATE = CURRENT_DATE + INTERVAL '1 day' THEN 'Tomorrow'
        WHEN ce.start_datetime::DATE < CURRENT_DATE + INTERVAL '7 days' THEN 'This Week'
        WHEN ce.start_datetime::DATE < CURRENT_DATE + INTERVAL '30 days' THEN 'This Month'
        ELSE 'Later'
    END AS time_category
FROM calendar_events ce
WHERE ce.start_datetime >= CURRENT_TIMESTAMP
    AND ce.status NOT IN ('cancelled', 'completed')
ORDER BY ce.start_datetime;

-- Create view for event statistics
CREATE OR REPLACE VIEW calendar_statistics AS
SELECT 
    company_id,
    COUNT(*) FILTER (WHERE start_datetime >= CURRENT_DATE AND start_datetime < CURRENT_DATE + INTERVAL '1 day') AS events_today,
    COUNT(*) FILTER (WHERE start_datetime >= CURRENT_DATE AND start_datetime < CURRENT_DATE + INTERVAL '7 days') AS events_this_week,
    COUNT(*) FILTER (WHERE start_datetime >= CURRENT_DATE AND start_datetime < CURRENT_DATE + INTERVAL '30 days') AS events_this_month,
    COUNT(*) FILTER (WHERE event_type = 'move_in' AND start_datetime >= CURRENT_DATE AND start_datetime < CURRENT_DATE + INTERVAL '30 days') AS move_ins_this_month,
    COUNT(*) FILTER (WHERE event_type = 'move_out' AND start_datetime >= CURRENT_DATE AND start_datetime < CURRENT_DATE + INTERVAL '30 days') AS move_outs_this_month,
    COUNT(*) FILTER (WHERE event_type = 'showing' AND start_datetime >= CURRENT_DATE AND start_datetime < CURRENT_DATE + INTERVAL '7 days') AS showings_this_week,
    COUNT(*) FILTER (WHERE event_type = 'maintenance' AND status = 'scheduled') AS pending_maintenance,
    COUNT(*) FILTER (WHERE event_type = 'inspection' AND start_datetime >= CURRENT_DATE AND start_datetime < CURRENT_DATE + INTERVAL '30 days') AS upcoming_inspections
FROM calendar_events
WHERE status NOT IN ('cancelled')
GROUP BY company_id;

-- Sample data for testing (uncomment to insert sample data)
/*
INSERT INTO calendar_events (company_id, title, event_type, start_datetime, end_datetime, property_name, unit_number, tenant_name, status)
VALUES 
('demo-company', 'Move In: Unit 3745', 'move_in', '2025-08-10 10:00:00', '2025-08-10 12:00:00', 'Rock Ridge Ranch', '3745', 'John Smith', 'scheduled'),
('demo-company', 'Showing: Unit 4407', 'showing', '2025-08-10 14:00:00', '2025-08-10 15:00:00', 'Sunset Apartments', '4407', 'Jane Doe', 'scheduled'),
('demo-company', 'HVAC Maintenance', 'maintenance', '2025-08-11 09:00:00', '2025-08-11 11:00:00', 'Building A', NULL, NULL, 'scheduled'),
('demo-company', 'Monthly Inspection', 'inspection', '2025-08-12 10:00:00', '2025-08-12 12:00:00', 'Downtown Properties', '201', NULL, 'scheduled'),
('demo-company', 'Owner Meeting', 'appointment', '2025-08-13 15:00:00', '2025-08-13 16:00:00', 'Main Office', NULL, 'Property Owner', 'scheduled');
*/
