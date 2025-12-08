-- ============================================
-- COMMUNITY FEATURE DATABASE SCHEMA
-- Separate Supabase Database
-- Run this in your Community Supabase SQL Editor
-- ============================================

-- ============================================
-- 1. COMMUNITIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS communities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  domain VARCHAR(100) NOT NULL, -- 'java', 'python', 'ai_ml', 'javascript', 'web_dev', 'data_science', etc.
  description TEXT,
  created_by UUID NOT NULL, -- References main DB users(id)
  thumbnail_url VARCHAR(500),
  member_count INTEGER DEFAULT 0,
  post_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_communities_domain ON communities(domain);
CREATE INDEX IF NOT EXISTS idx_communities_created_by ON communities(created_by);

-- ============================================
-- 2. COMMUNITY MEMBERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS community_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  community_id UUID NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
  user_id UUID NOT NULL, -- References main DB users(id)
  role VARCHAR(50) DEFAULT 'member', -- 'creator', 'moderator', 'member'
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(community_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_community_members_community ON community_members(community_id);
CREATE INDEX IF NOT EXISTS idx_community_members_user ON community_members(user_id);

-- ============================================
-- 3. COMMUNITY POSTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS community_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  community_id UUID NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
  user_id UUID NOT NULL, -- References main DB users(id)
  content TEXT NOT NULL,
  media_urls TEXT[], -- Array of image URLs from Cloudinary
  post_type VARCHAR(50) DEFAULT 'text', -- 'text', 'course_promotion', 'announcement'
  course_id UUID, -- References main DB courses(id) for promotions
  is_pinned BOOLEAN DEFAULT FALSE, -- For announcements
  likes_count INTEGER DEFAULT 0,
  replies_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_posts_community ON community_posts(community_id);
CREATE INDEX IF NOT EXISTS idx_posts_user ON community_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON community_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_pinned ON community_posts(is_pinned, created_at DESC);

-- ============================================
-- 4. POST LIKES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS post_likes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
  user_id UUID NOT NULL, -- References main DB users(id)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(post_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_post_likes_post ON post_likes(post_id);
CREATE INDEX IF NOT EXISTS idx_post_likes_user ON post_likes(user_id);

-- ============================================
-- 5. POST REPLIES TABLE (Supports Threading)
-- ============================================
CREATE TABLE IF NOT EXISTS post_replies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
  user_id UUID NOT NULL, -- References main DB users(id)
  parent_reply_id UUID REFERENCES post_replies(id) ON DELETE CASCADE, -- For threading
  content TEXT NOT NULL,
  likes_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_post_replies_post ON post_replies(post_id);
CREATE INDEX IF NOT EXISTS idx_post_replies_user ON post_replies(user_id);
CREATE INDEX IF NOT EXISTS idx_post_replies_parent ON post_replies(parent_reply_id);

-- ============================================
-- 6. REPLY LIKES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS reply_likes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reply_id UUID NOT NULL REFERENCES post_replies(id) ON DELETE CASCADE,
  user_id UUID NOT NULL, -- References main DB users(id)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(reply_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_reply_likes_reply ON reply_likes(reply_id);
CREATE INDEX IF NOT EXISTS idx_reply_likes_user ON reply_likes(user_id);

-- ============================================
-- 7. COMPETITIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS competitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  community_id UUID NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
  created_by UUID NOT NULL, -- References main DB users(id)
  title VARCHAR(255) NOT NULL,
  description TEXT,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  status VARCHAR(50) DEFAULT 'upcoming', -- 'upcoming', 'active', 'completed', 'cancelled'
  max_participants INTEGER,
  participants_count INTEGER DEFAULT 0,
  total_questions INTEGER DEFAULT 0,
  points_first INTEGER DEFAULT 100,
  points_second INTEGER DEFAULT 75,
  points_third INTEGER DEFAULT 50,
  points_top10 INTEGER DEFAULT 25,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_competitions_community ON competitions(community_id);
CREATE INDEX IF NOT EXISTS idx_competitions_status ON competitions(status);
CREATE INDEX IF NOT EXISTS idx_competitions_start_time ON competitions(start_time);

-- ============================================
-- 8. COMPETITION QUESTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS competition_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  options JSONB NOT NULL, -- [{id: 'A', text: '...'}, {id: 'B', text: '...'}, {id: 'C', text: '...'}, {id: 'D', text: '...'}]
  correct_answer VARCHAR(10) NOT NULL, -- 'A', 'B', 'C', 'D'
  points INTEGER DEFAULT 10,
  question_order INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_competition_questions_competition ON competition_questions(competition_id);
CREATE INDEX IF NOT EXISTS idx_competition_questions_order ON competition_questions(competition_id, question_order);

-- ============================================
-- 9. COMPETITION REGISTRATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS competition_registrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
  user_id UUID NOT NULL, -- References main DB users(id)
  registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(competition_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_competition_registrations_competition ON competition_registrations(competition_id);
CREATE INDEX IF NOT EXISTS idx_competition_registrations_user ON competition_registrations(user_id);

-- ============================================
-- 10. COMPETITION SUBMISSIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS competition_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
  user_id UUID NOT NULL, -- References main DB users(id)
  question_id UUID NOT NULL REFERENCES competition_questions(id) ON DELETE CASCADE,
  selected_answer VARCHAR(10) NOT NULL,
  is_correct BOOLEAN NOT NULL,
  points_earned INTEGER DEFAULT 0,
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(competition_id, user_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_competition_submissions_competition ON competition_submissions(competition_id);
CREATE INDEX IF NOT EXISTS idx_competition_submissions_user ON competition_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_competition_submissions_user_competition ON competition_submissions(user_id, competition_id);

-- ============================================
-- 11. GYAN POINTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS gyan_points (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE, -- References main DB users(id)
  total_points INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gyan_points_user ON gyan_points(user_id);
CREATE INDEX IF NOT EXISTS idx_gyan_points_total ON gyan_points(total_points DESC);

-- ============================================
-- 12. GYAN POINTS TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS gyan_points_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL, -- References main DB users(id)
  points_change INTEGER NOT NULL, -- Positive for earning, negative for spending
  transaction_type VARCHAR(50) NOT NULL, -- 'competition_win', 'course_purchase', 'reward', etc.
  reference_id UUID, -- competition_id, course_id, etc.
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gyan_points_transactions_user ON gyan_points_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_gyan_points_transactions_type ON gyan_points_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_gyan_points_transactions_created ON gyan_points_transactions(created_at DESC);

-- ============================================
-- ENABLE ROW LEVEL SECURITY
-- ============================================
ALTER TABLE communities ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_replies ENABLE ROW LEVEL SECURITY;
ALTER TABLE reply_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE competition_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE competition_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE competition_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE gyan_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE gyan_points_transactions ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS POLICIES (Permissive for development)
-- ============================================
CREATE POLICY "Allow all operations" ON communities FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON community_members FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON community_posts FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON post_likes FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON post_replies FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON reply_likes FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON competitions FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON competition_questions FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON competition_registrations FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON competition_submissions FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON gyan_points FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON gyan_points_transactions FOR ALL USING (true);

-- ============================================
-- DONE! Schema is ready
-- ============================================
