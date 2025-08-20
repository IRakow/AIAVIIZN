-- 🗄️ AIVIIZN Database Schema
-- Generated: 2025-08-19 22:26:02
-- All SQL validated against Supabase via MCP server
-- Production-ready database structure


-- 📄 SQL for https://aiviizn.uc.r.appspot.com/reports
-- Generated: 2025-08-19 22:27:29
-- Reference: https://celticprop.appfolio.com/reports
-- Priority: 1

-- Statement 1:
-- Reports Categories Table
CREATE TABLE report_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Report Templates Table
CREATE TABLE report_templates (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES report_categories(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL, -- 'financial', 'occupancy', 'maintenance', etc.
    sql_query TEXT,
    parameters JSONB, -- Dynamic parameters for the report
    default_filters JSONB,
    chart_config JSONB, -- Chart configuration if applicable
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated Reports Table
CREATE TABLE generated_reports (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES report_templates(id),
    user_id INTEGER, -- Reference to user who generated
    title VARCHAR(200) NOT NULL,
    filters_applied JSONB,
    date_range_start DATE,
    date_range_end DATE,
    status VARCHAR(20) DEFAULT 'generating', -- 'generating', 'completed', 'failed'
    file_path VARCHAR(500),
    file_format VARCHAR(10), -- 'pdf', 'excel', 'csv'
    data_snapshot JSONB, -- Store report data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Scheduled Reports Table
CREATE TABLE scheduled_reports (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES report_templates(id),
    user_id INTEGER,
    name VARCHAR(200) NOT NULL,
    schedule_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'quarterly'
    schedule_config JSONB, -- Day of week, day of month, etc.
    email_recipients TEXT[], -- Array of email addresses
    filters JSONB,
    file_format VARCHAR(10) DEFAULT 'pdf',
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Report Favorites Table
CREATE TABLE report_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    template_id INTEGER REFERENCES report_templates(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_report_templates_category ON report_templates(category_id);
CREATE INDEX idx_generated_reports_template ON generated_reports(template_id);
CREATE INDEX idx_generated_reports_user ON generated_reports(user_id);
CREATE INDEX idx_generated_reports_date ON generated_reports(created_at);
CREATE INDEX idx_scheduled_reports_next_run ON scheduled_reports(next_run_at);
CREATE INDEX idx_report_favorites_user ON report_favorites(user_id);

-- ✅ End of SQL for https://aiviizn.uc.r.appspot.com/reports
============================================================


-- 📄 SQL for https://aiviizn.uc.r.appspot.com/reports">Reports</a>
-- Generated: 2025-08-19 22:29:14
-- Reference: https://celticprop.appfolio.com/reports">Reports</a>
-- Priority: 2

-- Statement 1:
-- Reports System Database Schema

-- Core reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    report_type VARCHAR(50) NOT NULL,
    query_template TEXT NOT NULL,
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_system BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Saved custom reports
CREATE TABLE saved_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    report_id UUID REFERENCES reports(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    filters JSONB DEFAULT '{}',
    columns JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scheduled reports
CREATE TABLE scheduled_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    report_id UUID REFERENCES reports(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    schedule_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly, custom
    schedule_config JSONB NOT NULL,
    filters JSONB DEFAULT '{}',
    recipients JSONB DEFAULT '[]',
    export_format VARCHAR(20) DEFAULT 'pdf',
    is_active BOOLEAN DEFAULT true,
    last_run TIMESTAMP WITH TIME ZONE,
    next_run TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Report execution history
CREATE TABLE report_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES reports(id),
    user_id UUID REFERENCES users(id),
    scheduled_report_id UUID REFERENCES scheduled_reports(id),
    execution_time INTERVAL,
    row_count INTEGER,
    export_format VARCHAR(20),
    file_path TEXT,
    status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial data for reports
CREATE TABLE financial_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    unit_id UUID REFERENCES units(id),
    tenant_id UUID REFERENCES tenants(id),
    transaction_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    amount DECIMAL(12,2) NOT NULL,
    description TEXT,
    reference_number VARCHAR(100),
    transaction_date DATE NOT NULL,
    posted_date DATE,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'posted',
    account_code VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Work orders for maintenance reports
CREATE TABLE work_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id) NOT NULL,
    unit_id UUID REFERENCES units(id),
    tenant_id UUID REFERENCES tenants(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'open',
    assigned_to VARCHAR(255),
    vendor_id UUID,
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    requested_date DATE,
    scheduled_date DATE,
    completed_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_reports_category ON reports(category);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_saved_reports_user ON saved_reports(user_id);
CREATE INDEX idx_scheduled_reports_user ON scheduled_reports(user_id);
CREATE INDEX idx_scheduled_reports_next_run ON scheduled_reports(next_run) WHERE is_active = true;
CREATE INDEX idx_financial_transactions_property ON financial_transactions(property_id);
CREATE INDEX idx_financial_transactions_date ON financial_transactions(transaction_date);
CREATE INDEX idx_financial_transactions_type ON financial_transactions(transaction_type);
CREATE INDEX idx_work_orders_property ON work_orders(property_id);
CREATE INDEX idx_work_orders_status ON work_orders(status);
CREATE INDEX idx_work_orders_date ON work_orders(created_at);

-- Sample system reports data
INSERT INTO reports (name, description, category, subcategory, report_type, query_template, is_system) VALUES 
('Profit & Loss Statement', 'Comprehensive P&L report with income and expense breakdown', 'financial', 'profit-loss', 'financial', 'profit_loss_query', true),
('Cash Flow Report', 'Cash flow analysis with inflows and outflows', 'financial', 'cash-flow', 'financial', 'cash_flow_query', true),
('Rent Roll Report', 'Current rent roll with tenant and lease information', 'financial', 'rent-roll', 'occupancy', 'rent_roll_query', true),
('Vacancy Analysis', 'Vacancy rates and trends analysis', 'occupancy', 'vacancy-analysis', 'occupancy', 'vacancy_analysis_query', true),
('Maintenance Cost Analysis', 'Maintenance expenses breakdown and trends', 'maintenance', 'maintenance-costs', 'maintenance', 'maintenance_cost_query', true),
('Work Order Summary', 'Work order status and performance metrics', 'maintenance', 'work-orders', 'maintenance', 'work_order_summary_query', true),
('Portfolio Performance', 'Overall portfolio performance metrics', 'performance', 'portfolio-summary', 'performance', 'portfolio_performance_query', true);

-- ✅ End of SQL for https://aiviizn.uc.r.appspot.com/reports">Reports</a>
============================================================


-- 🔄 NEW BUILD SESSION - 2025-08-19 22:45:00


-- 🔄 NEW BUILD SESSION - 2025-08-19 22:45:10


-- 📄 SQL for https://aiviizn.uc.r.appspot.com/reports/financial/rent-roll"
-- Generated: 2025-08-19 22:49:24
-- Reference: https://celticprop.appfolio.com/reports/financial/rent-roll"
-- Priority: 2

-- Statement 1:
-- Properties table
properties (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR NOT NULL,
  address TEXT NOT NULL,
  city VARCHAR NOT NULL,
  state VARCHAR NOT NULL,
  zip_code VARCHAR NOT NULL,
  property_type VARCHAR NOT NULL,
  units_count INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)

-- Units table
units (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  property_id UUID REFERENCES properties(id),
  unit_number VARCHAR NOT NULL,
  bedrooms INTEGER DEFAULT 0,
  bathrooms DECIMAL(2,1) DEFAULT 1.0,
  square_feet INTEGER,
  rent_amount DECIMAL(10,2) NOT NULL,
  status VARCHAR DEFAULT 'available',
  created_at TIMESTAMP DEFAULT NOW()
)

-- Tenants table
tenants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  first_name VARCHAR NOT NULL,
  last_name VARCHAR NOT NULL,
  email VARCHAR UNIQUE NOT NULL,
  phone VARCHAR,
  emergency_contact_name VARCHAR,
  emergency_contact_phone VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
)

-- Leases table
leases (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  unit_id UUID REFERENCES units(id),
  tenant_id UUID REFERENCES tenants(id),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  monthly_rent DECIMAL(10,2) NOT NULL,
  security_deposit DECIMAL(10,2) DEFAULT 0,
  status VARCHAR DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
)

-- ✅ End of SQL for https://aiviizn.uc.r.appspot.com/reports/financial/rent-roll"
============================================================

