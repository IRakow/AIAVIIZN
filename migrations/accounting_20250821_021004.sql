-- AIVIIZN Database Migration for accounting
-- Generated from AppFolio page analysis
-- Timestamp: 2025-08-21T02:10:04.271848


-- Table: accounting_data
CREATE TABLE IF NOT EXISTS accounting_data (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    gl_account INTEGER,
    type TEXT,
);

