import axios from 'axios';
import { AuthResponse, UserData } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const authenticateUser = async (username: string, password: string): Promise<AuthResponse> => {
    console.log('Attempting to authenticate with:', { username });
    try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
            username,
            password,
        });
        console.log('Authentication response:', response.data);
        return response.data;
    } catch (error: any) {
        console.error('Login error:', error.response?.data || error.message);
        throw new Error(error.response?.data?.detail || 'Authentication failed');
    }
};

export const login = (authData: AuthResponse) => {
    console.log('Storing auth data:', authData);
    localStorage.setItem('token', authData.access_token);
    localStorage.setItem('user_id', authData.user_id);
};

export const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
};

export const registerUser = async (userData: UserData): Promise<AuthResponse> => {
    console.log('Attempting to register user with:', userData);
    try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
            user: userData,
            preferences: {}  // Empty preferences for initial registration
        });
        console.log('Registration response:', response.data);
        return response.data;
    } catch (error: any) {
        console.error('Registration error:', error.response?.data || error.message);
        throw new Error(error.response?.data?.detail || 'Registration failed');
    }
};

export const registerUserWithPreferences = async (
    userData: UserData,
    preferences: any
): Promise<AuthResponse> => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
            user: userData,
            preferences: preferences
        });
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.detail || 'Registration failed');
    }
};

// Helper function to get the auth token
export const getAuthToken = (): string | null => {
    return localStorage.getItem('token');
}; 