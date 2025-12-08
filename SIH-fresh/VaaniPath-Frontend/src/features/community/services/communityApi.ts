/**
 * Community API Service
 */
import api from '@/services/api';
import type {
  Community,
  CommunityCreate,
  Post,
  PostCreate,
  Reply,
  ReplyCreate,
  Competition,
  CompetitionCreate,
  QuestionCreate,
  LeaderboardEntry
} from '../types';

// Communities
export const getCommunities = async (params?: {
  page?: number;
  page_size?: number;
  domain?: string;
}): Promise<{ communities: Community[]; total: number; page: number; page_size: number }> => {
  const response = await api.get('/community/communities', { params });
  return response.data;
};

export const getCommunity = async (id: string): Promise<Community> => {
  const response = await api.get(`/community/communities/${id}`);
  return response.data;
};

export const createCommunity = async (data: CommunityCreate): Promise<Community> => {
  const response = await api.post('/community/communities', data);
  return response.data;
};

export const joinCommunity = async (id: string): Promise<{ message: string }> => {
  const response = await api.post(`/community/communities/${id}/join`);
  return response.data;
};

export const leaveCommunity = async (id: string): Promise<{ message: string }> => {
  const response = await api.post(`/community/communities/${id}/leave`);
  return response.data;
};

// Posts
export const getPosts = async (params: {
  community_id: string;
  page?: number;
  page_size?: number;
}): Promise<{ posts: Post[]; total: number; page: number; page_size: number }> => {
  const response = await api.get('/community/posts', { params });
  return response.data;
};

export const uploadPostMedia = async (file: File): Promise<{ url: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/community/posts/upload-media', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const createPost = async (data: PostCreate): Promise<Post> => {
  const response = await api.post('/community/posts', data);
  return response.data;
};

export const toggleLike = async (postId: string): Promise<{ message: string; liked: boolean; likes_count: number }> => {
  const response = await api.post(`/community/posts/${postId}/like`);
  return response.data;
};

export const createReply = async (postId: string, data: Omit<ReplyCreate, 'post_id'>): Promise<Reply> => {
  const response = await api.post(`/community/posts/${postId}/reply`, { ...data, post_id: postId });
  return response.data;
};

export const getReplies = async (postId: string): Promise<{ replies: Reply[]; total: number }> => {
  const response = await api.get(`/community/posts/${postId}/replies`);
  return response.data;
};

// Competitions
export const createCompetition = async (data: CompetitionCreate): Promise<Competition> => {
  const response = await api.post('/community/competitions', data);
  return response.data;
};

export const addQuestions = async (competitionId: string, questions: QuestionCreate[]): Promise<any> => {
  const response = await api.post(`/community/competitions/${competitionId}/questions`, questions);
  return response.data;
};

export const registerForCompetition = async (competitionId: string): Promise<{ message: string }> => {
  const response = await api.post(`/community/competitions/${competitionId}/register`);
  return response.data;
};

export const getCompetitions = async (communityId: string): Promise<Competition[]> => {
  const response = await api.get(`/community/competitions/by-community/${communityId}`);
  return response.data;
};

export const submitAnswer = async (competitionId: string, data: {
  question_id: string;
  selected_answer: string;
}): Promise<any> => {
  const response = await api.post(`/community/competitions/${competitionId}/submit`, {
    ...data,
    competition_id: competitionId
  });
  return response.data;
};

export const getLeaderboard = async (competitionId: string): Promise<{ entries: LeaderboardEntry[]; total_participants: number }> => {
  const response = await api.get(`/community/competitions/${competitionId}/leaderboard`);
  return response.data;
};

export const getGyanPoints = async () => {
    const response = await api.get<{ total_points: number }>('/community/gyan-points/me');
    return response.data;
};

export const getGyanPointsHistory = async () => {
    const response = await api.get<any[]>('/community/gyan-points/history');
    return response.data;
};

export const getCompetition = async (id: string): Promise<Competition> => {
    const response = await api.get(`/community/competitions/${id}`);
    return response.data;
};
