import api from './api';

export interface TutorCreate {
    email: string;
    password: string;
    full_name: string;
}

export interface TutorResponse {
    id: string;
    email: string;
    full_name: string;
    is_teacher: boolean;
    created_at: string;
    temporary_password: string;
}

export interface Tutor {
    id: string;
    email: string;
    full_name: string;
    created_at: string;
}

export interface Student {
    id: string;
    email: string;
    full_name: string;
    created_at: string;
}

export interface AdminStats {
    total_videos: number;
    total_users: number;
    total_students: number;
    total_teachers: number;
    videos_by_status: {
        completed: number;
        processing: number;
        failed: number;
        pending: number;
    };
}

// Create tutor
export const createTutor = async (tutorData: TutorCreate): Promise<TutorResponse> => {
    const response = await api.post<TutorResponse>('/admin/create-tutor', tutorData);
    return response.data;
};

// List all tutors
export const listTutors = async (): Promise<{ tutors: Tutor[]; total: number }> => {
    const response = await api.get('/admin/tutors');
    return response.data;
};

// List all students
export const listStudents = async (): Promise<{ students: Student[]; total: number }> => {
    const response = await api.get('/admin/students');
    return response.data;
};

// Get admin stats
export const getAdminStats = async (): Promise<AdminStats> => {
    const response = await api.get<AdminStats>('/admin/stats');
    return response.data;
};

// Toggle teacher status
export const toggleTeacherStatus = async (userId: string, isTeacher: boolean) => {
    const response = await api.patch(`/admin/users/${userId}/teacher`, null, {
        params: { is_teacher: isTeacher }
    });
    return response.data;
};

// Delete tutor
export const deleteTutor = async (tutorId: string): Promise<{ message: string; tutor_email: string; tutor_name: string; deleted_resources: { courses: number; videos: number } }> => {
    const response = await api.delete(`/admin/tutors/${tutorId}`);
    return response.data;
};

// Delete course (admin can delete any course)
export const deleteCourse = async (courseId: string): Promise<void> => {
    await api.delete(`/courses/${courseId}`);
};
