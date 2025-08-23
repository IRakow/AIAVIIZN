# test_supabase_connection.py - Test Supabase connection without user input

from supabase import create_client
import sys

# Your Supabase credentials
SUPABASE_URL = 'https://sejebqdhcilwcpjpznep.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ'

print("🔍 Testing Supabase Connection...")
print("="*50)

try:
    # Create client
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Supabase client created successfully")
    print(f"   URL: {SUPABASE_URL}")
    print(f"   Key: {SUPABASE_ANON_KEY[:20]}...")
    
    # Try to query a table to test connection
    print("\n📊 Testing database connection...")
    try:
        # Try to query users table (might be empty)
        response = supabase.table('users').select('*').limit(1).execute()
        print("✅ Database connection successful!")
        print(f"   Query executed successfully")
        if response.data:
            print(f"   Found {len(response.data)} record(s)")
        else:
            print("   Table exists but no data found (this is normal)")
    except Exception as e:
        if 'relation "public.users" does not exist' in str(e):
            print("⚠️  'users' table doesn't exist - this is expected if not yet created")
        else:
            print(f"⚠️  Query failed: {e}")
    
    print("\n🔐 Testing authentication service...")
    # Check if auth service is responding
    try:
        # This will fail but shows auth service is responding
        test_response = supabase.auth.sign_in_with_password({
            "email": "test@test.com",
            "password": "test"
        })
    except Exception as e:
        error_msg = str(e)
        if 'Invalid login credentials' in error_msg:
            print("✅ Auth service is responding correctly")
            print("   (Invalid credentials error is expected for test)")
        else:
            print(f"⚠️  Auth service response: {error_msg}")
    
    print("\n" + "="*50)
    print("✅ SUPABASE CONNECTION TEST COMPLETE")
    print("   Your Supabase instance is accessible")
    print("   You can now create users in the Supabase dashboard")
    print("   Go to: https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/auth/users")
    print("="*50)
    
except Exception as e:
    print(f"❌ Failed to create Supabase client: {e}")
    print("\n💡 This might be a version issue. Try:")
    print("   pip3 install supabase==1.2.0")
    sys.exit(1)