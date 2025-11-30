#!/usr/bin/env python3
"""
Test Supabase connection
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("SUPABASE CONNECTION TEST")
print("=" * 60)

print(f"\n1. Checking environment variables...")
print(f"   SUPABASE_URL: {SUPABASE_URL[:50]}..." if SUPABASE_URL else "   SUPABASE_URL: NOT SET")
print(f"   SUPABASE_KEY: {SUPABASE_KEY[:50]}..." if SUPABASE_KEY else "   SUPABASE_KEY: NOT SET")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ ERROR: Credentials not found in .env file!")
    exit(1)

print("\n2. Attempting to connect to Supabase...")
try:
    from supabase import create_client
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("   ✅ Client created successfully")
    
    print("\n3. Testing users table query...")
    response = client.table("users").select("*").limit(1).execute()
    print(f"   ✅ Query successful! Got {len(response.data)} rows")
    
    print("\n4. Testing insert (will fail if email exists)...")
    test_data = {
        "id": "test-connection-123",
        "email": "test-connection@example.com",
        "password_hash": "test_hash",
        "full_name": "Test Connection",
        "is_admin": False,
        "is_teacher": False,
        "created_at": "2025-11-20T15:00:00Z",
        "updated_at": "2025-11-20T15:00:00Z"
    }
    
    try:
        insert_response = client.table("users").insert(test_data).execute()
        print(f"   ✅ Insert successful!")
        
        # Clean up
        client.table("users").delete().eq("id", "test-connection-123").execute()
        print("   ✅ Cleanup successful!")
    except Exception as e:
        if "duplicate" in str(e).lower():
            print(f"   ⚠️  Email already exists (expected): {e}")
        else:
            print(f"   ❌ Insert failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ SUPABASE CONNECTION WORKING!")
    print("=" * 60)
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print("\n" + "=" * 60)
    print("❌ SUPABASE CONNECTION FAILED!")
    print("=" * 60)
    exit(1)
