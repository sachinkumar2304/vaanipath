"""
Check all teacher accounts in database
"""
import asyncio
from app.db.supabase_client import supabase

async def list_teachers():
    # Get all teachers
    response = supabase.table("users").select("*").eq("is_teacher", True).execute()
    
    print(f"Found {len(response.data)} teacher account(s):\n")
    
    for user in response.data:
        print(f"Email: {user.get('email')}")
        print(f"Full Name: {user.get('full_name')}")
        print(f"is_teacher: {user.get('is_teacher')}")
        print(f"is_admin: {user.get('is_admin')}")
        print("---")

if __name__ == "__main__":
    asyncio.run(list_teachers())
