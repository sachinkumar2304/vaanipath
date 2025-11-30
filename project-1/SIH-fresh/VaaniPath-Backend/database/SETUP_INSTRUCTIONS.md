# Database Setup Instructions for Quiz & Doubts

## Error You're Seeing
```
Could not find the table 'public.doubts' in the schema cache
```

This means the database tables for Quiz and Doubts features haven't been created yet in Supabase.

## How to Fix

### Step 1: Open Supabase SQL Editor
1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Click on "SQL Editor" in the left sidebar

### Step 2: Run the Migration Script
1. Open the file: `database/quiz_doubts_schema.sql`
2. Copy ALL the content from that file
3. Paste it into the Supabase SQL Editor
4. Click "RUN" button (or press Ctrl+Enter)

### Step 3: Verify Tables Were Created
After running the script, you should see a success message. To verify:
1. In Supabase, go to "Table Editor"
2. You should now see these new tables:
   - `doubts`
   - `quiz_questions` (may already exist)
   - `quiz_sessions` (may already exist)
   - `user_answers` (may already exist)

### Step 4: Test the Application
1. Your backend server will auto-reload (it's already running)
2. Refresh your Teacher Doubts page
3. You should no longer see the error
4. The page should load (showing empty list initially, which is correct)

## What These Tables Do

### `doubts`
- Stores student questions/doubts
- Links to `videos` table (which video the doubt is about)
- Links to `users` table (which student asked)
- Tracks status: 'pending' or 'answered'

### `quiz_questions`
- Stores quiz questions for each video
- Created by teachers
- Contains question text, options, correct answer

### `quiz_sessions`
- Tracks when students attempt quizzes
- Records scores and completion time

### `user_answers`
- Records individual answers during a quiz session
- Tracks which answers were correct

## Troubleshooting

### If you still see errors after running the script:
1. Make sure you're using the correct Supabase project
2. Check that your `.env` file has the correct `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
3. Try refreshing the Supabase schema cache (wait 30 seconds, or click "Refresh" in Table Editor)

### If RLS (Row Level Security) causes issues:
The script already sets up proper RLS policies so:
- Students can only see their own doubts
- Teachers can see doubts for their own videos
- Everyone can view quiz questions
- Users can only access their own quiz sessions

These security rules are important to keep your data safe!
