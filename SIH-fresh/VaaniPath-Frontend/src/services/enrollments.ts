import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// Get auth token from localStorage
const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
};

export interface Enrollment {
    id: string;
    student_id: string;
    course_id: string;
    enrolled_at: string;
    progress?: Record<string, VideoProgress>;
    course_title?: string;
    course_thumbnail?: string;
    total_videos?: number;
    completed_videos?: number;
    progress_percentage?: number;
}

export interface VideoProgress {
    completed: boolean;
    watched_duration: number;
    last_watched_at?: string;
}

export interface EnrollmentProgressUpdate {
    video_id: string;
    completed: boolean;
    watched_duration: number;
}

// Enroll in a course
export const enrollInCourse = async (courseId: string): Promise<Enrollment> => {
    const response = await axios.post(`${API_URL}/enrollments/${courseId}`, {}, {
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Get my enrollments
export const getMyEnrollments = async (): Promise<{ enrollments: Enrollment[]; total: number }> => {
    const response = await axios.get(`${API_URL}/enrollments/my`, {
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Get course progress
export const getCourseProgress = async (courseId: string): Promise<Enrollment> => {
    const response = await axios.get(`${API_URL}/enrollments/${courseId}/progress`, {
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Update video progress
export const updateVideoProgress = async (
    courseId: string,
    data: EnrollmentProgressUpdate
): Promise<Enrollment> => {
    const response = await axios.put(`${API_URL}/enrollments/${courseId}/progress`, data, {
        headers: getAuthHeaders(),
    });
    return response.data;
};

// Unenroll from course
export const unenrollFromCourse = async (courseId: string): Promise<void> => {
    await axios.delete(`${API_URL}/enrollments/${courseId}`, {
        headers: getAuthHeaders(),
    });
};

// Check if enrolled in a course
export const isEnrolledInCourse = async (courseId: string): Promise<boolean> => {
    try {
        await getCourseProgress(courseId);
        return true;
    } catch (error) {
        return false;
    }
};
