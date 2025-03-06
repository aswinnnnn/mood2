import { DiaryEntry, ChatResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export async function sendMessage(
  content: string, 
  timestamp: string,
  userId: string
): Promise<{ role: 'assistant', content: string, timestamp: string }> {
  const token = localStorage.getItem('token');
  
  const entry: DiaryEntry = {
    user_id: userId,
    content: content,
    timestamp: timestamp
  };

  try {
    const response = await fetch(`${API_BASE_URL}/diary-entry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(entry),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data: ChatResponse = await response.json();
    return {
      role: 'assistant',
      content: data.response,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}

export async function getUserContext(userId: string) {
  const token = localStorage.getItem('token');
  try {
    const response = await fetch(`${API_BASE_URL}/user-context/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching user context:', error);
    throw error;
  }
}

export async function getConversationHistory(userId: string) {
  const token = localStorage.getItem('token');
  try {
    const response = await fetch(`${API_BASE_URL}/conversation-history/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching conversation history:', error);
    throw error;
  }
}