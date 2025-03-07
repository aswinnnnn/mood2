import { DiaryEntry, ChatResponse } from '../types';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
});

// Add request interceptor
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
    }
);

export async function sendMessage(
  content: string, 
  timestamp: string,
  userId: string
): Promise<{ role: 'assistant', content: string, timestamp: string }> {
  const entry: DiaryEntry = {
    user_id: userId,
    content: content,
    timestamp: timestamp
  };

  try {
    const response = await api.post('/diary-entry', entry);
    return {
      role: 'assistant',
      content: response.data.response,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}

export async function getUserContext(userId: string) {
  try {
    const response = await api.get(`/user-context/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user context:', error);
    throw error;
  }
}

export async function getConversationHistory(userId: string) {
  try {
    const response = await api.get(`/conversation-history/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching conversation history:', error);
    throw error;
  }
}

export const getUserPreferences = async (userId: string) => {
    try {
        const response = await api.get(`/preferences/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching preferences:', error);
        throw error;
    }
};

export const updateUserPreferences = async (userId: string, preferences: any) => {
    try {
        const response = await api.put(`/preferences/${userId}`, preferences);
        return response.data;
    } catch (error) {
        console.error('Error updating preferences:', error);
        throw error;
    }
};

export async function registerUserWithPreferences(userData: any, preferences: any) {
  const response = await api.post('/api/auth/register', {
    user: userData,
    preferences: {
      ...preferences,
      name: userData.name  // Ensure name is included in preferences
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}