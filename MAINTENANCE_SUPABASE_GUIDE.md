# AIVIIZN Maintenance System - Supabase Integration Guide

## 🗄️ Database Setup

### 1. Run the SQL Schema
Execute the SQL file in your Supabase SQL Editor:
```bash
/Users/ianrakow/Desktop/AIVIIZN/supabase_maintenance_schema.sql
```

This will create all necessary tables, relationships, triggers, and sample data.

### 2. Supabase Configuration
The system is configured to use your Supabase project:
- **Project URL:** `https://sejebqdhcilwcpjpznep.supabase.co`
- **Project ID:** `sejebqdhcilwcpjpznep`
- **Database:** AIVIIZN project

## 📁 Updated Files

### Core Infrastructure:
- **`templates/base.html`** - Added Supabase JavaScript library
- **`static/js/supabase-config.js`** - Supabase client configuration and utility functions

### Maintenance Pages (Connected to Supabase):
- **`templates/maintenance/work_orders.html`** - Work orders with full CRUD operations
- **`templates/maintenance/recurring_work_orders.html`** - Recurring templates with database integration
- **`templates/maintenance/inspections.html`** - Inspections with calendar and database support

## 🎯 Features Implemented

### ✅ **Work Orders System**
- **Full Database Integration:** Create, read, update, delete work orders
- **Real-time Data:** Live data from Supabase with pagination and filtering
- **Photo Upload Support:** Database schema ready for file attachments
- **Vendor Assignment:** Dynamic vendor/staff loading from database
- **Property Management:** Real property and unit data from database
- **Advanced Filtering:** Server-side filtering by property, status, vendor, assignee
- **Hybrid Data:** Falls back to sample data if database is unavailable

### ✅ **Recurring Work Orders**
- **Template Management:** Create and manage recurring maintenance templates
- **Database Persistence:** All templates stored in Supabase
- **Property Assignment:** Link templates to multiple properties
- **Generation Tracking:** Track when work orders are auto-generated
- **Frequency Scheduling:** Daily, weekly, monthly, quarterly, annually

### ✅ **Inspections System**
- **Full CRUD Operations:** Create, schedule, complete inspections
- **Interactive Calendar:** Visual calendar view with inspection scheduling
- **Checklist Management:** Database-ready inspection checklists
- **Inspector Assignment:** Dynamic inspector loading from vendors table
- **Photo Documentation:** Schema supports inspection photos

## 🔧 Database Schema

### Core Tables:
- **`properties`** - Property information (West Plaza, Longmeadow, etc.)
- **`units`** - Individual units within properties
- **`vendors`** - Staff and external vendors/contractors
- **`work_orders`** - All maintenance work orders
- **`recurring_templates`** - Recurring work order templates
- **`inspections`** - Property inspections

### Features:
- **Auto-numbering:** Work orders and inspections get automatic numbers (WO-2025-000001)
- **Audit Trails:** `created_at` and `updated_at` timestamps
- **Data Relationships:** Proper foreign keys between all entities
- **Sample Data:** Pre-loaded with realistic test data
- **No Authentication:** Open access for simplified development

## 🚀 Usage

### 1. Work Orders
- Click **"New Service Request"** to create work orders
- All data saves to Supabase `work_orders` table
- Real-time filtering and pagination
- Status updates persist to database

### 2. Recurring Templates
- Click **"New Template"** to create recurring work orders
- Templates link to multiple properties via `template_properties` table
- Generation tracking and scheduling

### 3. Inspections
- Toggle between **List View** and **Calendar View**
- Click **"Schedule Inspection"** to create new inspections
- Interactive checklist system (database-ready)
- Inspector assignment from vendors table

## 🔄 Hybrid Data Approach

The system uses **hybrid data** - it attempts to load from Supabase first, but falls back to sample data if the database is unavailable:

```javascript
// Tries Supabase first
const { data, error } = await SupabaseUtils.getWorkOrders();

if (error) {
    // Falls back to sample data
    workOrders = sampleWorkOrders;
}
```

## 🎨 UI Features

All original AppFolio-style features remain:
- **Dashboard metrics** with click-to-filter
- **Bulk operations** on selected items
- **Advanced filtering** with real-time updates
- **Modal forms** with validation
- **Toast notifications** for user feedback
- **Responsive design** for all devices
- **Photo upload** interfaces (ready for file storage)

## ⚙️ Technical Implementation

### No Authentication Required
The system uses **anonymous access** with Row Level Security policies that allow full access without login:

```sql
CREATE POLICY "Allow anonymous full access on work_orders" 
ON work_orders FOR ALL USING (true);
```

### Real-time Updates
All CRUD operations immediately refresh the UI:
```javascript
await SupabaseUtils.createWorkOrder(data);
await loadWorkOrders(); // Refresh the list
```

### Error Handling
Graceful error handling with user-friendly messages:
```javascript
if (error) {
    showToast('Error creating work order', 'error');
    return;
}
```

## 🔗 Next Steps

1. **Run the SQL schema** in your Supabase project
2. **Test the forms** - create work orders, templates, and inspections
3. **Add file upload** - Implement Supabase Storage for photos
4. **Customize data** - Modify properties, vendors, and templates as needed
5. **Extend functionality** - Add reporting, notifications, etc.

The maintenance system is now fully connected to Supabase with hybrid data support and no authentication requirements!