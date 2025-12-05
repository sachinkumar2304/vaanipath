import api from './api';

export interface DubbedContentResponse {
    video_id: string;
    language: string;
    content_type: 'video' | 'audio' | 'document';
    content_url?: string;
    status: 'completed' | 'processing' | 'failed' | 'pending';
    cached: boolean;
    message: string;
}

export interface DubbingStatusResponse {
    status: 'completed' | 'processing' | 'failed' | 'not_started' | 'pending';
    progress: number;
    content_url?: string;
    error?: string;
    message: string;
}

export interface LanguageAvailability {
    code: string;
    available: boolean;
    status: 'original' | 'completed' | 'not_generated';
}

export interface AvailableLanguagesResponse {
    video_id: string;
    languages: LanguageAvailability[];
}

export interface ProgressResponse {
    progress: number;
    completed: boolean;
}

// Get dubbed content (triggers dubbing if not cached)
export const getDubbedContent = async (
    videoId: string,
    language: string
): Promise<DubbedContentResponse> => {
    const response = await api.get<DubbedContentResponse>(
        `/processing/content/${videoId}/${language}`
    );
    return response.data;
};

// Check dubbing status (for polling)
export const checkDubbingStatus = async (
    videoId: string,
    language: string
): Promise<DubbingStatusResponse> => {
    const response = await api.get<DubbingStatusResponse>(
        `/processing/content/${videoId}/${language}/status`
    );
    return response.data;
};

// Get available languages for a video
export const getAvailableLanguages = async (
    videoId: string
): Promise<AvailableLanguagesResponse> => {
    const response = await api.get<AvailableLanguagesResponse>(
        `/processing/content/${videoId}/available-languages`
    );
    return response.data;
};

// Update watch progress
export const updateProgress = async (
    videoId: string,
    progress: number
): Promise<void> => {
    await api.patch(`/videos/${videoId}/progress`, { progress_percentage: progress });
};

// Get current progress
export const getProgress = async (videoId: string): Promise<ProgressResponse> => {
    const response = await api.get<ProgressResponse>(`/videos/${videoId}/progress`);
    return response.data;
};

// Get quiz for video
export const getVideoQuiz = async (videoId: string): Promise<any> => {
    const response = await api.get(`/quiz/video/${videoId}/questions`);
    return response.data;
};

// Submit quiz
export const submitQuiz = async (videoId: string, answers: any): Promise<any> => {
    const response = await api.post(`/quiz/video/${videoId}/submit`, { answers });
    return response.data;
};

// Cancel dubbing
export const cancelDubbing = async (videoId: string, language: string): Promise<void> => {
    await api.delete(`/processing/content/${videoId}/${language}`);
};
