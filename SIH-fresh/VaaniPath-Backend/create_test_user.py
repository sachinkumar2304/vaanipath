import asyncio
from app.db.supabase_client import supabase
from app.core.security import get_password_hash
import uuid

async def create_test_user():
    email = "test@example.com"
    password = "password123"
    
    # Check if user exists
    existing = supabase.table("users").select("*").eq("email", email).execute()
    
    if existing.data:
        print(f"User {email} already exists. Updating password...")
        user_id = existing.data[0]["id"]
        supabase.table("users").update({
            "password_hash": get_password_hash(password)
        }).eq("id", user_id).execute()
        print("Password updated.")
    else:
        print(f"Creating user {email}...")
        user_data = {
            "email": email,
            "full_name": "Test User",
            "password_hash": get_password_hash(password),
            "is_admin": True,
            "is_teacher": False
        }
        supabase.table("users").insert(user_data).execute()
        print("User created.")

if __name__ == "__main__":
    asyncio.run(create_test_user())
