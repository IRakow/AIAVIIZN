#!/usr/bin/env python3
"""
Deploy the AIVIIZN app to Google App Engine
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Google App Engine deployment...")
    print("=" * 50)
    
    # Change to project directory
    os.chdir('/Users/ianrakow/Desktop/AIVIIZN')
    
    # Set the project
    print("📋 Setting project to aiviizn...")
    result = subprocess.run(['gcloud', 'config', 'set', 'project', 'aiviizn'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to set project: {result.stderr}")
        return 1
    
    # Deploy to App Engine
    print("☁️  Deploying to Google App Engine...")
    print("This may take 3-5 minutes...")
    print("")
    
    # Run the deployment
    result = subprocess.run(['gcloud', 'app', 'deploy', 'app.yaml', '--quiet'],
                          capture_output=False, text=True)
    
    if result.returncode == 0:
        print("")
        print("✅ Deployment successful!")
        print("🌐 Your app is live at: https://aiviizn.uc.r.appspot.com")
        print("")
        print("📝 Changes deployed:")
        print("  - Fixed missing {% block styles %} in base.html")
        print("  - Fixed URL matching in JavaScript for work-orders pages") 
        print("  - Added null checks to prevent JavaScript errors")
        print("")
        print("🔗 Test the fixed pages:")
        print("  - https://aiviizn.uc.r.appspot.com/maintenance/work-orders")
        print("  - https://aiviizn.uc.r.appspot.com/maintenance/recurring-work-orders")
        return 0
    else:
        print("❌ Deployment failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
