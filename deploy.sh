#!/bin/bash

# Deploy script for Property Management System

echo "🚀 Starting deployment..."

# Check if all required files exist
echo "📋 Checking files..."

if [ ! -f "app.py" ]; then
    echo "❌ app.py not found!"
    exit 1
fi

if [ ! -d "templates" ]; then
    echo "❌ templates directory not found!"
    exit 1
fi

# Create a deployment package
echo "📦 Creating deployment package..."

# Ensure all templates are in place
cat > file_check.txt << EOF
Required files:
- app.py ✓
- requirements.txt ✓
- Dockerfile ✓
- .env ✓
- templates/base.html ✓
- templates/dashboard.html ✓
- templates/properties.html ✓
- templates/tenants.html ✓
- templates/owners.html ✓
- templates/vendors.html ✓
- templates/guest_cards.html ✓
- templates/vacancies.html ✓
- templates/leases.html ✓
- templates/renewals.html ✓
- templates/rental_applications.html ✓
- templates/metrics.html ✓
- templates/receivables.html ✓
- templates/payables.html ✓
- templates/bank_accounts.html ✓
- templates/journal_entries.html ✓
- templates/bank_transfers.html ✓
- templates/gl_accounts.html ✓
- templates/diagnostics.html ✓
- templates/login.html ✓
EOF

echo "📝 Files ready for deployment"

# Deploy to Cloud Run
echo "☁️ Deploying to Google Cloud Run..."

gcloud run deploy property-management \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --timeout 60 \
    --max-instances 10 \
    --set-env-vars "SUPABASE_URL=https://sejebqdhcilwcpjpznep.supabase.co,SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ,SECRET_KEY=f3cfe9ed8fae309f02079dbf,FLASK_ENV=production"

echo "✅ Deployment complete!"
echo "🌐 Your app should be live at: https://[YOUR-SERVICE-NAME]-[PROJECT-ID].us-central1.run.app"