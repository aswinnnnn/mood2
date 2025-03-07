import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser, registerUserWithPreferences } from '../utils/auth';
import { login } from '../utils/auth';
import { useAuth } from '../context/AuthContext';
import BasicInfoForm from '../components/BasicInfoForm';
import PreferencesSetup from '../components/PreferencesSetup';

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [userData, setUserData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [registrationToken, setRegistrationToken] = useState('');

  useEffect(() => {
    console.log('Register page mounted');
  }, []);

  const handleBasicInfoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    console.log('Submitting basic info:', userData);

    try {
      if (userData.password !== userData.confirmPassword) {
        throw new Error('Passwords do not match');
      }

      const { confirmPassword, ...registrationData } = userData;
      const result = await registerUser(registrationData);
      console.log('Registration result:', result);
      
      if (result.access_token) {
        localStorage.setItem('token', result.access_token);
        setRegistrationToken(result.access_token);
        setUser({ id: result.user_id });
        setStep(2);
      } else {
        setError('Registration failed');
      }
    } catch (error: any) {
      console.error('Registration error:', error);
      setError(error.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegistrationComplete = async (preferences: any) => {
    try {
      // Navigate directly to home page after preferences are set
      navigate('/');
    } catch (error: any) {
      setError(error.message || 'Failed to save preferences');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50 flex items-center justify-center">
      <div className="w-full max-w-md p-6">
        <h1 className="text-3xl font-bold text-center text-purple-600 mb-8">
          {step === 1 ? 'Create Account' : 'Set Your Preferences'}
        </h1>
        {error && <div className="text-red-500 mb-4">{error}</div>}
        {step === 1 ? (
          <BasicInfoForm 
            userData={userData} 
            setUserData={setUserData} 
            onSubmit={handleBasicInfoSubmit} 
          />
        ) : (
          <PreferencesSetup 
            userData={userData}
            onComplete={handleRegistrationComplete} 
          />
        )}
        <div className="text-center mt-4">
          <button
            type="button"
            onClick={() => navigate('/login')}
            className="text-purple-600 hover:text-purple-800"
          >
            Already have an account? Sign In
          </button>
        </div>
      </div>
    </div>
  );
} 