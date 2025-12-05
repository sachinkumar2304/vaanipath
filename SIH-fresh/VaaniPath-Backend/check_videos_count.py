from app.db.supabase_client import supabase

result = supabase.table('videos').select('id, title').limit(5).execute()
print(f'Videos in DB: {len(result.data)}')
for v in result.data:
    print(f"  - {v['title']} ({v['id']})")
