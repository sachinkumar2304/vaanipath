/**
 * Community Feature Types
 */

export interface Community {
  id: string;
  name: string;
  domain: string;
  description?: string;
  thumbnail_url?: string;
  created_by: string;
  member_count: number;
  post_count: number;
  created_at: string;
  updated_at: string;
  is_member?: boolean;
  user_role?: string;
}

export interface CommunityCreate {
  name: string;
  domain: string;
  description?: string;
  thumbnail_url?: string;
}

export interface Post {
  id: string;
  community_id: string;
  user_id: string;
  content: string;
  media_urls?: string[];
  post_type: string;
  course_id?: string;
  is_pinned: boolean;
  likes_count: number;
  replies_count: number;
  created_at: string;
  updated_at: string;
  user_name?: string;
  user_email?: string;
  is_liked_by_user?: boolean;
}

export interface PostCreate {
  community_id: string;
  content: string;
  media_urls?: string[];
  post_type?: string;
  course_id?: string;
}

export interface Reply {
  id: string;
  post_id: string;
  user_id: string;
  parent_reply_id?: string;
  content: string;
  likes_count: number;
  created_at: string;
  updated_at: string;
  user_name?: string;
  user_email?: string;
  is_liked_by_user?: boolean;
}

export interface ReplyCreate {
  post_id: string;
  content: string;
  parent_reply_id?: string;
}

export interface Competition {
  id: string;
  community_id: string;
  created_by: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  status: string;
  max_participants?: number;
  participants_count: number;
  total_questions: number;
  points_first: number;
  points_second: number;
  points_third: number;
  points_top10: number;
  created_at: string;
  updated_at: string;
  is_registered?: boolean;
  user_score?: number;
  difficulty: "normal" | "hard";
}

export interface CompetitionCreate {
  community_id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  difficulty: "normal" | "hard";
  max_participants?: number;
  points_first?: number;
  points_second?: number;
  points_third?: number;
  points_top10?: number;
}

export interface QuestionOption {
  id: string;
  text: string;
}

export interface Question {
  id: string;
  competition_id: string;
  question_text: string;
  options: QuestionOption[];
  correct_answer: string;
  points: number;
  question_order: number;
  created_at: string;
}

export interface QuestionCreate {
  competition_id: string;
  question_text: string;
  options: QuestionOption[];
  correct_answer: string;
  points?: number;
  question_order: number;
}

export interface LeaderboardEntry {
  user_id: string;
  user_name: string;
  user_email: string;
  total_score: number;
  correct_answers: number;
  total_answers: number;
  rank: number;
}
