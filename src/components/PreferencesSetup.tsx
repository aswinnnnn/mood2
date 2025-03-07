import React, { useState } from 'react';

interface PreferencesSetupProps {
  userData: any;
  onComplete: (preferences: any) => void;
}

export default function PreferencesSetup({ userData, onComplete }: PreferencesSetupProps) {
  const [preferences, setPreferences] = useState({
    location: '',
    hobbies: [],
    likes: [],
    dislikes: [],
    favorite_genres: [],
    activity_level: 'medium',
    preferred_meditation_time: 15,
    preferred_notification_time: '09:00'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onComplete(preferences);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Personalize Your Experience</h2>
      <p className="mb-4">Help us understand you better to provide personalized support</p>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Add your preference fields here */}
        <div>
          <label className="block mb-2">What are your interests?</label>
          <input
            type="text"
            placeholder="Enter interests separated by commas"
            onChange={(e) => setPreferences({
              ...preferences,
              likes: e.target.value.split(',').map(item => item.trim())
            })}
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block mb-2">Favorite Movie/TV Genres</label>
          <select
            multiple
            onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions).map(opt => opt.value);
              setPreferences({...preferences, favorite_genres: selected});
            }}
            className="w-full p-2 border rounded"
          >
            <option value="action">Action</option>
            <option value="comedy">Comedy</option>
            <option value="drama">Drama</option>
            <option value="scifi">Sci-Fi</option>
            <option value="documentary">Documentary</option>
          </select>
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Complete Registration
        </button>
      </form>
    </div>
  );
} 