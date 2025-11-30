import api from './api';

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface SignupData {
    email: string;
    password: string;
    full_name: string;
    is_admin?: boolean;
}

export interface User {
    id: string;
    email: string;
    full_name: string;
    is_admin: boolean;
    is_teacher: boolean;
    created_at: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

// Login
export const login = async (credentials: LoginCredentials): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/login', credentials);
    return response.data;
};

// Signup (students only)
export const signup = async (userData: SignupData): Promise<User> => {
    const response = await api.post<User>('/auth/signup', userData);
    return response.data;
};

// Get current user
export const getCurrentUser = async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
};

// Logout
export const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
};
