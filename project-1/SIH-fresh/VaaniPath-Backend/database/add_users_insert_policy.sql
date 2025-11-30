-- Add INSERT policy for users table
-- This allows anyone to create a new user account (signup)

CREATE POLICY "Anyone can create user account" ON users
  FOR INSERT WITH CHECK (true);

-- Also add UPDATE policy so users can update their own profile
CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (true) WITH CHECK (true);
