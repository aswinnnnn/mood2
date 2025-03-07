import React from 'react';

interface BasicInfoFormProps {
  userData: {
    username: string;
    email: string;
    password: string;
    name: string;
    confirmPassword: string;
  };
  setUserData: (data: any) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export default function BasicInfoForm({ userData, setUserData, onSubmit }: BasicInfoFormProps) {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label className="block mb-2">Username</label>
        <input
          type="text"
          value={userData.username}
          onChange={(e) => setUserData({ ...userData, username: e.target.value })}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <div>
        <label className="block mb-2">Email</label>
        <input
          type="email"
          value={userData.email}
          onChange={(e) => setUserData({ ...userData, email: e.target.value })}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <div>
        <label className="block mb-2">Full Name</label>
        <input
          type="text"
          value={userData.name}
          onChange={(e) => setUserData({ ...userData, name: e.target.value })}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <div>
        <label className="block mb-2">Password</label>
        <input
          type="password"
          value={userData.password}
          onChange={(e) => setUserData({ ...userData, password: e.target.value })}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <div>
        <label className="block mb-2">Confirm Password</label>
        <input
          type="password"
          value={userData.confirmPassword}
          onChange={(e) => setUserData({ ...userData, confirmPassword: e.target.value })}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <button
        type="submit"
        className="w-full bg-purple-600 text-white p-2 rounded hover:bg-purple-700"
      >
        Continue
      </button>
    </form>
  );
} 