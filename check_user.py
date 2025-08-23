# check_user.py - Run this script to check your Supabase user status
# Save this as check_user.py and run: python3 check_user.py

from supabase import create_client
import sys

# Your Supabase credentials
SUPABASE_URL = 'https://sejebqdhcilwcpjpznep.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ'

print("🔍 Checking Supabase Connection and User...")
print("="*50)

try:
    # Create client
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Supabase client created successfully")
    
    # Get user email to test
    email = input("\nEnter your Supabase user email: ")
    password = input("Enter your password: ")
    
    print("\n" + "="*50)
    print("Testing authentication...")
    
    try:
        # Try to sign in
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response and response.user:
            user = response.user
            print("\n✅ LOGIN SUCCESSFUL!")
            print(f"   User ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Created: {user.created_at}")
            print(f"   Email Confirmed: {user.email_confirmed_at}")
            print(f"   Last Sign In: {user.last_sign_in_at}")
            
            if not user.email_confirmed_at:
                print("\n⚠️  WARNING: Email not confirmed!")
                print("   Please check your email for confirmation link")
            
            if response.session:
                print("\n🔑 Session created successfully")
                print(f"   Access token: {response.session.access_token[:20]}...")
                
            print("\n✅ Everything looks good! You should be able to login.")
            
        else:
            print("❌ Authentication failed - no user returned")
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Authentication failed: {error_msg}")
        
        if 'Invalid login credentials' in error_msg:
            print("\n💡 Possible issues:")
            print("   1. Wrong password")
            print("   2. User doesn't exist")
            print("   3. Email not confirmed")
            
        elif 'Email not confirmed' in error_msg:
            print("\n💡 Your email is not confirmed!")
            print("   1. Check your email for confirmation link")
            print("   2. Or manually confirm in Supabase dashboard:")
            print("      - Go to Authentication → Users")
            print("      - Find your user")
            print("      - Click 'Confirm Email'")
            
except Exception as e:
    print(f"❌ Failed to create Supabase client: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("Additional debugging info:")
print(f"URL: {SUPABASE_URL}")
print(f"Key starts with: {SUPABASE_ANON_KEY[:20]}")
print("="*50)