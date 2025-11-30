import api from './api';

export interface Question {
    question: string;
    options: string[];
    correctAnswer: number;
    points: number;
}

export interface QuizCreateData {
    courseId: string;
    title: string;
    description: string;
    questions: Question[];
}

export interface Quiz {
    id: string;
    title: string;
    question_count: number;
    created_at: string;
}

export const createQuiz = async (data: QuizCreateData) => {
    const response = await api.post('/quiz/create', data);
    return response.data;
};

export const getTeacherQuizzes = async () => {
    const response = await api.get('/quiz/teacher/list');
    return response.data;
};
