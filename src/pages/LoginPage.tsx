import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authenticateUser, login } from '../utils/auth';
import { useAuth } from '../context/AuthContext';
import { Sparkles } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    console.log('Attempting login with:', credentials.username);

    try {
      const response = await authenticateUser(credentials.username, credentials.password);
      console.log('Login response:', response);
      
      if (response && response.access_token) {
        login(response);
        setUser({ id: response.user_id });
        navigate('/journal');
      } else {
        setError('Invalid login response');
      }
    } catch (error: any) {
      console.error('Login error:', error);
      setError(error.message || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50 flex items-center justify-center">
      <div className="w-full max-w-md p-6">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Sparkles className="w-12 h-12 text-purple-600" />
          </div>
          <h1 className="text-3xl font-bold text-purple-600">Welcome to MoodScribe</h1>
          <p className="text-gray-600 mt-2">Your personal emotional support companion</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="text-red-500">{error}</div>}
          <div>
            <label className="block mb-2">Username</label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block mb-2">Password</label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-purple-600 text-white p-2 rounded hover:bg-purple-700"
          >
            Sign In
          </button>
          
          <div className="text-center mt-4">
            <button
              type="button"
              onClick={() => navigate('/register')}
              className="text-purple-600 hover:text-purple-800"
            >
              Don't have an account? Sign Up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 