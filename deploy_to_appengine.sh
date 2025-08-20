#!/bin/bash

echo "🚀 Starting Google App Engine deployment..."
echo "================================================"

# Change to the project directory
cd /Users/ianrakow/Desktop/AIVIIZN

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set the project ID
echo "📋 Setting project..."
gcloud config set project aiviizn

# Deploy to App Engine
echo "☁️  Deploying to Google App Engine..."
echo "This may take a few minutes..."

# Deploy with automatic yes to prompts
gcloud app deploy app.yaml --quiet

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Your app is live at: https://aiviizn.uc.r.appspot.com"
    echo ""
    echo "📝 Changes deployed:"
    echo "  - Fixed missing {% block styles %} in base.html"
    echo "  - Fixed URL matching in JavaScript for work-orders pages"
    echo "  - Added null checks to prevent JavaScript errors"
    echo ""
    echo "🔗 Test the fixed pages:"
    echo "  - https://aiviizn.uc.r.appspot.com/maintenance/work-orders"
    echo "  - https://aiviizn.uc.r.appspot.com/maintenance/recurring-work-orders"
else
    echo "❌ Deployment failed. Please check the error messages above."
    exit 1
fi
