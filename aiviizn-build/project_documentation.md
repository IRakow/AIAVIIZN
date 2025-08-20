# AIVIIZN Property Management System

## 🔐 Authentication Workflow
1. **User logs into AppFolio** (celticprop.appfolio.com) in browser
2. **Claude accesses authenticated AppFolio pages** via browser tools
3. **No additional authentication needed** during build process
4. **Copies exact functionality** from AppFolio to AIVIIZN

## 🏗️ Project Overview
Advanced Flask-based property management system that replicates and enhances AppFolio functionality with modern AI integration.

## 🛠️ Tech Stack
- **Backend:** Flask (Python) with SQLAlchemy
- **Database:** Supabase (accessed via MCP server)
- **Frontend:** Bootstrap 5, Font Awesome, Inter font, jQuery
- **Templates:** Jinja2 with base.html inheritance
- **Authentication:** Browser session for AppFolio access
- **AI Integration:** Claude API for intelligent features

## 📁 Project Structure
```
AIVIIZN/
├── templates/
│   ├── base.html (main layout)
│   ├── dashboard/
│   ├── properties/
│   ├── maintenance/
│   ├── leasing/
│   ├── accounting/
│   ├── reports/
│   └── tenants/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── aiviizn_build.log
├── build_progress.md
└── database_schema.sql
```

## 🎨 Template Structure
All pages must extend base.html:
```html
{% extends "base.html" %}

{% block title %}Page Title - AIVIIZN{% endblock %}
{% block page_title %}Page Title{% endblock %}

{% block page_description %}
<p class="text-muted mb-0">Brief description of the page</p>
{% endblock %}

{% block content %}
<!-- Page content here with Bootstrap 5 classes -->
{% endblock %}

{% block extra_css %}
<!-- Additional CSS if needed -->
{% endblock %}

{% block extra_js %}
<!-- Additional JavaScript if needed -->
{% endblock %}
```

## 🗄️ Database Integration
- **Connected via MCP server** to Supabase
- **Real database operations** for all functionality
- **Full CRUD operations** required
- **Production-ready data persistence**
- **Proper foreign key relationships**

## 📋 AppFolio Reference Access
- **Claude accesses authenticated AppFolio pages** automatically
- **Copies exact functionality** from reference pages
- **Maintains AIVIIZN layout** and navigation structure
- **Integrates AppFolio features** into modern design system

## 🏢 Core Modules to Build

### 1. Dashboard
- Property overview and metrics
- Recent activity feed
- Financial summary widgets
- Quick action buttons

### 2. Properties
- Property listing and management
- Unit management within properties
- Property details and documentation
- Maintenance history per property

### 3. Tenants
- Tenant directory and profiles
- Lease management
- Communication history
- Payment tracking

### 4. Maintenance
- Work order management
- Vendor coordination
- Inventory tracking
- Preventive maintenance scheduling

### 5. Leasing
- Application processing
- Lease document management
- Renewal workflows
- Marketing and availability

### 6. Accounting
- Rent collection
- Expense tracking
- Financial reporting
- Budget management

### 7. Reports
- Financial reports
- Occupancy analytics
- Maintenance reports
- Custom reporting tools

## 🎯 Build Requirements
- **Production-ready code** (no placeholders)
- **Real Supabase integration** with working CRUD
- **Responsive design** using Bootstrap 5
- **Modern UX/UI** with smooth interactions
- **Form validation** and error handling
- **Search and filtering** capabilities
- **Bulk actions** where appropriate
- **Export functionality** for reports

## 🚀 AI Enhancements (Future)
- Smart maintenance predictions
- Automated tenant screening
- Intelligent rent pricing
- Natural language search
- Document processing automation
- Predictive analytics
