import api from './api';

export interface Doubt {
    id: string;
    user_id: string;
    video_id: string;
    question: string;
    lecture_number: number;
    subject: string;
    status: 'pending' | 'answered';
    created_at: string;
    student_name: string;
    course_name: string;
    answer?: string;
    answered_at?: string;
}

export const getTeacherDoubts = async () => {
    const response = await api.get('/doubts/teacher');
    return response.data;
};

export const answerDoubt = async (doubtId: string, answer: string) => {
    const response = await api.post(`/doubts/${doubtId}/answer`, { answer });
    return response.data;
};

export interface DoubtCreateData {
    video_id: string;
    question: string;
    lecture_number?: number;
    subject?: string;
}

// Get student's own doubts
export const getStudentDoubts = async (): Promise<Doubt[]> => {
    const response = await api.get<Doubt[]>('/doubts/');
    return response.data;
};

// Create a new doubt
export const createDoubt = async (data: DoubtCreateData): Promise<Doubt> => {
    const response = await api.post<Doubt>('/doubts/', data);
    return response.data;
};
