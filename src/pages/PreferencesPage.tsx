import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getUserPreferences, updateUserPreferences } from '../services/api';

interface Preferences {
  location: string;
  hobbies: string[];
  likes: string[];
  dislikes: string[];
  favorite_genres: string[];
  activity_level: 'low' | 'medium' | 'high';
  preferred_meditation_time?: number;
  preferred_notification_time?: string;
}

export default function PreferencesPage() {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState<Preferences>({
    location: '',
    hobbies: [],
    likes: [],
    dislikes: [],
    favorite_genres: [],
    activity_level: 'medium'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadPreferences();
  }, [user]);

  const loadPreferences = async () => {
    if (!user) return;
    try {
      const data = await getUserPreferences(user.id);
      setPreferences(data);
    } catch (error) {
      console.error('Error loading preferences:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    try {
      await updateUserPreferences(user.id, preferences);
      setMessage('Preferences updated successfully!');
    } catch (error) {
      setMessage('Error updating preferences');
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">User Preferences</h1>
      {message && (
        <div className="mb-4 p-2 bg-blue-100 text-blue-700 rounded">
          {message}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-2">Location</label>
          <input
            type="text"
            value={preferences.location}
            onChange={(e) => setPreferences({...preferences, location: e.target.value})}
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block mb-2">Activity Level</label>
          <select
            value={preferences.activity_level}
            onChange={(e) => setPreferences({...preferences, activity_level: e.target.value as 'low' | 'medium' | 'high'})}
            className="w-full p-2 border rounded"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label className="block mb-2">Preferred Meditation Time (minutes)</label>
          <input
            type="number"
            value={preferences.preferred_meditation_time || ''}
            onChange={(e) => setPreferences({...preferences, preferred_meditation_time: parseInt(e.target.value)})}
            className="w-full p-2 border rounded"
          />
        </div>

        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Save Preferences
        </button>
      </form>
    </div>
  );
} 