# AIVIIZN Property Management System - Project Documentation

## 🏢 Project Overview
**Project Name:** AIVIIZN Property Management System  
**Technology Stack:** Python Flask + Supabase + Jinja2 Templates  
**Purpose:** Complete property management solution for tracking tenants, properties, maintenance, accounting, and leasing operations  
**Location:** `/Users/ianrakow/Desktop/AIVIIZN/`

## 🔑 Authentication & Security

### Supabase Configuration
```
URL: https://sejebqdhcilwcpjpznep.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ
```

### Authentication Flow
1. **Login System:** Server-side authentication using Flask sessions
2. **Session Management:** 24-hour session lifetime with secure cookies
3. **Protected Routes:** All routes use `@login_required` decorator
4. **Demo Login:** admin@aiviizn.com / demo123 (for testing)

## 📁 Project Structure

```
AIVIIZN/
├── app.py                 # Main Flask application with all routes
├── requirements.txt       # Python dependencies
├── templates/            # Jinja2 HTML templates
│   ├── dashboard.html    # Main dashboard with stats and charts
│   ├── auth/            # Authentication templates
│   │   ├── login.html   # Login page with Supabase integration
│   │   └── register.html # Registration page
│   ├── leasing/         # Leasing module templates
│   │   ├── vacancies.html
│   │   ├── guest_cards.html
│   │   ├── rental_applications.html
│   │   ├── leases.html
│   │   ├── renewals.html
│   │   ├── metrics.html
│   │   └── signals.html
│   ├── maintenance/     # Maintenance module templates
│   │   ├── work_orders.html
│   │   ├── recurring_work_orders.html
│   │   ├── inspections.html
│   │   ├── unit_turns.html
│   │   ├── projects.html
│   │   ├── purchase_orders.html
│   │   ├── inventory.html
│   │   ├── fixed_assets.html
│   │   └── smart_maintenance.html
│   ├── accounting/      # Accounting module templates
│   │   ├── receivables.html
│   │   ├── payables.html
│   │   ├── bank_accounts.html
│   │   ├── journal_entries.html
│   │   ├── bank_transfers.html
│   │   ├── gl_accounts.html
│   │   ├── diagnostics.html
│   │   └── receipts.html
│   ├── people/          # People management templates
│   │   ├── tenants.html
│   │   ├── owners.html
│   │   └── vendors.html
│   ├── properties/      # Property management templates
│   │   └── properties.html
│   ├── reporting/       # Reporting module templates
│   │   ├── reports.html
│   │   ├── scheduled_reports.html
│   │   ├── metrics.html
│   │   └── surveys.html
│   └── communication/   # Communication module templates
│       ├── letters.html
│       ├── forms.html
│       └── inbox.html
├── static/              # Static assets (CSS, JS, images)
└── config/              # Configuration files
```

## 🎯 Core Functionality Modules

### 1. Dashboard Module
- **Purpose:** Central hub showing key metrics and quick actions
- **Key Stats Displayed:**
  - Move-ins tracking (updated count, finished count)
  - Delinquencies (0-30, 31-60, 61+ days)
  - Work orders (new, assigned, completed)
  - Insurance coverage metrics
  - Online payment statistics
  - Financial performance charts
  - Recent move-ins table

### 2. Leasing Module
- **Vacancies:** Track available units with days vacant, pricing
- **Guest Cards:** Manage prospective tenant inquiries
- **Rental Applications:** Process and track applications
- **Leases:** Generate and manage lease agreements
- **Renewals:** Handle lease renewals with status tracking
- **Metrics:** Occupancy rates, demand analysis, pricing metrics
- **Signals:** Automated alerts and notifications

### 3. Maintenance Module
- **Work Orders:** Track maintenance requests (resident, internal, unit turn)
- **Recurring Work Orders:** Scheduled maintenance tasks
- **Inspections:** Property inspection tracking
- **Unit Turns:** Manage unit turnover process
- **Projects:** Capital improvement projects
- **Purchase Orders:** Vendor purchase management
- **Inventory:** Maintenance supplies tracking
- **Fixed Assets:** Equipment and asset management
- **Smart Maintenance:** Predictive maintenance features

### 4. Accounting Module
- **Receivables:** Tenant payment tracking
- **Payables:** Vendor bills and payments
- **Bank Accounts:** Multiple account management with reconciliation
- **Journal Entries:** General ledger entries
- **Bank Transfers:** Inter-account transfers
- **GL Accounts:** Chart of accounts management
- **Diagnostics:** Financial health checks, deposit mismatches
- **Receipts:** Payment receipt management

### 5. People Management
- **Tenants:** Current and past tenant records
- **Owners:** Property owner information
- **Vendors:** Service provider management

### 6. Properties Module
- **Property Records:** Complete property information
- **Unit Management:** Individual unit tracking
- **Owner Associations:** Link properties to owners

### 7. Communication Module
- **Letters:** Template-based correspondence
- **Forms:** Document management
- **Inbox:** Message center

### 8. Reporting Module
- **Standard Reports:** Pre-built report templates
- **Scheduled Reports:** Automated report generation
- **Metrics:** Performance analytics
- **Surveys:** Tenant satisfaction surveys

## 🎨 UI/UX Design System

### Visual Design
- **Color Scheme:** Purple gradient theme (#667eea to #764ba2)
- **Framework:** Bootstrap 5.3 with custom CSS
- **Icons:** Font Awesome 6.4
- **Typography:** Inter font family
- **Layout:** Sidebar navigation with main content area

### Key UI Components
- **Sidebar:** Collapsible navigation with dropdown menus
- **Stat Cards:** Dashboard metric displays with icons
- **Data Tables:** Sortable, filterable tables for data
- **Forms:** Bootstrap form components with validation
- **Alerts:** Flash message system for user feedback
- **Charts:** Chart.js for financial visualizations

## 🔧 Technical Implementation Details

### Flask Application Structure
```python
# Key decorators and functions
@login_required  # Protects routes requiring authentication
@app.route()     # Defines URL endpoints
session[]        # Server-side session storage
flash()          # User notification messages
```

### Session Management
- **Storage:** Server-side Flask sessions
- **Duration:** 24-hour lifetime
- **Security:** HTTPOnly, Secure, SameSite cookies
- **User Data:** user_id, email, company stored in session

### Database Schema (Implied from UI)
- **Users:** Authentication and profile data
- **Properties:** Buildings and units
- **Tenants:** Resident information
- **Leases:** Rental agreements
- **Work Orders:** Maintenance requests
- **Transactions:** Financial records
- **Documents:** Letters, forms, templates

## 🚀 Deployment Information

### Environment Configuration
- **Development:** Flask debug mode on port 8080
- **Production Ready:** Includes Dockerfile and app.yaml
- **Cloud:** Google Cloud Platform deployment files
- **CI/CD:** cloudbuild.yaml for automated deployment

### Required Environment Variables
```
FLASK_SECRET_KEY    # Session encryption key
SUPABASE_URL        # Supabase project URL
SUPABASE_ANON_KEY   # Supabase anonymous key
```

## 📊 Current System Status

### What's Working
✅ Complete authentication system with Supabase  
✅ Session management and protected routes  
✅ Dashboard with mock data displays  
✅ All navigation routes configured  
✅ Beautiful, responsive UI design  
✅ Template structure for all modules  

### Data Population Status
- Currently using mock/demo data in routes
- Ready for Supabase database integration
- All data structures defined in Python dictionaries

## 🔄 Integration Points

### Supabase Integration
- **Authentication:** ✅ Implemented
- **Database:** Ready for table creation
- **Real-time:** Available for notifications
- **Storage:** Available for documents

### External Services Ready for Integration
- Payment processing (Stripe/PayPal)
- SMS notifications (Twilio)
- Email service (SendGrid)
- Document generation (PDF)
- Background jobs (Celery)

## 📝 Development Notes

### Key Files to Remember
1. **app.py** - Main application logic and routes
2. **templates/dashboard.html** - Main UI template
3. **templates/auth/login.html** - Authentication entry point
4. **requirements.txt** - Python dependencies

### Common Development Tasks
```bash
# Run development server
python app.py

# Install dependencies
pip install -r requirements.txt

# Deploy to production
./deploy.sh
```

### Testing Credentials
- **Demo Admin:** admin@aiviizn.com / demo123
- **Test Company:** Test Company

## 🎯 Next Steps for Full Implementation

1. **Database Setup**
   - Create Supabase tables matching data structures
   - Implement RLS (Row Level Security) policies
   - Set up database migrations

2. **Data Integration**
   - Replace mock data with Supabase queries
   - Implement CRUD operations for all modules
   - Add data validation and error handling

3. **Feature Completion**
   - Implement file upload for documents
   - Add email notifications
   - Create report generation system
   - Build analytics dashboards

4. **Production Readiness**
   - Add comprehensive error logging
   - Implement rate limiting
   - Set up monitoring and alerts
   - Create backup strategies

## 🔐 Security Considerations

- All routes protected with login_required
- Session-based authentication (not JWT)
- HTTPS required in production
- Input validation on all forms
- SQL injection prevention via Supabase
- XSS protection with Jinja2 auto-escaping

## 📚 Additional Resources

- **Supabase Docs:** https://supabase.com/docs
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Bootstrap Components:** https://getbootstrap.com/docs/5.3/
- **Chart.js:** https://www.chartjs.org/docs/

---

## Summary
AIVIIZN is a comprehensive property management system built with Flask and Supabase. The authentication system is complete and functional, using server-side sessions for security. The UI is polished and professional with a modern design. All routes are configured and templates are in place. The system is ready for database integration to replace mock data with real Supabase queries.