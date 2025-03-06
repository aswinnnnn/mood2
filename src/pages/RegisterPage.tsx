import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../utils/auth';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    name: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    const { confirmPassword, ...registrationData } = formData;
    try {
      const result = await registerUser(registrationData);
      if (result.success) {
        navigate('/'); // Redirect to login after successful registration
      } else {
        setError(result.error || 'Registration failed');
      }
    } catch (error) {
      setError('Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50 flex items-center justify-center">
      <div className="w-full max-w-md p-6">
        <h1 className="text-3xl font-bold text-center text-purple-600 mb-8">Create Account</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="text-red-500">{error}</div>}
          {['email', 'username', 'name', 'password', 'confirmPassword'].map((field) => (
            <input
              key={field}
              type={field.includes('password') ? 'password' : field === 'email' ? 'email' : 'text'}
              placeholder={field.charAt(0).toUpperCase() + field.slice(1).replace(/([A-Z])/g, ' $1')}
              value={formData[field as keyof typeof formData]}
              onChange={e => setFormData({...formData, [field]: e.target.value})}
              className="w-full p-2 border rounded"
              required
            />
          ))}
          <button type="submit" className="w-full bg-purple-600 text-white p-2 rounded">
            Register
          </button>
          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="text-purple-600 hover:text-purple-800"
            >
              Already have an account? Sign In
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 