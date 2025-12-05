"""
Reset password for newtutor@test.com
"""
import asyncio
from app.db.supabase_client import supabase
from app.core.security import get_password_hash

async def reset_teacher_password():
    email = "newtutor@test.com"
    new_password = "password123"
    
    # Update password
    password_hash = get_password_hash(new_password)
    
    result = supabase.table("users").update({
        "password_hash": password_hash,
        "is_teacher": True,  # Ensure is_teacher is set
        "is_admin": False
    }).eq("email", email).execute()
    
    if result.data:
        print(f"✅ Password reset successful for {email}")
        print(f"   New password: {new_password}")
        print(f"   is_teacher: True")
    else:
        print(f"❌ Failed to reset password")

if __name__ == "__main__":
    asyncio.run(reset_teacher_password())
