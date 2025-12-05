"""
Check exact user data in database
"""
import asyncio
from app.db.supabase_client import supabase

async def check_exact_user():
    email = "newtutor@test.com"
    
    response = supabase.table("users").select("*").eq("email", email).execute()
    
    if response.data:
        user = response.data[0]
        print(f"Database record for {email}:\n")
        for key, value in user.items():
            print(f"  {key}: {value}")
    else:
        print(f"User not found: {email}")

if __name__ == "__main__":
    asyncio.run(check_exact_user())
