import api from './api';

export interface Video {
    id: string;
    title: string;
    description: string;
    domain: string;
    source_language: string;
    target_languages: string[];
    status: string;
    file_url: string;
    content_type?: string;  // 'video', 'audio', 'document'
    thumbnail_url?: string;
    duration?: number;
    uploaded_by: string;
    created_at: string;
}

export interface VideoListResponse {
    videos: Video[];
    total: number;
    page: number;
    page_size: number;
}

export interface VideoUploadData {
    title: string;
    description?: string;
    domain: string;
    source_language: string;
    target_languages: string;
    course_id: string;
}

// Upload video with progress tracking
export const uploadVideo = async (
    file: File,
    data: VideoUploadData,
    onProgress?: (progress: number) => void
): Promise<Video> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', data.title);
    if (data.description) formData.append('description', data.description);
    formData.append('domain', data.domain);
    formData.append('source_language', data.source_language);
    formData.append('target_languages', data.target_languages);
    formData.append('course_id', data.course_id);

    const response = await api.post<Video>('/videos/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            if (onProgress && progressEvent.total) {
                const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                onProgress(progress);
            }
        },
    });

    return response.data;
};

// Get tutor's uploaded videos
export const getMyVideos = async (page: number = 1, pageSize: number = 20): Promise<VideoListResponse> => {
    const response = await api.get<VideoListResponse>(`/videos/my-videos?page=${page}&page_size=${pageSize}`);
    return response.data;
};

// Get all videos (public)
export const getAllVideos = async (page: number = 1, pageSize: number = 20): Promise<VideoListResponse> => {
    const response = await api.get<VideoListResponse>(`/videos/?page=${page}&page_size=${pageSize}`);
    return response.data;
};

// Delete video
export const deleteVideo = async (videoId: string): Promise<void> => {
    await api.delete(`/videos/${videoId}`);
};

// Get video details
export const getVideoDetails = async (videoId: string): Promise<Video> => {
    const response = await api.get<Video>(`/videos/${videoId}`);
    return response.data;
};

// Enroll in a course
export const enrollInCourse = async (videoId: string): Promise<{ message: string; enrolled: boolean }> => {
    const response = await api.post(`/videos/${videoId}/enroll`);
    return response.data;
};

// Get enrolled videos
export const getEnrolledVideos = async (page: number = 1, pageSize: number = 20): Promise<VideoListResponse> => {
    const response = await api.get<VideoListResponse>(`/videos/?page=${page}&page_size=${pageSize}&enrolled=true`);
    return response.data;
};

