export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;  // ISO string format
}

export interface DiaryEntry {
  user_id: string;
  content: string;
  timestamp: string;  // ISO string format
}

export interface ChatResponse {
  response: string;
  context: {
    mood?: string;
    recent_activities?: string[];
    favorite_genres?: string[];
    watched_movies?: string[];
    stress_level?: number;
    goals?: string[];
    recommended_genres?: string[];
  };
}