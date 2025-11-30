"""
Script to check and create teacher account
"""
import asyncio
from app.db.supabase_client import supabase
from app.core.security import get_password_hash

async def check_and_create_teacher():
    email = "newteacher@test.com"  # From the screenshot
    password = "password123"  # Common test password
    
    # Check if user exists
    response = supabase.table("users").select("*").eq("email", email).execute()
    
    if response.data:
        print(f"User exists: {email}")
        user = response.data[0]
        print(f"  is_teacher: {user.get('is_teacher')}")
        print(f"  is_admin: {user.get('is_admin')}")
        
        # Update to be a teacher if not already
        if not user.get('is_teacher'):
            print("\n✅ Updating user to be a teacher...")
            supabase.table("users").update({
                "is_teacher": True
            }).eq("email", email).execute()
            print("✅ User updated!")
    else:
        print(f"User does not exist: {email}")
        print("\n✅ Creating teacher account...")
        
        user_data = {
            "email": email,
            "password_hash": get_password_hash(password),
            "full_name": "Test Teacher",
            "is_teacher": True,
            "is_admin": False,
            "created_at": "2025-11-29T00:00:00Z"
        }
        
        result = supabase.table("users").insert(user_data).execute()
        print(f"✅ Teacher account created!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")

if __name__ == "__main__":
    asyncio.run(check_and_create_teacher())
