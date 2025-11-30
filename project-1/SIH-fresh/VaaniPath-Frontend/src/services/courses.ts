import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Get auth token from localStorage
const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
};

export interface Course {
    id: string;
    title: string;
    description?: string;
    thumbnail_url?: string;
    teacher_id: string;
    teacher_name?: string;
    domain: string;
    source_language: string;
    target_languages: string[];
    created_at: string;
    updated_at?: string;
    total_videos?: number;
    total_duration?: number;
}

export interface CourseCreate {
    title: string;
    description?: string;
    thumbnail_url?: string;
    domain: string;
    source_language: string;
    target_languages: string[];
}

export interface CourseUpdate {
    title?: string;
    description?: string;
    thumbnail_url?: string;
    domain?: string;
    source_language?: string;
    target_languages?: string[];
}

export interface CourseWithVideos extends Course {
    videos: any[];  // Will use Video type from videos service
}

// Create a new course
export const createCourse = async (data: CourseCreate): Promise<Course> => {
    const response = await axios.post(`${API_URL}/courses`, data, {
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Get all courses (public)
export const getAllCourses = async (params?: {
    page?: number;
    page_size?: number;
    domain?: string;
    language?: string;
    search?: string;
}): Promise<{ courses: Course[]; total: number; page: number; page_size: number }> => {
    const response = await axios.get(`${API_URL}/courses`, {
        params,
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Get teacher's courses
export const getMyCourses = async (params?: {
    page?: number;
    page_size?: number;
}): Promise<{ courses: Course[]; total: number; page: number; page_size: number }> => {
    const response = await axios.get(`${API_URL}/courses/my`, {
        params,
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Get course by ID
export const getCourseById = async (id: string): Promise<CourseWithVideos> => {
    const response = await axios.get(`${API_URL}/courses/${id}`, {
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Update course
export const updateCourse = async (id: string, data: CourseUpdate): Promise<Course> => {
    const response = await axios.put(`${API_URL}/courses/${id}`, data, {
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Delete course
export const deleteCourse = async (id: string): Promise<void> => {
    await axios.delete(`${API_URL}/courses/${id}`, {
        headers: getAuthHeaders(),
    });
};

// Get course videos
export const getCourseVideos = async (id: string): Promise<any[]> => {
    const response = await axios.get(`${API_URL}/courses/${id}/videos`, {
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Upload thumbnail for course
export const uploadCourseThumbnail = async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);

    // Using existing cloudinary upload endpoint
    const response = await axios.post(`${API_URL}/videos/upload-thumbnail`, formData, {
        headers: {
            ...getAuthHeaders(),
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data.thumbnail_url;
};

// Get teacher stats
export const getTeacherStats = async (): Promise<{ totalVideos: number; totalStudents: number; totalViews: number }> => {
    const response = await axios.get(`${API_URL}/courses/stats/overview`, {
        headers: getAuthHeaders(),
    });
    return response.data;
};
