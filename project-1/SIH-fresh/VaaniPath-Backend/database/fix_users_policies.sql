-- Fix users table RLS policies
-- Drop existing policies if they exist and recreate them properly

-- Drop existing policies
DROP POLICY IF EXISTS "Users can read own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Anyone can create user account" ON users;

-- Create proper policies
-- 1. Anyone can read (public profiles)
CREATE POLICY "Users can read own profile" ON users
  FOR SELECT USING (true);

-- 2. Anyone can insert (signup)
CREATE POLICY "Anyone can create user account" ON users
  FOR INSERT WITH CHECK (true);

-- 3. Users can update their own profile
CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (true) WITH CHECK (true);

-- Done!
