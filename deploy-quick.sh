#!/bin/bash

# Quick deployment script for Google Cloud Run
# Make this executable: chmod +x deploy.sh
# Run with: ./deploy.sh

echo "🚀 Starting deployment to Google Cloud Run..."

# Set your project ID
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="aiaviizn"
REGION="us-central1"

# Create Dockerfile if it doesn't exist
if [ ! -f "Dockerfile" ]; then
    echo "📝 Creating Dockerfile..."
    cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
EOF
fi

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "📝 Creating requirements.txt..."
    cat > requirements.txt << 'EOF'
Flask==2.3.3
Flask-CORS==4.0.0
supabase==1.2.0
python-dotenv==1.0.0
Jinja2==3.1.2
gunicorn==21.2.0
postgrest==0.13.0
realtime==1.0.0
gotrue==1.3.0
storage3==0.6.0
EOF
fi

# Create .gcloudignore
echo "📝 Creating .gcloudignore..."
cat > .gcloudignore << 'EOF'
.gcloudignore
.git
.gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
*.db
.DS_Store
EOF

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "SUPABASE_URL=https://sejebqdhcilwcpjpznep.supabase.co" \
    --set-env-vars "SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ" \
    --set-env-vars "SECRET_KEY=f3cfe9ed8fae309f02079dbf" \
    --set-env-vars "FLASK_ENV=production"

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at: https://$SERVICE_NAME-$PROJECT_ID.run.app"