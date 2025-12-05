import api from './api';

export interface TeacherStats {
    total_videos: number;
    total_students: number;
    total_views: number;
}

// Get teacher dashboard stats
export const getTeacherStats = async (): Promise<TeacherStats> => {
    const response = await api.get<TeacherStats>('/teacher/stats');
    return response.data;
};
